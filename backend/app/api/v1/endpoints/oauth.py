"""Fix 15: Google and GitHub OAuth 2.0 via Authlib + SessionMiddleware.

Flow:
  1. GET /auth/oauth/{provider}       — redirect to provider consent screen
  2. GET /auth/oauth/{provider}/callback — exchange code, upsert user, set cookie

Requires env vars:
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
  GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
  APP_BASE_URL  (e.g. https://app.opsai.dev)
"""
from typing import Optional

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User

router = APIRouter()
oauth = OAuth()

_base = getattr(settings, 'APP_BASE_URL', 'http://localhost:8000')

# ── Register providers ───────────────────────────────────────────────────────────────────
if getattr(settings, 'GOOGLE_CLIENT_ID', None):
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

if getattr(settings, 'GITHUB_CLIENT_ID', None):
    oauth.register(
        name='github',
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email read:user'},
    )


# ── Helpers ─────────────────────────────────────────────────────────────────────

async def _upsert_oauth_user(
    db: AsyncSession,
    provider: str,
    oauth_id: str,
    email: str,
    full_name: Optional[str],
    avatar_url: Optional[str],
) -> User:
    result = await db.execute(select(User).where(User.oauth_provider == provider, User.oauth_id == oauth_id))
    user = result.scalar_one_or_none()

    if not user:
        # Check if an email-based account already exists; link it
        result2 = await db.execute(select(User).where(User.email == email))
        user = result2.scalar_one_or_none()

    if user:
        # Update OAuth fields on existing user
        user.oauth_provider = provider
        user.oauth_id = oauth_id
        if avatar_url:
            user.avatar_url = avatar_url
    else:
        user = User(
            email=email,
            hashed_password="",  # No password for OAuth users
            full_name=full_name or email.split('@')[0],
            is_active=True,
            is_verified=True,
            oauth_provider=provider,
            oauth_id=oauth_id,
            avatar_url=avatar_url,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user


def _set_cookie(response: Response, token: str) -> None:
    from app.api.v1.endpoints.auth import _set_auth_cookie
    _set_auth_cookie(response, token)


# ── Routes ──────────────────────────────────────────────────────────────────────

@router.get("/{provider}")
async def oauth_login(provider: str, request: Request):
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=400, detail=f"OAuth provider '{provider}' not configured.")
    redirect_uri = f"{_base}/api/v1/auth/oauth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=400, detail=f"OAuth provider '{provider}' not configured.")

    try:
        token = await client.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e.error}")

    # Extract user info per provider
    if provider == "google":
        user_info = token.get('userinfo') or await client.userinfo(token=token)
        email = user_info.get('email')
        full_name = user_info.get('name')
        oauth_id = user_info.get('sub')
        avatar_url = user_info.get('picture')
    elif provider == "github":
        resp = await client.get('user', token=token)
        user_info = resp.json()
        oauth_id = str(user_info.get('id'))
        full_name = user_info.get('name') or user_info.get('login')
        avatar_url = user_info.get('avatar_url')
        # GitHub may not expose email in profile; fetch primary email
        email = user_info.get('email')
        if not email:
            emails_resp = await client.get('user/emails', token=token)
            emails = emails_resp.json()
            primary = next((e for e in emails if e.get('primary') and e.get('verified')), None)
            email = primary['email'] if primary else None
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider.")

    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from OAuth provider.")

    user = await _upsert_oauth_user(db, provider, oauth_id, email, full_name, avatar_url)
    jwt_token = create_access_token({"sub": str(user.id), "email": user.email})
    _set_cookie(response, jwt_token)

    frontend_url = getattr(settings, 'ALLOWED_ORIGINS', ['http://localhost:3000'])[0]
    from starlette.responses import RedirectResponse
    return RedirectResponse(url=f"{frontend_url}/dashboard")

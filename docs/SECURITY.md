# OpsAI Security Guide

## Security Principles

### Authentication
- JWT tokens with 24-hour expiry
- Passwords hashed with bcrypt (cost factor 12)
- No plaintext credentials stored anywhere

### Webhook Security
- All GitHub webhooks verified via HMAC-SHA256 signature
- Per-project webhook secrets (randomly generated 64-char hex)
- Constant-time comparison to prevent timing attacks

### API Security
- CORS restricted to configured origins only
- Rate limiting recommended via nginx or API gateway
- All DB queries use parameterized statements (SQLAlchemy ORM)

### Infrastructure
- Non-root Docker containers
- Secrets via environment variables only (never in code)
- Database not exposed to public internet

## Vulnerability Checklist

- [x] SQL Injection: ORM with parameterized queries
- [x] XSS: Next.js auto-escaping + CSP headers
- [x] CSRF: JWT-based auth (stateless)
- [x] Secrets: .env excluded from git
- [x] Webhook spoofing: HMAC signature verification
- [x] Dependency CVEs: Automated Dependabot alerts

## Production Recommendations

1. Enable HTTPS via Let's Encrypt
2. Set `DEBUG=false` in production
3. Use strong `APP_SECRET_KEY` (`openssl rand -hex 32`)
4. Enable PostgreSQL SSL connections
5. Rotate webhook secrets periodically
6. Monitor with Sentry or similar error tracking

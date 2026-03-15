'use client';
import { Sidebar } from '@/components/layout/Sidebar';
import { Users, UserPlus, Crown, Shield, Eye } from 'lucide-react';

const roleIcons: Record<string, any> = {
  owner: Crown,
  admin: Shield,
  viewer: Eye,
};

const roleColors: Record<string, string> = {
  owner: 'text-yellow-400',
  admin: 'text-blue-400',
  viewer: 'text-gray-400',
};

const mockMembers = [
  { id: '1', email: 'ossama@samotech.dev', name: 'Ossama Hashim', role: 'owner', joined: '2026-03-01' },
  { id: '2', email: 'dev@example.com', name: 'Team Dev', role: 'admin', joined: '2026-03-10' },
  { id: '3', email: 'viewer@example.com', name: 'Stakeholder', role: 'viewer', joined: '2026-03-12' },
];

export default function TeamPage() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-3xl mx-auto">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">👥 Team</h1>
              <p className="text-gray-400 mt-1">Manage members and permissions</p>
            </div>
            <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors">
              <UserPlus size={16} /> Invite Member
            </button>
          </div>

          <div className="card">
            <div className="space-y-3">
              {mockMembers.map((member) => {
                const RoleIcon = roleIcons[member.role];
                return (
                  <div key={member.id} className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
                        {member.name[0]}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{member.name}</p>
                        <p className="text-xs text-gray-500">{member.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <RoleIcon size={14} className={roleColors[member.role]} />
                      <span className={`text-xs font-medium capitalize ${roleColors[member.role]}`}>
                        {member.role}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* OAuth login notice */}
          <div className="card mt-6 border-blue-800/50">
            <h3 className="text-sm font-semibold text-white mb-2">🔐 SSO Login Options</h3>
            <p className="text-xs text-gray-400 mb-3">Team members can sign in with:</p>
            <div className="flex gap-3">
              <button className="flex items-center gap-2 bg-white text-gray-900 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors">
                <svg width="16" height="16" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
                Sign in with Google
              </button>
              <button className="flex items-center gap-2 bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors border border-gray-700">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
                Sign in with GitHub
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

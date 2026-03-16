'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  ActivityIcon,
  BarChart2Icon,
  CreditCardIcon,
  KeyIcon,
  LayoutDashboardIcon,
  LogOutIcon,
  ServerIcon,
  SettingsIcon,
} from 'lucide-react';
import { api } from '@/lib/api';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboardIcon },
  { href: '/projects', label: 'Projects', icon: ServerIcon },
  { href: '/runs', label: 'Pipeline Runs', icon: ActivityIcon },
  { href: '/analytics', label: 'Analytics', icon: BarChart2Icon },
  { href: '/api-keys', label: 'API Keys', icon: KeyIcon },
  { href: '/billing', label: 'Billing', icon: CreditCardIcon },
  { href: '/settings', label: 'Settings', icon: SettingsIcon },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
    } catch {
      // ignore — clear client-side state regardless
    } finally {
      router.push('/login');
    }
  };

  return (
    <aside className="flex h-screen w-60 flex-col bg-gray-900 text-gray-100 shadow-xl">
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 py-5 border-b border-gray-700">
        <span className="text-2xl">⚡</span>
        <span className="text-lg font-bold tracking-tight">OpsAI</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/');
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="border-t border-gray-700 px-3 py-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOutIcon className="h-4 w-4 shrink-0" />
          Log out
        </button>
      </div>
    </aside>
  );
}

'use client';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Activity, CheckCircle, XCircle, TrendingUp } from 'lucide-react';

const statCards = [
  { label: 'Total Runs', key: 'total', icon: Activity, color: 'text-blue-400', bg: 'bg-blue-900/20' },
  { label: 'Failed', key: 'failed', icon: XCircle, color: 'text-red-400', bg: 'bg-red-900/20' },
  { label: 'Resolved', key: 'resolved', icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-900/20' },
  { label: 'Avg. MTTR', key: 'mttr', icon: TrendingUp, color: 'text-yellow-400', bg: 'bg-yellow-900/20' },
];

export function DashboardStats() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get('/stats').then(r => r.data),
  });

  const mockStats = { total: 148, failed: 23, resolved: 21, mttr: '14m' };
  const stats = data || mockStats;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map(({ label, key, icon: Icon, color, bg }) => (
        <div key={key} className="card flex items-center gap-4">
          <div className={`${bg} p-3 rounded-lg`}>
            <Icon size={22} className={color} />
          </div>
          <div>
            <p className="text-sm text-gray-400">{label}</p>
            <p className="text-2xl font-bold text-white">
              {isLoading ? '...' : stats[key as keyof typeof stats]}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

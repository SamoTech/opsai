'use client';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import { GitBranch, Clock, ChevronRight } from 'lucide-react';
import Link from 'next/link';

export function RecentRuns() {
  const { data: runs, isLoading } = useQuery({
    queryKey: ['recent-runs'],
    queryFn: () => api.get('/runs/recent').then(r => r.data),
  });

  const mockRuns = [
    { id: '1', pipeline_name: 'CI Build', branch: 'main', status: 'failed', created_at: new Date().toISOString(), root_cause: 'dependency' },
    { id: '2', pipeline_name: 'Deploy Staging', branch: 'develop', status: 'success', created_at: new Date(Date.now() - 3600000).toISOString(), root_cause: null },
    { id: '3', pipeline_name: 'Unit Tests', branch: 'feature/auth', status: 'failed', created_at: new Date(Date.now() - 7200000).toISOString(), root_cause: 'code_error' },
  ];

  const displayRuns = runs || mockRuns;

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-white mb-4">🔄 Recent Pipeline Runs</h2>
      {isLoading ? (
        <p className="text-gray-500 text-sm">Loading...</p>
      ) : (
        <div className="space-y-3">
          {displayRuns.map((run: any) => (
            <Link
              key={run.id}
              href={`/runs/${run.id}`}
              className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors group"
            >
              <div className="flex items-center gap-4">
                <span className={run.status === 'failed' ? 'badge-failed' : run.status === 'success' ? 'badge-success' : 'badge-pending'}>
                  {run.status}
                </span>
                <div>
                  <p className="text-sm font-medium text-white">{run.pipeline_name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <GitBranch size={12} className="text-gray-500" />
                    <span className="text-xs text-gray-500">{run.branch}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {run.root_cause && (
                  <span className="text-xs text-gray-500 bg-gray-700 px-2 py-1 rounded">
                    {run.root_cause.replace('_', ' ')}
                  </span>
                )}
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <Clock size={12} />
                  {formatDistanceToNow(new Date(run.created_at), { addSuffix: true })}
                </div>
                <ChevronRight size={16} className="text-gray-600 group-hover:text-gray-400" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

import { Sidebar } from '@/components/layout/Sidebar';
import { DashboardStats } from '@/components/dashboard/DashboardStats';
import { RecentRuns } from '@/components/dashboard/RecentRuns';

export default function HomePage() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white">🤖 OpsAI Dashboard</h1>
            <p className="text-gray-400 mt-1">Real-time CI/CD pipeline intelligence</p>
          </div>
          <DashboardStats />
          <div className="mt-8">
            <RecentRuns />
          </div>
        </div>
      </main>
    </div>
  );
}

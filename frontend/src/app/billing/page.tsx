import { Check } from 'lucide-react';
import { Sidebar } from '@/components/layout/Sidebar';

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    description: 'Perfect to get started',
    features: ['3 projects', '50 runs/month', 'Slack alerts', 'Community support'],
    cta: 'Current Plan',
    highlighted: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 29,
    description: 'For serious developers',
    features: ['Unlimited projects', '1,000 runs/month', 'Auto-fix PRs', 'PR comment bot', 'Email + Slack alerts', 'Priority support'],
    cta: 'Upgrade to Pro',
    highlighted: true,
  },
  {
    id: 'team',
    name: 'Team',
    price: 99,
    description: 'For engineering teams',
    features: ['Everything in Pro', '10,000 runs/month', 'Team workspaces', 'SSO (Google + GitHub)', 'Role-based access', 'Dedicated support'],
    cta: 'Upgrade to Team',
    highlighted: false,
  },
];

export default function BillingPage() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-5xl mx-auto">
          <div className="mb-10 text-center">
            <h1 className="text-3xl font-bold text-white">💳 Plans & Billing</h1>
            <p className="text-gray-400 mt-2">Upgrade to unlock more power</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`card flex flex-col ${
                  plan.highlighted ? 'border-blue-500 ring-2 ring-blue-500/30' : ''
                }`}
              >
                {plan.highlighted && (
                  <div className="text-center mb-4">
                    <span className="bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                <h2 className="text-xl font-bold text-white">{plan.name}</h2>
                <p className="text-gray-400 text-sm mt-1">{plan.description}</p>
                <div className="my-4">
                  <span className="text-4xl font-bold text-white">${plan.price}</span>
                  {plan.price > 0 && <span className="text-gray-400 text-sm">/month</span>}
                </div>
                <ul className="space-y-2 flex-1 mb-6">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-gray-300">
                      <Check size={14} className="text-green-400 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <button
                  className={`w-full py-2.5 rounded-lg font-medium text-sm transition-colors ${
                    plan.highlighted
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : plan.price === 0
                      ? 'bg-gray-700 text-gray-400 cursor-default'
                      : 'bg-gray-700 hover:bg-gray-600 text-white'
                  }`}
                  disabled={plan.price === 0}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

'use client';
import { useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Key, Plus, Trash2, Copy, Eye, EyeOff } from 'lucide-react';

const mockKeys = [
  { id: '1', name: 'Production Integration', key_prefix: 'opsai_abc1', created_at: '2026-03-01', requests_count: 142 },
  { id: '2', name: 'CI Script', key_prefix: 'opsai_xyz9', created_at: '2026-03-10', requests_count: 38 },
];

export default function APIKeysPage() {
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyVisible, setNewKeyVisible] = useState<string | null>(null);

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-3xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white">🔑 API Keys</h1>
            <p className="text-gray-400 mt-1">Use API keys to integrate OpsAI into your own tools</p>
          </div>

          {/* Create new key */}
          <div className="card mb-6">
            <h2 className="text-lg font-semibold text-white mb-4">Create New Key</h2>
            <div className="flex gap-3">
              <input
                type="text"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="Key name e.g. Production CI"
                className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
              <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors">
                <Plus size={16} /> Generate
              </button>
            </div>
          </div>

          {/* Keys list */}
          <div className="card">
            <h2 className="text-lg font-semibold text-white mb-4">Active Keys</h2>
            <div className="space-y-3">
              {mockKeys.map((key) => (
                <div key={key.id} className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Key size={16} className="text-blue-400" />
                    <div>
                      <p className="text-sm font-medium text-white">{key.name}</p>
                      <p className="text-xs text-gray-500 font-mono">{key.key_prefix}••••••••••••••</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-gray-500">{key.requests_count} requests</span>
                    <button className="text-gray-500 hover:text-white transition-colors">
                      <Copy size={15} />
                    </button>
                    <button className="text-gray-500 hover:text-red-400 transition-colors">
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Usage example */}
          <div className="card mt-6">
            <h2 className="text-lg font-semibold text-white mb-3">💻 Usage Example</h2>
            <pre className="bg-gray-950 rounded-lg p-4 text-xs text-green-400 overflow-x-auto">{`# Python SDK
import opsai
client = opsai.Client(api_key="opsai_abc1...")
result = client.analyze(log_text=open("build.log").read())
print(result.fix_suggestion)

# JavaScript SDK
import { OpsAI } from '@opsai/sdk';
const client = new OpsAI({ apiKey: 'opsai_abc1...' });
const result = await client.analyze({ log: buildLog });
console.log(result.fixSuggestion);`}</pre>
          </div>
        </div>
      </main>
    </div>
  );
}

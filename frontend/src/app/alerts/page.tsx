'use client';

import { useEffect, useState } from 'react';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    fetch('/api/alerts').then((r) => r.json()).then(setAlerts).catch(() => {});
  }, []);

  const emojiMap: Record<string, string> = { critical: '🔴', important: '🟡', info: '🔵', client: '👤' };

  return (
    <div>
      <h2 className="text-2xl font-bold text-brand-deep-teal mb-4">Alerts</h2>
      <div className="space-y-3">
        {alerts.map((a) => (
          <div key={a.id} className={`bg-white rounded-lg shadow p-4 border-l-4 ${
            a.priority === 'critical' ? 'border-red-500' :
            a.priority === 'important' ? 'border-yellow-500' : 'border-blue-500'
          }`}>
            <div className="flex justify-between items-start">
              <div>
                <p className="font-semibold">{emojiMap[a.priority] || '🔵'} {a.title}</p>
                <p className="text-sm text-gray-600 mt-1">{a.message?.substring(0, 200)}</p>
              </div>
              <span className="text-xs text-gray-400">{a.created_at}</span>
            </div>
          </div>
        ))}
        {alerts.length === 0 && <p className="text-gray-400 text-center py-8">No alerts — connect backend</p>}
      </div>
    </div>
  );
}

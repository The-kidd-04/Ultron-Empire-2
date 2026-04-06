'use client';

import { useEffect, useState } from 'react';
import { fetchDashboard, fetchMarket } from '@/lib/api';
import AlertCard from '@/components/AlertCard';

export default function Dashboard() {
  const [dash, setDash] = useState<any>(null);
  const [market, setMarket] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchDashboard().catch(() => null),
      fetchMarket().catch(() => null),
    ]).then(([d, m]) => {
      setDash(d);
      setMarket(m);
      setLoading(false);
    });
  }, []);

  const nifty = market?.nifty ?? '—';
  const niftyChange = market?.nifty_change_pct;
  const vix = market?.vix ?? '—';
  const totalAum = dash?.aum?.total_cr ?? '—';
  const clientCount = dash?.aum?.client_count ?? 0;
  const criticalAlerts = (dash?.alerts?.critical ?? 0) + (dash?.alerts?.important ?? 0);
  const recentAlerts = dash?.alerts?.recent ?? [];
  const overdueClients = dash?.reviews?.overdue_clients ?? [];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-brand-deep-teal">Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashCard
          title="Total AUM"
          value={loading ? '...' : `₹${totalAum} Cr`}
          subtitle={`Across ${clientCount} clients`}
          color="emerald"
        />
        <DashCard
          title="Active Alerts"
          value={loading ? '...' : String(criticalAlerts)}
          subtitle={`${dash?.alerts?.critical ?? 0} critical, ${dash?.alerts?.important ?? 0} important`}
          color="red"
        />
        <DashCard
          title="Nifty 50"
          value={loading ? '...' : String(nifty)}
          subtitle={niftyChange != null ? `${niftyChange >= 0 ? '+' : ''}${niftyChange}%` : ''}
          color="green"
        />
        <DashCard
          title="India VIX"
          value={loading ? '...' : String(vix)}
          subtitle={vix !== '—' ? (vix < 15 ? 'Low volatility' : vix < 20 ? 'Moderate' : 'High volatility') : ''}
          color="blue"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-brand-deep-teal mb-4">Recent Alerts</h3>
          {loading ? (
            <p className="text-gray-400 text-sm">Loading...</p>
          ) : recentAlerts.length > 0 ? (
            <div className="space-y-3">
              {recentAlerts.map((a: any) => (
                <AlertCard
                  key={a.id}
                  priority={a.priority}
                  title={a.title}
                  message=""
                  createdAt={a.created_at}
                />
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No recent alerts</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-brand-deep-teal mb-4">Client Reviews Due</h3>
          {loading ? (
            <p className="text-gray-400 text-sm">Loading...</p>
          ) : overdueClients.length > 0 ? (
            <div className="space-y-2">
              {overdueClients.map((c: any, i: number) => (
                <div key={i} className="flex justify-between items-center py-2 border-b last:border-0">
                  <span className="text-sm font-medium text-brand-deep-teal">{c.name}</span>
                  <span className="text-xs text-red-500">Due: {c.due}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No overdue reviews</p>
          )}
        </div>
      </div>
    </div>
  );
}

function DashCard({ title, value, subtitle, color }: { title: string; value: string; subtitle: string; color: string }) {
  const colorMap: Record<string, string> = {
    emerald: 'border-brand-emerald',
    red: 'border-red-500',
    green: 'border-green-500',
    blue: 'border-blue-500',
  };
  return (
    <div className={`bg-white rounded-lg shadow p-5 border-l-4 ${colorMap[color] || 'border-gray-300'}`}>
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-bold text-brand-deep-teal mt-1">{value}</p>
      <p className="text-xs text-gray-400 mt-1">{subtitle}</p>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch('/api/analytics').then(r => r.json()).then(setData).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-brand-deep-teal">Business Analytics</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total AUM" value={data ? `₹${data.total_aum_cr} Cr` : '—'} />
        <StatCard title="Total Clients" value={data ? data.total_clients : '—'} />
        <StatCard title="Avg AUM/Client" value={data ? `₹${data.avg_aum_per_client_cr} Cr` : '—'} />
        <StatCard title="Monthly Trail" value={data ? `₹${(data.estimated_monthly_trail_cr * 100).toFixed(0)}K` : '—'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-4">Client Concentration</h3>
          {data?.client_concentration ? (
            <div>
              <div className={`text-2xl font-bold ${
                data.client_concentration.risk_level === 'High' ? 'text-red-600' :
                data.client_concentration.risk_level === 'Moderate' ? 'text-yellow-600' : 'text-green-600'
              }`}>
                Top 3 = {data.client_concentration.top3_pct}% of AUM
              </div>
              <p className="text-sm text-gray-500 mt-1">Risk: {data.client_concentration.risk_level}</p>
              {data.client_concentration.top3?.map(([name, aum]: [string, number], i: number) => (
                <div key={i} className="flex justify-between py-1 text-sm border-b last:border-0">
                  <span>{name}</span><span className="font-medium">₹{aum} Cr</span>
                </div>
              ))}
            </div>
          ) : <p className="text-gray-400">Connect backend...</p>}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-4">Risk Profile Distribution</h3>
          {data?.risk_profile_distribution ? (
            Object.entries(data.risk_profile_distribution).map(([profile, count]) => (
              <div key={profile} className="flex justify-between py-2 border-b last:border-0">
                <span className={`px-2 py-0.5 rounded text-xs ${
                  profile === 'Aggressive' ? 'bg-red-100 text-red-700' :
                  profile === 'Moderate' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'
                }`}>{profile}</span>
                <span className="font-medium">{count as number} clients</span>
              </div>
            ))
          ) : <p className="text-gray-400">Connect backend...</p>}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-4">Wallet Share</h3>
          <div className="text-3xl font-bold text-brand-emerald">{data?.wallet_share_pct || 0}%</div>
          <p className="text-sm text-gray-500">of total client wealth managed by us</p>
          <div className="mt-2 w-full bg-gray-100 rounded-full h-3">
            <div className="h-3 rounded-full bg-brand-emerald" style={{width: `${data?.wallet_share_pct || 0}%`}} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-4">Revenue Forecast</h3>
          <div className="text-2xl font-bold text-brand-deep-teal">₹{data ? (data.estimated_annual_trail_cr * 100).toFixed(0) : '—'}K/year</div>
          <p className="text-sm text-gray-500">Estimated trail income at 0.75% avg</p>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="bg-white rounded-lg shadow p-5 border-l-4 border-brand-emerald">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-bold text-brand-deep-teal mt-1">{value}</p>
    </div>
  );
}

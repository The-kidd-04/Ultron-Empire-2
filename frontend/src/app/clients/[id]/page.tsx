'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import PortfolioChart from '@/components/PortfolioChart';

export default function ClientDetailPage() {
  const params = useParams();
  const [client, setClient] = useState<any>(null);

  useEffect(() => {
    if (params.id) {
      fetch(`/api/clients/${params.id}`).then((r) => r.json()).then(setClient).catch(() => {});
    }
  }, [params.id]);

  if (!client) return <div className="text-center py-20 text-gray-400">Loading client...</div>;

  const holdings = (client.holdings || []).map((h: any) => ({ product: h.product, amount: h.amount }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-brand-deep-teal">{client.name}</h2>
          <p className="text-gray-500">{client.age} yrs | {client.occupation} | {client.city}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          client.risk_profile === 'Aggressive' ? 'bg-red-100 text-red-700' :
          client.risk_profile === 'Moderate' ? 'bg-yellow-100 text-yellow-700' :
          'bg-green-100 text-green-700'
        }`}>{client.risk_profile}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard label="Total Wealth" value={`₹${client.total_investable_wealth} Cr`} />
        <StatCard label="AUM with Us" value={`₹${client.current_aum_with_us} Cr`} />
        <StatCard label="Investment Horizon" value={`${client.investment_horizon} years`} />
        <StatCard label="Annual Income" value={`₹${client.annual_income} Cr`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {holdings.length > 0 && <PortfolioChart holdings={holdings} />}

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-3">Goals</h3>
          {(client.goals || []).map((g: any, i: number) => (
            <div key={i} className="flex justify-between py-2 border-b last:border-0 text-sm">
              <span>{g.name}</span>
              <span className="font-medium">₹{g.target} Cr in {g.years} yrs</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-3">Family</h3>
          {(client.family_members || []).map((f: any, i: number) => (
            <div key={i} className="text-sm py-1">{f.name} — {f.relation}, age {f.age}</div>
          ))}
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-3">Notes</h3>
          <p className="text-sm text-gray-600">{client.notes || 'No notes'}</p>
          <div className="mt-3 text-xs text-gray-400 space-y-1">
            <div>Last Review: {client.last_review_date || '—'}</div>
            <div>Next Review: {client.next_review_date || '—'}</div>
            <div>Prefers: {client.communication_preference || '—'}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-xl font-bold text-brand-deep-teal mt-1">{value}</p>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';

interface ClientSummary {
  id: number;
  name: string;
  city: string;
  risk_profile: string;
  current_aum_with_us: number;
  tags: string[];
  next_review_date: string | null;
}

export default function ClientsPage() {
  const [clients, setClients] = useState<ClientSummary[]>([]);

  useEffect(() => {
    fetch('/api/clients').then((r) => r.json()).then(setClients).catch(() => {});
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold text-brand-deep-teal mb-4">Clients</h2>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-brand-deep-teal text-white">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">City</th>
              <th className="px-4 py-3 text-left">Risk Profile</th>
              <th className="px-4 py-3 text-right">AUM (Cr)</th>
              <th className="px-4 py-3 text-left">Next Review</th>
              <th className="px-4 py-3 text-left">Tags</th>
            </tr>
          </thead>
          <tbody>
            {clients.map((c) => (
              <tr key={c.id} className="border-b hover:bg-brand-light-bg">
                <td className="px-4 py-3 font-medium">
                  <a href={`/clients/${c.id}`} className="text-brand-emerald hover:underline">{c.name}</a>
                </td>
                <td className="px-4 py-3">{c.city}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs ${
                    c.risk_profile === 'Aggressive' ? 'bg-red-100 text-red-700' :
                    c.risk_profile === 'Moderate' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>{c.risk_profile}</span>
                </td>
                <td className="px-4 py-3 text-right">₹{c.current_aum_with_us}</td>
                <td className="px-4 py-3">{c.next_review_date || '—'}</td>
                <td className="px-4 py-3">{(c.tags || []).map((t) => (
                  <span key={t} className="inline-block bg-brand-mint/20 text-brand-forest text-xs px-2 py-0.5 rounded mr-1">{t}</span>
                ))}</td>
              </tr>
            ))}
            {clients.length === 0 && (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">Connect backend to load clients</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

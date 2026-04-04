'use client';

import { useEffect, useState } from 'react';

export default function MarketPage() {
  const [data, setData] = useState<string>('');

  useEffect(() => {
    fetch('/api/market').then((r) => r.json()).then((d) => setData(d.data)).catch(() => {});
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold text-brand-deep-teal mb-4">Market Overview</h2>
      <div className="bg-white rounded-lg shadow p-6">
        <pre className="whitespace-pre-wrap text-sm font-mono">{data || 'Loading market data...'}</pre>
      </div>
    </div>
  );
}

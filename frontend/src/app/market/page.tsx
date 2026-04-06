'use client';

import { useEffect, useState } from 'react';
import { fetchMarket } from '@/lib/api';
import SectorHeatmap from '@/components/SectorHeatmap';

export default function MarketPage() {
  const [data, setData] = useState<any>(null);
  const [sectors, setSectors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchMarket('overview').catch(() => null),
      fetchMarket('sectors').catch(() => ({ data: '' })),
    ]).then(([overview, sectorData]) => {
      setData(overview);
      // Parse sector data from text response if available
      if (sectorData?.data) {
        const parsed = parseSectors(sectorData.data);
        if (parsed.length > 0) setSectors(parsed);
      }
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="text-center py-20 text-gray-400">Loading market data...</div>
    );
  }

  const niftyChange = data?.nifty_change_pct ?? 0;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-brand-deep-teal">Market Overview</h2>

      {/* Index Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <IndexCard
          name="Nifty 50"
          value={data?.nifty}
          change={niftyChange}
        />
        <IndexCard
          name="Sensex"
          value={data?.sensex}
          change={niftyChange}
        />
        <VixCard value={data?.vix} />
        <FiiDiiCard fii={data?.fii_net} dii={data?.dii_net} />
      </div>

      {/* Sector Heatmap */}
      {sectors.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-4">Sector Performance</h3>
          <SectorHeatmap sectors={sectors} />
        </div>
      )}

      {/* Raw Market Data */}
      {data?.data && typeof data.data === 'string' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-4">Detailed Market Data</h3>
          <pre className="whitespace-pre-wrap text-sm font-mono text-gray-700 max-h-96 overflow-y-auto">
            {data.data}
          </pre>
        </div>
      )}

      {/* PE Ratio */}
      {data?.nifty_pe && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-2">Nifty PE Ratio</h3>
          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-bold text-brand-deep-teal">{data.nifty_pe}</span>
            <span className="text-sm text-gray-500">
              {data.nifty_pe < 18 ? 'Attractive valuation' :
               data.nifty_pe < 22 ? 'Fair valuation' :
               data.nifty_pe < 25 ? 'Expensive' : 'Overvalued'}
            </span>
          </div>
          <div className="mt-3 w-full bg-gray-100 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                data.nifty_pe < 18 ? 'bg-green-500' :
                data.nifty_pe < 22 ? 'bg-yellow-400' :
                data.nifty_pe < 25 ? 'bg-orange-500' : 'bg-red-500'
              }`}
              style={{ width: `${Math.min((data.nifty_pe / 35) * 100, 100)}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function IndexCard({ name, value, change }: { name: string; value?: number; change?: number }) {
  const isPositive = (change ?? 0) >= 0;
  return (
    <div className="bg-white rounded-lg shadow p-5">
      <p className="text-sm text-gray-500">{name}</p>
      <p className="text-2xl font-bold text-brand-deep-teal mt-1">
        {value ? value.toLocaleString('en-IN') : '—'}
      </p>
      {change != null && (
        <p className={`text-sm mt-1 font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
          {isPositive ? '+' : ''}{change.toFixed(2)}%
        </p>
      )}
    </div>
  );
}

function VixCard({ value }: { value?: number }) {
  const level = !value ? 'Unknown' : value < 15 ? 'Low' : value < 20 ? 'Moderate' : 'High';
  const color = level === 'Low' ? 'text-green-600' : level === 'Moderate' ? 'text-yellow-600' : 'text-red-600';
  return (
    <div className="bg-white rounded-lg shadow p-5">
      <p className="text-sm text-gray-500">India VIX</p>
      <p className="text-2xl font-bold text-brand-deep-teal mt-1">{value ?? '—'}</p>
      <p className={`text-sm mt-1 font-medium ${color}`}>{level} volatility</p>
    </div>
  );
}

function FiiDiiCard({ fii, dii }: { fii?: number; dii?: number }) {
  return (
    <div className="bg-white rounded-lg shadow p-5">
      <p className="text-sm text-gray-500 mb-2">FII / DII (Cr)</p>
      <div className="space-y-1">
        <div className="flex justify-between text-sm">
          <span>FII</span>
          <span className={`font-medium ${(fii ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {fii != null ? `${fii >= 0 ? '+' : ''}₹${fii}` : '—'}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span>DII</span>
          <span className={`font-medium ${(dii ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {dii != null ? `${dii >= 0 ? '+' : ''}₹${dii}` : '—'}
          </span>
        </div>
      </div>
    </div>
  );
}

function parseSectors(text: string): { name: string; changePct: number }[] {
  const sectors: { name: string; changePct: number }[] = [];
  const lines = text.split('\n');
  for (const line of lines) {
    const match = line.match(/([A-Za-z\s&]+).*?([+-]?\d+\.?\d*)%/);
    if (match) {
      sectors.push({ name: match[1].trim(), changePct: parseFloat(match[2]) });
    }
  }
  return sectors;
}

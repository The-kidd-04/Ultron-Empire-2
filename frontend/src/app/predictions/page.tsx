'use client';

import { useEffect, useState } from 'react';
import { fetchMomentum, fetchValuation, fetchDrawdownRisk, fetchPatterns, refreshMomentum } from '@/lib/api';
import MomentumGauge from '@/components/MomentumGauge';

export default function PredictionsPage() {
  const [momentum, setMomentum] = useState<any[]>([]);
  const [valuation, setValuation] = useState<any>(null);
  const [drawdown, setDrawdown] = useState<any>(null);
  const [patterns, setPatterns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAll();
  }, []);

  async function loadAll() {
    setLoading(true);
    const [m, v, d, p] = await Promise.all([
      fetchMomentum().catch(() => []),
      fetchValuation().catch(() => null),
      fetchDrawdownRisk().catch(() => null),
      fetchPatterns().catch(() => []),
    ]);
    setMomentum(Array.isArray(m) ? m : []);
    setValuation(v);
    setDrawdown(d);
    setPatterns(Array.isArray(p) ? p : p?.matches || []);
    setLoading(false);
  }

  async function handleRefresh() {
    setRefreshing(true);
    await refreshMomentum().catch(() => {});
    await loadAll();
    setRefreshing(false);
  }

  if (loading) {
    return <div className="text-center py-20 text-gray-400">Loading prediction signals...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-brand-deep-teal">Market Signals & Predictions</h2>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-4 py-2 text-sm bg-brand-emerald text-white rounded-lg hover:bg-brand-forest disabled:opacity-50"
        >
          {refreshing ? 'Refreshing...' : 'Refresh Signals'}
        </button>
      </div>

      {/* Sector Momentum */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold text-brand-deep-teal mb-4">Sector Momentum</h3>
        {momentum.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {momentum.map((m: any, i: number) => (
              <MomentumGauge
                key={i}
                sector={m.sector}
                score={m.score}
                signal={m.signal}
                confidence={m.confidence}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">No momentum signals yet. Click "Refresh Signals" to compute.</p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Valuation Zone */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-4">Valuation Zone</h3>
          {valuation ? (
            <div>
              <div className="flex items-baseline gap-3 mb-3">
                <span className="text-3xl font-bold text-brand-deep-teal">
                  {valuation.pe_ratio || valuation.pe}
                </span>
                <span className="text-sm text-gray-500">Nifty PE</span>
              </div>
              <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-3 ${
                valuation.zone === 'Deep Value' || valuation.zone === 'Value Zone' ? 'bg-green-100 text-green-700' :
                valuation.zone === 'Fair Value' ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                {valuation.zone}
              </div>
              <div className="text-sm text-gray-500 mb-2">
                Percentile: {valuation.percentile}th
              </div>
              {valuation.expected_3y_cagr && (
                <div className="text-sm">
                  <span className="text-gray-500">Expected 3Y CAGR: </span>
                  <span className="font-medium text-brand-emerald">{valuation.expected_3y_cagr}</span>
                </div>
              )}
              {valuation.recommendation && (
                <p className="text-sm text-gray-600 mt-3 border-t pt-3">{valuation.recommendation}</p>
              )}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">Valuation data unavailable</p>
          )}
        </div>

        {/* Drawdown Risk */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-4">Drawdown Risk</h3>
          {drawdown ? (
            <div className="space-y-4">
              <div className={`text-lg font-bold ${
                drawdown.risk_level === 'Low' ? 'text-green-600' :
                drawdown.risk_level === 'Moderate' ? 'text-yellow-600' :
                drawdown.risk_level === 'High' ? 'text-orange-600' : 'text-red-600'
              }`}>
                Risk: {drawdown.risk_level}
              </div>
              <RiskBar label="10% correction" probability={drawdown.prob_10pct_correction} />
              <RiskBar label="20% correction" probability={drawdown.prob_20pct_correction} />
              <RiskBar label="30% correction" probability={drawdown.prob_30pct_correction} />
              {drawdown.analysis && (
                <p className="text-xs text-gray-500 mt-2 border-t pt-2">{drawdown.analysis}</p>
              )}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">Drawdown data unavailable</p>
          )}
        </div>
      </div>

      {/* Pattern Matches */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold text-brand-deep-teal mb-4">Historical Pattern Matches</h3>
        {patterns.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {patterns.map((p: any, i: number) => (
              <div key={i} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-brand-deep-teal text-sm">{p.pattern || p.name}</h4>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-brand-mint/20 text-brand-forest">
                    {p.probability || p.confidence}% match
                  </span>
                </div>
                <p className="text-xs text-gray-500">{p.description || p.historical_outcome}</p>
                {p.action && (
                  <p className="text-xs text-brand-emerald mt-2 font-medium">{p.action}</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">No pattern matches for current conditions</p>
        )}
      </div>
    </div>
  );
}

function RiskBar({ label, probability }: { label: string; probability?: number }) {
  const pct = probability ?? 0;
  const color = pct < 20 ? 'bg-green-500' : pct < 40 ? 'bg-yellow-500' : pct < 60 ? 'bg-orange-500' : 'bg-red-500';
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{pct}%</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

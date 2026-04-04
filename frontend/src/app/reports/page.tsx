'use client';

import { useState } from 'react';

const REPORT_TYPES = [
  { id: 'client_portfolio', label: 'Client Portfolio Report', description: 'Full portfolio analysis for a client meeting' },
  { id: 'fund_comparison', label: 'Fund Comparison', description: 'Detailed side-by-side fund comparison' },
  { id: 'market_outlook', label: 'Market Outlook', description: 'Comprehensive market analysis and strategy' },
];

export default function ReportsPage() {
  const [reportType, setReportType] = useState('client_portfolio');
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  async function generate() {
    if (!input.trim()) return;
    setLoading(true);
    try {
      const body: any = { report_type: reportType };
      if (reportType === 'client_portfolio') body.client_name = input;
      else if (reportType === 'fund_comparison') body.fund_names = input.split(' vs ').map((s: string) => s.trim());

      const res = await fetch('/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      setResult(data.content || data.error || 'No report generated');
    } catch {
      setResult('Error connecting to backend');
    }
    setLoading(false);
  }

  const selected = REPORT_TYPES.find((r) => r.id === reportType)!;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-brand-deep-teal">Report Generator</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {REPORT_TYPES.map((rt) => (
          <button key={rt.id} onClick={() => setReportType(rt.id)}
            className={`text-left p-4 rounded-lg border transition ${
              reportType === rt.id ? 'border-brand-emerald bg-brand-emerald/5' : 'bg-white hover:border-brand-emerald'
            }`}>
            <p className="font-semibold text-sm text-brand-deep-teal">{rt.label}</p>
            <p className="text-xs text-gray-500 mt-1">{rt.description}</p>
          </button>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <input className="w-full border rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-emerald focus:outline-none"
          placeholder={
            reportType === 'client_portfolio' ? 'Client name (e.g., Rajesh Mehta)' :
            reportType === 'fund_comparison' ? 'Fund A vs Fund B' : 'Click generate'
          }
          value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && generate()} />

        <button onClick={generate} disabled={loading}
          className="bg-brand-emerald text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-forest disabled:opacity-50">
          {loading ? 'Generating Report...' : 'Generate Report'}
        </button>
      </div>

      {result && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-brand-deep-teal mb-3">{selected.label}</h3>
          <pre className="whitespace-pre-wrap text-sm font-sans">{result}</pre>
        </div>
      )}
    </div>
  );
}

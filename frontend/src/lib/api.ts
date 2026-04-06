const API_BASE = '/api';

export async function fetchChat(query: string) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  return res.json();
}

export async function fetchAlerts(limit = 20) {
  const res = await fetch(`${API_BASE}/alerts?limit=${limit}`);
  return res.json();
}

export async function fetchClients(search?: string) {
  const params = search ? `?search=${encodeURIComponent(search)}` : '';
  const res = await fetch(`${API_BASE}/clients${params}`);
  return res.json();
}

export async function fetchMarket(indicator = 'overview') {
  const res = await fetch(`${API_BASE}/market?indicator=${indicator}`);
  return res.json();
}

export async function fetchClient(id: number) {
  const res = await fetch(`${API_BASE}/clients/${id}`);
  return res.json();
}

export async function fetchDashboard() {
  const res = await fetch(`${API_BASE}/dashboard`);
  return res.json();
}

export async function fetchMarketHistory(days = 30) {
  const res = await fetch(`${API_BASE}/market/history?days=${days}`);
  return res.json();
}

export async function fetchMomentum() {
  const res = await fetch(`${API_BASE}/predictions/momentum`);
  return res.json();
}

export async function fetchValuation(pe?: number) {
  const params = pe ? `?pe=${pe}` : '';
  const res = await fetch(`${API_BASE}/predictions/valuation${params}`);
  return res.json();
}

export async function fetchDrawdownRisk(pe?: number, vix?: number, fiiNet?: number) {
  const params = new URLSearchParams();
  if (pe) params.set('nifty_pe', String(pe));
  if (vix) params.set('vix', String(vix));
  if (fiiNet) params.set('fii_net_monthly', String(fiiNet));
  const qs = params.toString();
  const res = await fetch(`${API_BASE}/predictions/drawdown-risk${qs ? '?' + qs : ''}`);
  return res.json();
}

export async function fetchPatterns(pe?: number, vix?: number) {
  const params = new URLSearchParams();
  if (pe) params.set('nifty_pe', String(pe));
  if (vix) params.set('vix', String(vix));
  const qs = params.toString();
  const res = await fetch(`${API_BASE}/predictions/patterns${qs ? '?' + qs : ''}`);
  return res.json();
}

export async function postMonteCarlo(data: {
  portfolio_cr: number;
  allocation: Record<string, number>;
  years?: number;
  target_cr?: number;
}) {
  const res = await fetch(`${API_BASE}/predictions/monte-carlo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function fetchAnalytics() {
  const res = await fetch(`${API_BASE}/analytics`);
  return res.json();
}

export async function postContent(data: {
  content_type: string;
  topic?: string;
  context?: string;
  client_name?: string;
}) {
  const res = await fetch(`${API_BASE}/content`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function postReport(data: {
  report_type: string;
  client_name?: string;
  fund_names?: string[];
}) {
  const res = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function refreshMomentum() {
  const res = await fetch(`${API_BASE}/predictions/momentum/refresh`);
  return res.json();
}

export async function fetchEarnings() {
  const res = await fetch(`${API_BASE}/market/earnings`);
  return res.json();
}

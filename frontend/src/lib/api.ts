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

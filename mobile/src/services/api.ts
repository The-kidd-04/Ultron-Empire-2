const API_URL = 'https://api.ultron.pmssahihai.com/api/v1';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_URL}${path}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  };

  const res = await fetch(url, { ...options, headers });

  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${body || res.statusText}`);
  }

  return res.json();
}

// ---------- Dashboard ----------
export interface DashboardData {
  aum: {
    total_cr: number;
    client_count: number;
    avg_per_client_cr: number;
  };
  alerts: {
    critical: number;
    important: number;
    info: number;
    recent: AlertData[];
  };
  reviews: {
    overdue_count: number;
    overdue_clients: { name: string; due: string }[];
  };
}

export function fetchDashboard(): Promise<DashboardData> {
  return request<DashboardData>('/dashboard');
}

// ---------- Chat ----------
export interface ChatResponse {
  response: string;
  tools_used: string[];
}

export function sendChat(query: string): Promise<ChatResponse> {
  return request<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
}

// ---------- Voice ----------
export async function sendVoice(audioUri: string): Promise<ChatResponse> {
  const formData = new FormData();
  formData.append('file', {
    uri: audioUri,
    name: 'voice.m4a',
    type: 'audio/m4a',
  } as any);

  const res = await fetch(`${API_URL}/chat/voice`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Voice API ${res.status}`);
  }

  return res.json();
}

// ---------- Alerts ----------
export interface AlertData {
  id: string;
  title: string;
  description: string;
  priority: 'critical' | 'important' | 'info';
  timestamp: string;
  client_name?: string;
}

export function fetchAlerts(limit = 20): Promise<AlertData[]> {
  return request<AlertData[]>(`/alerts?limit=${limit}`);
}

// ---------- Clients ----------
export interface ClientSummary {
  id: string;
  name: string;
  aum_cr: number;
  risk_profile: string;
  phone?: string;
  email?: string;
}

export interface ClientDetail extends ClientSummary {
  pan: string;
  joined_date: string;
  next_review: string;
  holdings: {
    name: string;
    allocation_pct: number;
    value_cr: number;
    return_pct: number;
  }[];
  contact: {
    phone: string;
    email: string;
    address: string;
  };
}

export function fetchClients(): Promise<ClientSummary[]> {
  return request<ClientSummary[]>('/clients');
}

export function fetchClientById(id: string): Promise<ClientDetail> {
  return request<ClientDetail>(`/clients/${id}`);
}

// ---------- Market ----------
export interface MarketOverview {
  indices: {
    name: string;
    value: number;
    change: number;
    change_pct: number;
  }[];
  sectors: {
    name: string;
    change_pct: number;
  }[];
  vix: number;
  updated_at: string;
}

export function fetchMarket(): Promise<MarketOverview> {
  return request<MarketOverview>('/market?indicator=overview');
}

// ---------- Predictions ----------
export interface Prediction {
  id: string;
  signal: 'buy' | 'sell' | 'hold';
  ticker: string;
  confidence: number;
  rationale: string;
  timestamp: string;
}

export function fetchPredictions(): Promise<Prediction[]> {
  return request<Prediction[]>('/predictions');
}

// ---------- Content ----------
export interface GeneratedContent {
  content: string;
  type: string;
  topic: string;
}

export function generateContent(type: string, topic: string): Promise<GeneratedContent> {
  return request<GeneratedContent>('/content', {
    method: 'POST',
    body: JSON.stringify({ type, topic }),
  });
}

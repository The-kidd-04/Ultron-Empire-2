const { contextBridge } = require('electron');

// Default API base — can be overridden via settings
const DEFAULT_API = 'http://localhost:8000/api/v1';

function getApiBase() {
  try {
    const stored = localStorage.getItem('ultron_api_url');
    if (stored) return stored;
  } catch {}
  return DEFAULT_API;
}

async function apiFetch(endpoint, options = {}) {
  const base = getApiBase();
  const url = `${base}${endpoint}`;
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

contextBridge.exposeInMainWorld('ultron', {
  /**
   * Send a chat query to the backend
   * @param {string} query
   * @returns {Promise<{response: string, tools_used?: string[], response_time_ms?: number}>}
   */
  sendChat: (query) => apiFetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  }),

  /**
   * Fetch dashboard summary
   */
  fetchDashboard: () => apiFetch('/dashboard'),

  /**
   * Fetch live market data
   */
  fetchMarket: () => apiFetch('/market'),

  /**
   * Fetch active alerts
   */
  fetchAlerts: () => apiFetch('/alerts'),

  /**
   * Fetch client list
   */
  fetchClients: () => apiFetch('/clients'),

  /**
   * Get the current API base URL
   */
  getApiUrl: () => getApiBase(),

  /**
   * Set a custom API base URL (persisted in localStorage)
   */
  setApiUrl: (url) => {
    try { localStorage.setItem('ultron_api_url', url); } catch {}
  },

  /**
   * Reset API URL to default
   */
  resetApiUrl: () => {
    try { localStorage.removeItem('ultron_api_url'); } catch {}
  }
});

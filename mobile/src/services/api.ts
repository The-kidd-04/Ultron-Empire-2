const API_URL = 'https://api.ultron.pmssahihai.com/api/v1';

export async function fetchDashboard() {
  const res = await fetch(`${API_URL}/dashboard`);
  return res.json();
}

export async function sendChat(query: string) {
  const res = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  return res.json();
}

export async function fetchAlerts(limit = 20) {
  const res = await fetch(`${API_URL}/alerts?limit=${limit}`);
  return res.json();
}

export async function fetchClients() {
  const res = await fetch(`${API_URL}/clients`);
  return res.json();
}

export async function sendVoice(audioUri: string) {
  const formData = new FormData();
  formData.append('file', { uri: audioUri, name: 'voice.ogg', type: 'audio/ogg' } as any);
  const res = await fetch(`${API_URL}/chat/voice`, { method: 'POST', body: formData });
  return res.json();
}

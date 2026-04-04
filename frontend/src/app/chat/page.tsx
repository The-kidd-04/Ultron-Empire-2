'use client';

import { useState } from 'react';

export default function ChatPage() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([]);
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!query.trim()) return;
    const userMsg = query;
    setMessages((prev) => [...prev, { role: 'user', text: userMsg }]);
    setQuery('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: 'ultron', text: data.response }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'ultron', text: 'Error connecting to Ultron backend.' }]);
    }
    setLoading(false);
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-brand-deep-teal mb-4">Chat with Ultron</h2>

      <div className="bg-white rounded-lg shadow min-h-[500px] flex flex-col">
        <div className="flex-1 p-4 space-y-4 overflow-y-auto">
          {messages.length === 0 && (
            <p className="text-gray-400 text-center mt-20">Ask Ultron anything about PMS, AIF, markets, or clients...</p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-3 rounded-lg text-sm whitespace-pre-wrap ${
                m.role === 'user'
                  ? 'bg-brand-deep-teal text-white'
                  : 'bg-brand-light-bg text-brand-near-black border'
              }`}>
                {m.text}
              </div>
            </div>
          ))}
          {loading && <div className="text-brand-emerald text-sm animate-pulse">Ultron is thinking...</div>}
        </div>

        <div className="border-t p-4 flex gap-2">
          <input
            className="flex-1 border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-emerald"
            placeholder="Ask Ultron anything..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-brand-emerald text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-brand-forest disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

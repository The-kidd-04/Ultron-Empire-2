'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'ultron';
  text: string;
  tools?: string[];
  time?: number;
}

export default function ChatInterface() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function send() {
    if (!query.trim() || loading) return;
    const q = query;
    setQuery('');
    setMessages((p) => [...p, { role: 'user', text: q }]);
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
      });
      const data = await res.json();
      setMessages((p) => [...p, { role: 'ultron', text: data.response, tools: data.tools_used, time: data.response_time_ms }]);
    } catch {
      setMessages((p) => [...p, { role: 'ultron', text: 'Connection error. Is the backend running?' }]);
    }
    setLoading(false);
  }

  const suggestions = [
    'Compare Quant Small Cap vs Stallion Asset',
    'Morning brief',
    'Client brief for Rajesh Mehta',
    'Market snapshot',
    'Which PMS has best Sharpe ratio?',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-140px)]">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center mt-16 space-y-4">
            <div className="w-16 h-16 bg-brand-emerald rounded-full flex items-center justify-center mx-auto text-white text-2xl font-bold">N</div>
            <h3 className="text-xl font-semibold text-brand-deep-teal">How can I help you today?</h3>
            <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
              {suggestions.map((s) => (
                <button key={s} onClick={() => { setQuery(s); }} className="text-xs bg-white border border-brand-light-gray rounded-full px-3 py-1.5 hover:border-brand-emerald hover:text-brand-emerald transition">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] rounded-xl px-4 py-3 text-sm whitespace-pre-wrap ${
              m.role === 'user' ? 'bg-brand-deep-teal text-white' : 'bg-white border shadow-sm text-brand-near-black'
            }`}>
              {m.text}
              {m.tools && m.tools.length > 0 && (
                <div className="mt-2 text-xs opacity-60">Tools: {m.tools.join(', ')} | {m.time}ms</div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="flex justify-start"><div className="bg-white border rounded-xl px-4 py-3 text-sm text-brand-emerald animate-pulse">Ultron is analyzing...</div></div>}
        <div ref={bottomRef} />
      </div>

      <div className="border-t bg-white p-3 flex gap-2">
        <input
          className="flex-1 border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-emerald"
          placeholder="Ask Ultron anything about PMS, AIF, markets, clients..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
        />
        <button onClick={send} disabled={loading} className="bg-brand-emerald text-white px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-brand-forest disabled:opacity-50 transition">
          Send
        </button>
      </div>
    </div>
  );
}

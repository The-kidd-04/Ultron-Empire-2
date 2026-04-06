'use client';

import { useState, useEffect } from 'react';

const CONTENT_TYPES = [
  { id: 'social_post', label: 'Social Media Post', icon: '📱', placeholder: 'Topic or theme (e.g., Top 5 PMS funds Q1 2026)' },
  { id: 'client_message', label: 'Client Message', icon: '💬', placeholder: 'Client name + context (e.g., Rajesh Mehta — portfolio review)' },
  { id: 'newsletter', label: 'Newsletter', icon: '📰', placeholder: 'Newsletter theme (e.g., Monthly market recap March 2026)' },
  { id: 'morning_brief', label: 'Morning Brief', icon: '🌅', placeholder: 'Optional focus area (leave empty for auto)' },
  { id: 'whatsapp_message', label: 'WhatsApp Update', icon: '📲', placeholder: 'Quick update topic (e.g., Nifty hits all-time high)' },
];

const DAY_SUGGESTIONS: Record<number, { type: string; topic: string }> = {
  1: { type: 'social_post', topic: 'Weekly market outlook and PMS strategy positioning' },
  2: { type: 'social_post', topic: 'Fund spotlight — highlight a top-performing PMS' },
  3: { type: 'social_post', topic: 'Investor education — key wealth management concept' },
  4: { type: 'social_post', topic: 'Mid-week market review and sectoral analysis' },
  5: { type: 'newsletter', topic: 'Weekly market recap and PMS performance summary' },
  6: { type: 'social_post', topic: 'Weekend reading — book or article recommendation for investors' },
  0: { type: 'social_post', topic: 'Week ahead preview — key events and market outlook' },
};

export default function ContentPage() {
  const [contentType, setContentType] = useState('social_post');
  const [topic, setTopic] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestion, setSuggestion] = useState<{ type: string; topic: string } | null>(null);

  useEffect(() => {
    const day = new Date().getDay();
    setSuggestion(DAY_SUGGESTIONS[day] || null);
  }, []);

  async function generate() {
    if (!topic.trim() && contentType !== 'morning_brief') return;
    setLoading(true);
    try {
      const res = await fetch('/api/content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_type: contentType,
          topic: topic || 'auto',
          context: topic,
          client_name: contentType === 'client_message' ? topic.split('—')[0]?.trim() : undefined,
        }),
      });
      const data = await res.json();
      setResult(data.content || data.error || 'No content generated');
    } catch {
      setResult('Error connecting to backend');
    }
    setLoading(false);
  }

  function useSuggestion() {
    if (suggestion) {
      setContentType(suggestion.type);
      setTopic(suggestion.topic);
    }
  }

  const selected = CONTENT_TYPES.find((ct) => ct.id === contentType)!;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-brand-deep-teal">Content Generator</h2>

      {/* Today's suggestion */}
      {suggestion && (
        <div className="bg-brand-mint/10 border border-brand-mint/30 rounded-lg p-4 flex justify-between items-center">
          <div>
            <p className="text-sm font-medium text-brand-forest">Today's suggested content</p>
            <p className="text-xs text-gray-600 mt-1">{suggestion.topic}</p>
          </div>
          <button
            onClick={useSuggestion}
            className="text-xs px-3 py-1.5 bg-brand-emerald text-white rounded hover:bg-brand-forest"
          >
            Use this
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <div className="flex flex-wrap gap-3">
          {CONTENT_TYPES.map((ct) => (
            <button key={ct.id} onClick={() => setContentType(ct.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm border transition ${
                contentType === ct.id ? 'bg-brand-emerald text-white border-brand-emerald' : 'bg-white hover:border-brand-emerald'
              }`}>
              <span>{ct.icon}</span> {ct.label}
            </button>
          ))}
        </div>

        <input className="w-full border rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-emerald focus:outline-none"
          placeholder={selected.placeholder}
          value={topic} onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && generate()} />

        <button onClick={generate} disabled={loading}
          className="bg-brand-emerald text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-forest disabled:opacity-50">
          {loading ? 'Generating...' : 'Generate Content'}
        </button>
      </div>

      {result && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-brand-deep-teal">Generated Content</h3>
            <button onClick={() => navigator.clipboard.writeText(result)} className="text-xs text-brand-emerald hover:underline">
              Copy to clipboard
            </button>
          </div>
          <pre className="whitespace-pre-wrap text-sm font-sans text-brand-near-black">{result}</pre>
        </div>
      )}
    </div>
  );
}

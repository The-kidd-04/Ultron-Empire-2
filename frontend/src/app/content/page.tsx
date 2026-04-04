'use client';

import { useState } from 'react';

const CONTENT_TYPES = [
  { id: 'social_post', label: 'Social Media Post', icon: '📱' },
  { id: 'client_message', label: 'Client Message', icon: '💬' },
  { id: 'newsletter', label: 'Newsletter', icon: '📰' },
];

export default function ContentPage() {
  const [contentType, setContentType] = useState('social_post');
  const [topic, setTopic] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  async function generate() {
    if (!topic.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content_type: contentType, topic, context: topic, client_name: topic }),
      });
      const data = await res.json();
      setResult(data.content || data.error || 'No content generated');
    } catch {
      setResult('Error connecting to backend');
    }
    setLoading(false);
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-brand-deep-teal">Content Generator</h2>

      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <div className="flex gap-3">
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
          placeholder={contentType === 'client_message' ? 'Client name + context...' : 'Topic or theme...'}
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

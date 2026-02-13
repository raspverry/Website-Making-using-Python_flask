'use client';
import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';

export default function AgentPage({ params }: { params: Promise<{ uid: string }> }) {
  const { uid } = use(params);
  const router = useRouter();
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<{text: string; isUser: boolean}[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    api.setToken(token);
  }, [router]);

  const handleAsk = async (q: string) => {
    if (!q.trim() || loading) return;
    setMessages(prev => [...prev, { text: q, isUser: true }]);
    setQuestion('');
    setLoading(true);

    try {
      const data = await api.askAgent(uid, q);
      setMessages(prev => [...prev, { text: data.answer, isUser: false }]);
    } catch {
      setMessages(prev => [...prev, { text: 'Failed to get response. Make sure you have run a scan first.', isUser: false }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 text-sm text-gray-500 mb-6">
        <Link href="/dashboard" className="hover:text-gray-700">Dashboard</Link>
        <span>/</span>
        <Link href={`/dashboard/sites/${uid}`} className="hover:text-gray-700">Site</Link>
        <span>/</span>
        <span className="text-gray-900">AI Agent</span>
      </div>

      <h1 className="text-2xl font-bold text-gray-900 mb-6">AI Accessibility Agent</h1>

      <div aria-live="polite" className="bg-white rounded-xl border border-gray-200 p-6 mb-4 min-h-[400px] max-h-[500px] overflow-y-auto space-y-3">
        {messages.length === 0 && (
          <p className="text-gray-400 text-center py-10">Ask a question about your site&apos;s accessibility issues.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${m.isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'} whitespace-pre-line`}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2 text-sm text-gray-500 animate-pulse">Thinking...</div>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <label htmlFor="agent-question" className="sr-only">Ask a question about your site&apos;s accessibility</label>
        <input
          id="agent-question"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAsk(question)}
          placeholder="e.g., What should I fix first?"
          disabled={loading}
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
        />
        <button onClick={() => handleAsk(question)} disabled={loading} className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50">
          Ask
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {['What should I fix first?', 'How do I improve my score?', 'Explain my critical violations'].map((q) => (
          <button key={q} onClick={() => handleAsk(q)} disabled={loading} className="text-xs bg-gray-100 text-gray-600 px-3 py-1.5 rounded-full hover:bg-gray-200 transition disabled:opacity-50">
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

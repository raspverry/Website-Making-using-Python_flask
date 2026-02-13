'use client';
import { useState, use } from 'react';

export default function AgentPage({ params }: { params: Promise<{ uid: string }> }) {
  const { uid } = use(params);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<{text: string; isUser: boolean}[]>([]);

  const handleAsk = async (q: string) => {
    if (!q.trim()) return;
    setMessages(prev => [...prev, { text: q, isUser: true }]);
    setQuestion('');
    
    try {
      const res = await fetch(`/api/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ siteUid: uid, question: q }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { text: data.answer || 'No response', isUser: false }]);
    } catch {
      setMessages(prev => [...prev, { text: 'Failed to get response.', isUser: false }]);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">AI Accessibility Agent</h1>
      
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4 min-h-[400px] max-h-[500px] overflow-y-auto space-y-3">
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
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAsk(question)}
          placeholder="e.g., What should I fix first?"
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button onClick={() => handleAsk(question)} className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition">
          Ask
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {['What should I fix first?', 'How do I improve my score?', 'What are the ADA penalties?'].map((q) => (
          <button key={q} onClick={() => handleAsk(q)} className="text-xs bg-gray-100 text-gray-600 px-3 py-1.5 rounded-full hover:bg-gray-200 transition">
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

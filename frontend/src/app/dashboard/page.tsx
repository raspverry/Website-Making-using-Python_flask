'use client';
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { ScoreCircle } from '@/components/ScoreCircle';
import type { Site } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [newName, setNewName] = useState('');
  const [addError, setAddError] = useState('');
  const [adding, setAdding] = useState(false);

  const loadSites = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) { router.push('/login'); return; }
      api.setToken(token);
      const data = await api.getSites();
      setSites(data);
    } catch {
      router.push('/login');
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => { loadSites(); }, [loadSites]);

  const handleAddSite = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddError('');
    setAdding(true);
    try {
      await api.createSite(newUrl, newName);
      setShowAdd(false);
      setNewUrl('');
      setNewName('');
      await loadSites();
    } catch (err) {
      setAddError(err instanceof Error ? err.message : 'Failed to add site');
    } finally {
      setAdding(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-48"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">My Websites</h1>
        <button onClick={() => setShowAdd(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition">
          Add Website
        </button>
      </div>

      {showAdd && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Add a Website</h2>
          {addError && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{addError}</div>}
          <form onSubmit={handleAddSite} className="flex gap-3">
            <input type="url" value={newUrl} onChange={(e) => setNewUrl(e.target.value)} required placeholder="https://example.com" className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
            <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Site name (optional)" className="w-48 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
            <button type="submit" disabled={adding} className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50">{adding ? 'Adding...' : 'Add'}</button>
            <button type="button" onClick={() => setShowAdd(false)} className="text-gray-500 px-4 py-2.5 rounded-lg text-sm hover:bg-gray-100">Cancel</button>
          </form>
        </div>
      )}

      {sites.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <p className="text-gray-500">No websites added yet. Add your first website to start scanning.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {sites.map((site) => (
            <Link key={site.uid} href={`/dashboard/sites/${site.uid}`} className="block bg-white rounded-xl border border-gray-200 p-6 hover:border-blue-300 hover:shadow-sm transition">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{site.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{site.url}</p>
                  {site.last_scan_at && (
                    <p className="text-xs text-gray-400 mt-1">Last scan: {new Date(site.last_scan_at).toLocaleDateString()}</p>
                  )}
                </div>
                <div className="flex items-center gap-4">
                  {site.compliance_score !== null ? (
                    <ScoreCircle score={site.compliance_score} />
                  ) : (
                    <span className="text-sm text-gray-400">Not scanned</span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

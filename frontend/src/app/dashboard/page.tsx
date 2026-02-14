'use client';
import { Suspense, useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { ScoreCircle } from '@/components/ScoreCircle';
import type { Site } from '@/types';

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded-lg w-48" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-44 bg-gray-100 rounded-xl border border-gray-200" />
            ))}
          </div>
        </div>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [newName, setNewName] = useState('');
  const [addError, setAddError] = useState('');
  const [adding, setAdding] = useState(false);
  const [userName, setUserName] = useState('');
  const [userPlan, setUserPlan] = useState('free');
  const [checkoutSuccess, setCheckoutSuccess] = useState(false);
  const [usage, setUsage] = useState<{
    plan: string;
    scans_used: number; scans_limit: number;
    sites_used: number; sites_limit: number;
    next_scheduled_scan: string | null;
  } | null>(null);

  const refreshUserData = useCallback(async () => {
    try {
      const sub = await api.getSubscription();
      const stored = localStorage.getItem('user');
      if (stored) {
        const user = JSON.parse(stored);
        user.plan = sub.plan;
        localStorage.setItem('user', JSON.stringify(user));
      }
    } catch {
      // Subscription fetch failed, keep existing data
    }
  }, []);

  const loadSites = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) { router.push('/login'); return; }
      api.setToken(token);
      const stored = localStorage.getItem('user');
      if (stored) {
        try { setUserName(JSON.parse(stored).name); } catch { /* ignore */ }
      }

      // Handle Stripe checkout success
      if (searchParams.get('checkout') === 'success') {
        setCheckoutSuccess(true);
        await refreshUserData();
        // Clean up URL
        window.history.replaceState({}, '', '/dashboard');
      }

      const data = await api.getSites();
      setSites(data);

      // Load usage data
      try {
        const usageData = await api.getUsage();
        setUsage(usageData);
        setUserPlan(usageData.plan);
      } catch {
        // Usage endpoint may fail for new accounts
      }
    } catch {
      router.push('/login');
    } finally {
      setLoading(false);
    }
  }, [router, searchParams, refreshUserData]);

  useEffect(() => { loadSites(); }, [loadSites]);

  const handleAddSite = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddError('');
    setAdding(true);
    try {
      const site = await api.createSite(newUrl, newName);
      setShowAdd(false);
      setNewUrl('');
      setNewName('');
      // Auto-scan: trigger scan then navigate to site detail
      try {
        await api.startScan(site.uid);
      } catch {
        // Scan may fail (e.g., plan limit) — still navigate to the site
      }
      router.push(`/dashboard/sites/${site.uid}`);
    } catch (err) {
      setAddError(err instanceof Error ? err.message : 'Failed to add site');
    } finally {
      setAdding(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded-lg w-48" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-44 bg-gray-100 rounded-xl border border-gray-200" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {userName ? `Welcome back, ${userName}` : 'My Websites'}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {sites.length === 0
              ? 'Add your first website to get started'
              : `${sites.length} site${sites.length !== 1 ? 's' : ''} monitored`}
          </p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="inline-flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-blue-700 shadow-sm hover:shadow transition-all duration-200"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Website
        </button>
      </div>

      {/* Checkout Success Banner */}
      {checkoutSuccess && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex items-center gap-3">
          <svg className="w-5 h-5 text-green-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <p className="text-sm text-green-800 font-medium">
            Plan upgraded successfully! Your new features are now active.
          </p>
          <button onClick={() => setCheckoutSuccess(false)} className="ml-auto text-green-600 hover:text-green-800" aria-label="Dismiss">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Plan Usage Bar */}
      {usage && (
        <div className="mb-6 bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex flex-wrap items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-gray-500">Plan:</span>
              <span className="font-semibold text-gray-900 capitalize">{usage.plan === 'free' ? 'Free' : usage.plan}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-500">Sites:</span>
              <span className={`font-semibold ${usage.sites_used >= usage.sites_limit ? 'text-red-600' : 'text-gray-900'}`}>
                {usage.sites_used}/{usage.sites_limit}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-500">Scans this month:</span>
              <span className={`font-semibold ${usage.scans_limit !== -1 && usage.scans_used >= usage.scans_limit ? 'text-red-600' : 'text-gray-900'}`}>
                {usage.scans_used}/{usage.scans_limit === -1 ? 'Unlimited' : usage.scans_limit}
              </span>
            </div>
            {usage.next_scheduled_scan && (
              <div className="flex items-center gap-2">
                <span className="text-gray-500">Next auto-scan:</span>
                <span className="font-semibold text-gray-900">
                  {new Date(usage.next_scheduled_scan).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            )}
            {userPlan === 'free' && (
              <Link href="/pricing" className="ml-auto text-sm font-semibold text-blue-600 hover:text-blue-700">
                Upgrade for more scans &rarr;
              </Link>
            )}
          </div>
          {/* Progress bar for scan usage */}
          {usage.scans_limit > 0 && (
            <div className="mt-3 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${usage.scans_used >= usage.scans_limit ? 'bg-red-500' : 'bg-blue-500'}`}
                style={{ width: `${Math.min((usage.scans_used / usage.scans_limit) * 100, 100)}%` }}
              />
            </div>
          )}
        </div>
      )}

      {/* Add Website Form */}
      {showAdd && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Add a Website</h2>
          <p className="text-sm text-gray-500 mb-5">Enter the URL and we&apos;ll automatically check for accessibility issues.</p>
          {addError && (
            <div role="alert" className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-center gap-2">
              <svg className="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
              {addError}
            </div>
          )}
          <form onSubmit={handleAddSite} className="flex flex-col sm:flex-row gap-3 items-end">
            <div className="flex-1 min-w-0 w-full">
              <label htmlFor="site-url" className="block text-sm font-medium text-gray-700 mb-1">Website URL</label>
              <input
                id="site-url"
                type="url"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                required
                placeholder="https://example.com"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
              />
            </div>
            <div className="w-full sm:w-48">
              <label htmlFor="site-name" className="block text-sm font-medium text-gray-700 mb-1">
                Site name <span className="text-gray-400 font-normal">(optional)</span>
              </label>
              <input
                id="site-name"
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="My Website"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" disabled={adding} className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50">
                {adding ? 'Adding...' : 'Add Site'}
              </button>
              <button type="button" onClick={() => { setShowAdd(false); setAddError(''); }} className="text-gray-500 px-4 py-2.5 rounded-lg text-sm hover:bg-gray-100 transition-colors">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Sites Grid */}
      {sites.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-16 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">No websites yet</h3>
          <p className="text-sm text-gray-500 mb-6 max-w-sm mx-auto">
            Add your first website to scan it for WCAG 2.2 accessibility issues and get AI-powered fix suggestions.
          </p>
          <button
            onClick={() => setShowAdd(true)}
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-blue-700 shadow-sm transition-all duration-200"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Your First Website
          </button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sites.map((site) => (
            <Link
              key={site.uid}
              href={`/dashboard/sites/${site.uid}`}
              className="card-hover block bg-white rounded-xl border border-gray-200 p-6 hover:border-blue-200 group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="min-w-0 flex-1 mr-3">
                  <h3 className="text-base font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                    {site.name}
                  </h3>
                  <p className="text-sm text-gray-500 truncate mt-0.5">{site.url}</p>
                </div>
                {site.compliance_score !== null ? (
                  <ScoreCircle score={site.compliance_score} size="sm" />
                ) : (
                  <div className="w-14 h-14 rounded-full border-2 border-dashed border-gray-200 flex items-center justify-center">
                    <span className="text-[10px] text-gray-400 font-medium">N/A</span>
                  </div>
                )}
              </div>
              <div className="flex items-center justify-between">
                {site.last_scan_at ? (
                  <p className="text-xs text-gray-400">
                    Scanned {new Date(site.last_scan_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </p>
                ) : (
                  <p className="text-xs text-gray-400">Not scanned yet</p>
                )}
                <span className="text-xs text-blue-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  View details &rarr;
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

'use client';
import { useState, useEffect, useCallback, useRef, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { ScoreCircle } from '@/components/ScoreCircle';
import { ViolationCard } from '@/components/ViolationCard';
import type { Site, Scan, Violation } from '@/types';

type SeverityFilter = 'all' | 'critical' | 'serious' | 'moderate' | 'minor';

export default function SiteDetailPage({ params }: { params: Promise<{ uid: string }> }) {
  const { uid } = use(params);
  const router = useRouter();
  const [site, setSite] = useState<Site | null>(null);
  const [scan, setScan] = useState<Scan | null>(null);
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<SeverityFilter>('all');
  const [deleting, setDeleting] = useState(false);
  const [userPlan, setUserPlan] = useState('free');
  const [maxPages, setMaxPages] = useState(5);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const startPolling = useCallback(() => {
    stopPolling();
    pollRef.current = setInterval(async () => {
      try {
        const data = await api.getLatestScan(uid);
        if (data.scan.status === 'completed' || data.scan.status === 'failed') {
          stopPolling();
          setScan(data.scan);
          setViolations(data.violations);
          setScanning(false);
          setSite(prev => prev ? { ...prev, compliance_score: data.scan.score } : prev);
        }
      } catch {
        // Keep polling on transient errors
      }
    }, 3000);
  }, [uid, stopPolling]);

  useEffect(() => stopPolling, [stopPolling]);

  const loadData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) { router.push('/login'); return; }
      api.setToken(token);

      const siteData = await api.getSite(uid);
      setSite(siteData);

      // Get user plan info for upsell/PDF logic
      try {
        const usageData = await api.getUsage();
        setUserPlan(usageData.plan);
        setMaxPages(usageData.max_pages);
      } catch { /* Usage may fail */ }

      try {
        const scanData = await api.getLatestScan(uid);
        setScan(scanData.scan);
        setViolations(scanData.violations);
        if (scanData.scan.status === 'pending' || scanData.scan.status === 'running') {
          setScanning(true);
          startPolling();
        }
      } catch {
        // No scan yet
      }
    } catch {
      setError('Failed to load site data');
    } finally {
      setLoading(false);
    }
  }, [uid, router, startPolling]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleScan = async () => {
    setScanning(true);
    setError('');
    try {
      const result = await api.startScan(uid);
      setScan(result.scan);
      setViolations([]);
      startPolling();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed');
      setScanning(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this site? All scan data will be permanently removed.')) return;
    setDeleting(true);
    try {
      await api.deleteSite(uid);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete site');
      setDeleting(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      const blob = await api.downloadReport(uid);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pageguard-report-${uid}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download report');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const filtered = filter === 'all' ? violations : violations.filter((v) => v.severity === filter);

  const severityCounts = {
    critical: violations.filter((v) => v.severity === 'critical').length,
    serious: violations.filter((v) => v.severity === 'serious').length,
    moderate: violations.filter((v) => v.severity === 'moderate').length,
    minor: violations.filter((v) => v.severity === 'minor').length,
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="animate-pulse space-y-6">
          <div className="h-5 bg-gray-200 rounded w-40" />
          <div className="h-8 bg-gray-200 rounded w-64" />
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-28 bg-gray-100 rounded-xl border border-gray-200" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!site) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-lg font-semibold text-gray-900 mb-1">Site not found</h2>
        <p className="text-sm text-gray-500 mb-4">This site may have been deleted or doesn&apos;t exist.</p>
        <Link href="/dashboard" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
          &larr; Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1.5 text-sm text-gray-500 mb-6" aria-label="Breadcrumb">
        <Link href="/dashboard" className="hover:text-gray-700 transition-colors">Dashboard</Link>
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
        <span className="text-gray-900 font-medium">{site.name}</span>
      </nav>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{site.name}</h1>
          <p className="text-sm text-gray-500 mt-1">{site.url}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            href={`/dashboard/sites/${uid}/agent`}
            className="inline-flex items-center gap-1.5 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 hover:border-gray-400 transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            AI Agent
          </Link>
          {scan && scan.status === 'completed' && (userPlan === 'pro' || userPlan === 'agency') && (
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf}
              className="inline-flex items-center gap-1.5 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 hover:border-gray-400 transition-all disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {downloadingPdf ? 'Downloading...' : 'PDF Report'}
            </button>
          )}
          <button
            onClick={handleScan}
            disabled={scanning}
            className="inline-flex items-center gap-1.5 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 shadow-sm transition-all disabled:opacity-50"
          >
            {scanning ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Scanning...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Run Scan
              </>
            )}
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="text-gray-400 hover:text-red-600 p-2 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
            aria-label="Delete site"
            title="Delete site"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {error && (
        <div role="alert" className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex items-center gap-2">
          <svg className="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
          {error}
        </div>
      )}

      {scan ? (
        <>
          {/* SPA / Scanner Warning */}
          {scan.warnings && (() => {
            try {
              const warnings: string[] = JSON.parse(scan.warnings);
              return warnings.length > 0 ? (
                <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-800 flex gap-2">
                  <svg className="w-5 h-5 shrink-0 text-amber-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <div>
                    <p className="font-medium mb-1">Scan notice</p>
                    {warnings.map((w, i) => <p key={i}>{w}</p>)}
                  </div>
                </div>
              ) : null;
            } catch { return null; }
          })()}

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col items-center justify-center col-span-2 md:col-span-1">
              <ScoreCircle score={scan.score ?? 0} />
              <p className="text-xs text-gray-500 mt-2 font-medium">Compliance Score</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
              <p className="text-3xl font-bold text-gray-900">{scan.total_violations}</p>
              <p className="text-xs text-gray-500 mt-1">Total Issues</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
              <p className="text-3xl font-bold text-red-600">{scan.critical_count}</p>
              <p className="text-xs text-gray-500 mt-1">Critical</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
              <p className="text-3xl font-bold text-orange-500">{scan.serious_count}</p>
              <p className="text-xs text-gray-500 mt-1">Serious</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
              <p className="text-3xl font-bold text-yellow-500">{scan.moderate_count + scan.minor_count}</p>
              <p className="text-xs text-gray-500 mt-1">Moderate/Minor</p>
            </div>
          </div>

          {/* Scan Info */}
          <div className="flex flex-wrap items-center gap-4 mb-6 text-sm text-gray-500">
            <span>{scan.pages_scanned} page{scan.pages_scanned !== 1 ? 's' : ''} scanned</span>
            {scan.completed_at && (
              <>
                <span className="w-1 h-1 rounded-full bg-gray-300" />
                <span>
                  {new Date(scan.completed_at).toLocaleDateString('en-US', {
                    month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit',
                  })}
                </span>
              </>
            )}
          </div>

          {/* Upsell Banner for Free Users */}
          {userPlan === 'free' && scan.status === 'completed' && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-blue-900">
                    This scan analyzed {scan.pages_scanned} page{scan.pages_scanned !== 1 ? 's' : ''} (Free plan limit: {maxPages})
                  </p>
                  <p className="text-sm text-blue-700 mt-0.5">
                    Your site may have additional pages with accessibility issues. Upgrade to scan up to 50 pages with weekly auto-scans and AI fix suggestions.
                  </p>
                </div>
                <Link
                  href="/pricing"
                  className="inline-flex items-center gap-1.5 bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-all shrink-0"
                >
                  Upgrade to Starter — $29/mo
                </Link>
              </div>
            </div>
          )}

          {/* PDF Upsell for Starter Users */}
          {userPlan === 'starter' && scan.status === 'completed' && (
            <div className="mb-6 p-3 bg-gray-50 border border-gray-200 rounded-xl flex items-center gap-3">
              <svg className="w-5 h-5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-sm text-gray-600 flex-1">
                Need a PDF compliance report for stakeholders? <Link href="/pricing" className="text-blue-600 font-medium hover:underline">Upgrade to Pro ($79/mo)</Link> to download professional reports.
              </p>
            </div>
          )}

          {/* Next Scheduled Scan */}
          {site.next_scan_at && scan.status === 'completed' && (
            <div className="mb-6 flex items-center gap-2 text-sm text-gray-500">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Next automatic scan: {new Date(site.next_scan_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
            </div>
          )}

          {/* Violations */}
          {violations.length > 0 && (
            <div>
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Violations ({filtered.length}{filter !== 'all' ? ` ${filter}` : ''})
                </h2>
                <div className="flex flex-wrap gap-1.5" role="radiogroup" aria-label="Filter violations by severity">
                  {(['all', 'critical', 'serious', 'moderate', 'minor'] as const).map((f) => {
                    const count = f === 'all' ? violations.length : severityCounts[f];
                    const isActive = filter === f;
                    return (
                      <button
                        key={f}
                        onClick={() => setFilter(f)}
                        role="radio"
                        aria-checked={isActive}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                          isActive
                            ? 'bg-gray-900 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        {f} ({count})
                      </button>
                    );
                  })}
                </div>
              </div>
              <div className="space-y-3">
                {filtered.map((v, i) => (
                  <ViolationCard key={i} violation={v} />
                ))}
                {filtered.length === 0 && (
                  <p className="text-sm text-gray-400 text-center py-8">No {filter} violations found.</p>
                )}
              </div>
            </div>
          )}

          {violations.length === 0 && scan.status === 'completed' && (
            <div className="bg-green-50 rounded-xl border border-green-200 p-12 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-green-900 mb-1">No automated violations found</h3>
              <p className="text-sm text-green-700">Our scanner found no issues in the server-rendered HTML. Note that automated tools detect ~30% of all accessibility issues. We recommend combining with manual testing.</p>
            </div>
          )}

          {/* Disclaimer */}
          {scan.status === 'completed' && (
            <div className="mt-8 p-4 bg-gray-50 rounded-xl border border-gray-200 text-xs text-gray-500 leading-relaxed">
              <p>
                <strong>Disclaimer:</strong> This scan checks server-rendered HTML for 13 common WCAG 2.2 Level AA violations.
                Automated tools detect approximately 30% of all accessibility issues. A passing score does not guarantee
                legal compliance with ADA, Section 508, or other regulations. This is not legal advice.{' '}
                <a href="/disclaimer" className="text-blue-600 hover:underline">Read full disclaimer</a>.
              </p>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-16 text-center">
          <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">Ready to scan</h3>
          <p className="text-sm text-gray-500 mb-6 max-w-sm mx-auto">
            Run your first scan to check this website for WCAG 2.2 Level AA accessibility compliance.
          </p>
          <button
            onClick={handleScan}
            disabled={scanning}
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-blue-700 shadow-sm transition-all disabled:opacity-50"
          >
            {scanning ? 'Scanning...' : 'Start First Scan'}
          </button>
        </div>
      )}
    </div>
  );
}

'use client';
import { useState, useEffect, useCallback, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { ScoreCircle } from '@/components/ScoreCircle';
import { ViolationCard } from '@/components/ViolationCard';
import type { Site, Scan, Violation } from '@/types';

export default function SiteDetailPage({ params }: { params: Promise<{ uid: string }> }) {
  const { uid } = use(params);
  const router = useRouter();
  const [site, setSite] = useState<Site | null>(null);
  const [scan, setScan] = useState<Scan | null>(null);
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState('');

  const loadData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) { router.push('/login'); return; }
      api.setToken(token);

      const siteData = await api.getSite(uid);
      setSite(siteData);

      try {
        const scanData = await api.getLatestScan(uid);
        setScan(scanData.scan);
        setViolations(scanData.violations);
      } catch {
        // No scan yet - that's OK
      }
    } catch {
      setError('Failed to load site data');
    } finally {
      setLoading(false);
    }
  }, [uid, router]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleScan = async () => {
    setScanning(true);
    setError('');
    try {
      const result = await api.startScan(uid);
      setScan(result.scan);
      setViolations(result.violations);
      if (site) setSite({ ...site, compliance_score: result.scan.score });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed');
    } finally {
      setScanning(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-64"></div>
          <div className="h-48 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!site) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="text-red-600">Site not found</p>
        <Link href="/dashboard" className="text-blue-600 hover:underline mt-2 inline-block">Back to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-2 text-sm text-gray-500 mb-6">
        <Link href="/dashboard" className="hover:text-gray-700">Dashboard</Link>
        <span>/</span>
        <span className="text-gray-900">{site.name}</span>
      </div>

      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{site.name}</h1>
          <p className="text-sm text-gray-500 mt-1">{site.url}</p>
        </div>
        <div className="flex gap-3">
          <Link href={`/dashboard/sites/${uid}/agent`} className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition">
            AI Agent
          </Link>
          <button onClick={handleScan} disabled={scanning} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50">
            {scanning ? 'Scanning...' : 'Run Scan'}
          </button>
        </div>
      </div>

      {error && <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>}

      {scan ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-white rounded-xl border border-gray-200 p-4 flex flex-col items-center">
              <ScoreCircle score={scan.score ?? 0} />
              <p className="text-xs text-gray-500 mt-2">Compliance Score</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
              <p className="text-3xl font-bold text-gray-900">{scan.total_violations}</p>
              <p className="text-xs text-gray-500 mt-1">Total Issues</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
              <p className="text-3xl font-bold text-red-600">{scan.critical_count}</p>
              <p className="text-xs text-gray-500 mt-1">Critical</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
              <p className="text-3xl font-bold text-orange-500">{scan.serious_count}</p>
              <p className="text-xs text-gray-500 mt-1">Serious</p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
              <p className="text-3xl font-bold text-yellow-500">{scan.moderate_count + scan.minor_count}</p>
              <p className="text-xs text-gray-500 mt-1">Moderate/Minor</p>
            </div>
          </div>

          {violations.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Violations ({violations.length})</h2>
              <div className="space-y-3">
                {violations.map((v, i) => (
                  <ViolationCard key={i} violation={v} />
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <p className="text-gray-500 mb-4">No scan results yet. Run your first scan to check accessibility compliance.</p>
          <button onClick={handleScan} disabled={scanning} className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50">
            {scanning ? 'Scanning...' : 'Scan Now'}
          </button>
        </div>
      )}
    </div>
  );
}

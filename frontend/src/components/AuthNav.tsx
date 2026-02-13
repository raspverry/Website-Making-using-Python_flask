'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export function AuthNav() {
  const router = useRouter();
  const [user, setUser] = useState<{ name: string; plan: string } | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem('user');
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch { /* ignore */ }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    router.push('/');
  };

  if (user) {
    return (
      <div className="flex items-center gap-1 sm:gap-2">
        <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors">
          Dashboard
        </Link>
        <div className="hidden sm:block h-5 w-px bg-gray-200" />
        <span className="hidden sm:inline text-sm text-gray-500 px-2">{user.name}</span>
        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-blue-50 text-blue-700 capitalize">
          {user.plan}
        </span>
        <button
          onClick={handleLogout}
          className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors"
        >
          Log out
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1 sm:gap-2">
      <Link href="/pricing" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors">
        Pricing
      </Link>
      <Link href="/login" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors">
        Log in
      </Link>
      <Link
        href="/signup"
        className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 shadow-sm hover:shadow transition-all duration-200"
      >
        Free Scan
      </Link>
    </div>
  );
}

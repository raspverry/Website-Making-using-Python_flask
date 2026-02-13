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
      <div className="flex items-center space-x-4">
        <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 text-sm font-medium">Dashboard</Link>
        <span className="text-sm text-gray-500">{user.name}</span>
        <button onClick={handleLogout} className="text-gray-600 hover:text-gray-900 text-sm font-medium">Logout</button>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-4">
      <Link href="/pricing" className="text-gray-600 hover:text-gray-900 text-sm font-medium">Pricing</Link>
      <Link href="/login" className="text-gray-600 hover:text-gray-900 text-sm font-medium">Log in</Link>
      <Link href="/signup" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition">
        Scan Free
      </Link>
    </div>
  );
}

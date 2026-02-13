'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

interface PricingCardProps {
  name: string;
  price: string;
  period: string;
  features: string[];
  cta: string;
  highlighted?: boolean;
}

export function PricingCard({ name, price, period, features, cta, highlighted }: PricingCardProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    if (name === 'Free') {
      router.push('/signup');
      return;
    }

    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (!token) {
      router.push('/signup');
      return;
    }

    setLoading(true);
    try {
      api.setToken(token);
      const data = await api.createCheckout(name.toLowerCase());
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch {
      router.push('/signup');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`relative rounded-2xl p-8 transition-all duration-200 ${
      highlighted
        ? 'bg-blue-600 text-white ring-4 ring-blue-600 ring-offset-2 shadow-xl shadow-blue-200/50 scale-[1.02]'
        : 'bg-white border border-gray-200 hover:border-gray-300 hover:shadow-sm'
    }`}>
      {highlighted && (
        <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
          <span className="bg-gradient-to-r from-amber-400 to-amber-500 text-amber-950 text-xs font-bold px-3 py-1 rounded-full shadow-sm">
            Most Popular
          </span>
        </div>
      )}
      <h3 className={`text-lg font-semibold ${highlighted ? 'text-white' : 'text-gray-900'}`}>{name}</h3>
      <div className="mt-4 flex items-baseline">
        <span className="text-4xl font-bold tracking-tight">{price}</span>
        <span className={`ml-1 text-sm ${highlighted ? 'text-blue-200' : 'text-gray-500'}`}>{period}</span>
      </div>
      <ul className="mt-6 space-y-3">
        {features.map((f, i) => (
          <li key={i} className={`flex items-start gap-2.5 text-sm ${highlighted ? 'text-blue-100' : 'text-gray-600'}`}>
            <svg className={`w-4 h-4 mt-0.5 shrink-0 ${highlighted ? 'text-blue-200' : 'text-blue-500'}`} fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            {f}
          </li>
        ))}
      </ul>
      <button
        onClick={handleClick}
        disabled={loading}
        className={`mt-8 w-full py-3 rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 ${
          highlighted
            ? 'bg-white text-blue-600 hover:bg-blue-50 shadow-sm'
            : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
        }`}
      >
        {loading ? 'Loading...' : cta}
      </button>
    </div>
  );
}

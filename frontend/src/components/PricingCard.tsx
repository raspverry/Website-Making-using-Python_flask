'use client';

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

    try {
      api.setToken(token);
      const data = await api.createCheckout(name.toLowerCase());
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (err) {
      // If not logged in or error, redirect to signup
      router.push('/signup');
    }
  };

  return (
    <div className={`rounded-2xl p-8 ${highlighted ? 'bg-blue-600 text-white ring-4 ring-blue-600 ring-offset-2' : 'bg-white border border-gray-200'}`}>
      <h3 className={`text-lg font-semibold ${highlighted ? 'text-white' : 'text-gray-900'}`}>{name}</h3>
      <div className="mt-4 flex items-baseline">
        <span className="text-4xl font-bold">{price}</span>
        <span className={`ml-1 text-sm ${highlighted ? 'text-blue-200' : 'text-gray-500'}`}>{period}</span>
      </div>
      <ul className="mt-6 space-y-3">
        {features.map((f, i) => (
          <li key={i} className={`flex items-center text-sm ${highlighted ? 'text-blue-100' : 'text-gray-600'}`}>
            <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>
            {f}
          </li>
        ))}
      </ul>
      <button
        onClick={handleClick}
        className={`mt-8 w-full py-3 rounded-lg font-medium transition ${highlighted ? 'bg-white text-blue-600 hover:bg-blue-50' : 'bg-blue-600 text-white hover:bg-blue-700'}`}
      >
        {cta}
      </button>
    </div>
  );
}

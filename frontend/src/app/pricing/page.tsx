import { PricingCard } from '@/components/PricingCard';
import Link from 'next/link';

export default function PricingPage() {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: '/month',
      features: ['1 website', '1 scan per month', 'Basic report', '5 pages max'],
      cta: 'Start Free',
    },
    {
      name: 'Starter',
      price: '$29',
      period: '/month',
      features: ['1 website', 'Weekly scans', 'AI fix suggestions', 'Email alerts', 'Full report', '50 pages per scan'],
      cta: 'Get Started',
    },
    {
      name: 'Pro',
      price: '$79',
      period: '/month',
      features: ['5 websites', 'Daily scans', 'PDF compliance reports', 'Compliance badge', 'Priority support', '50 pages per scan'],
      cta: 'Go Pro',
      highlighted: true,
    },
    {
      name: 'Agency',
      price: '$199',
      period: '/month',
      features: ['20 websites', 'Daily scans', 'White-label reports', 'Team access', 'REST API access', 'Client portal', '100 pages per scan'],
      cta: 'Contact Sales',
    },
  ];

  return (
    <div className="py-20 sm:py-28">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <p className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-3">Pricing</p>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">Simple, transparent pricing</h1>
          <p className="mt-4 text-lg text-gray-500 max-w-2xl mx-auto">
            Start with a free scan. Upgrade when you need more sites, more scans, or AI-powered fix suggestions.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <PricingCard key={plan.name} {...plan} />
          ))}
        </div>

        {/* FAQ */}
        <div className="mt-20 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">Common Questions</h2>
          <div className="space-y-3">
            {[
              { q: 'Can I cancel anytime?', a: 'Yes. No contracts, no cancellation fees. Downgrade or cancel your plan at any time from the billing portal.' },
              { q: 'What payment methods do you accept?', a: 'We accept all major credit cards through Stripe. Your payment is secure and PCI-compliant.' },
              { q: 'Do I need a credit card for the free plan?', a: 'No. The free plan is completely free — no credit card required. You can upgrade anytime.' },
              { q: 'Can I switch plans later?', a: 'Absolutely. Upgrade or downgrade anytime. Changes take effect immediately.' },
            ].map((faq) => (
              <details key={faq.q} className="group bg-white rounded-xl border border-gray-200 hover:border-gray-300 transition-colors">
                <summary className="flex items-center justify-between cursor-pointer px-6 py-4 text-left">
                  <span className="text-sm font-medium text-gray-900 pr-4">{faq.q}</span>
                  <svg className="w-4 h-4 text-gray-400 shrink-0 group-open:rotate-180 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                <div className="px-6 pb-4 text-sm text-gray-500 leading-relaxed">{faq.a}</div>
              </details>
            ))}
          </div>
        </div>

        <div className="mt-16 text-center">
          <p className="text-sm text-gray-500">
            Not sure which plan is right for you?{' '}
            <Link href="/signup" className="text-blue-600 hover:text-blue-700 font-medium">
              Start with a free scan
            </Link>{' '}
            and decide later.
          </p>
        </div>
      </div>
    </div>
  );
}

import { PricingCard } from '@/components/PricingCard';

export default function PricingPage() {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: '/month',
      features: ['1 website', '1 scan', 'Basic report', '5 pages max'],
      cta: 'Start Free',
    },
    {
      name: 'Starter',
      price: '$29',
      period: '/month',
      features: ['1 website', 'Weekly scans', 'AI fix suggestions', 'Email alerts', 'Full report'],
      cta: 'Get Started',
    },
    {
      name: 'Pro',
      price: '$79',
      period: '/month',
      features: ['5 websites', 'Daily scans', 'PDF reports', 'Compliance badge', 'Priority support'],
      cta: 'Go Pro',
      highlighted: true,
    },
    {
      name: 'Agency',
      price: '$199',
      period: '/month',
      features: ['20 websites', 'Unlimited scans', 'White-label', 'Team access', 'API access', 'Client portal'],
      cta: 'Contact Sales',
    },
  ];

  return (
    <div className="py-20">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900">Simple, transparent pricing</h1>
          <p className="mt-4 text-xl text-gray-600">Choose the plan that fits your needs. No hidden fees.</p>
        </div>
        <div className="grid md:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <PricingCard key={plan.name} {...plan} />
          ))}
        </div>
      </div>
    </div>
  );
}

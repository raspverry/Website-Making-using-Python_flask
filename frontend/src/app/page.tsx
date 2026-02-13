import { CountdownTimer } from '@/components/CountdownTimer';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="bg-gradient-to-b from-red-50 to-white py-20">
        <div className="max-w-5xl mx-auto px-4 text-center">
          <div className="inline-flex items-center bg-red-100 text-red-800 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            ADA Title II Deadline: April 24, 2026
          </div>
          <h1 className="text-5xl md:text-6xl font-black text-gray-900 leading-tight">
            Is Your Website<br />
            <span className="text-red-600">ADA Compliant?</span>
          </h1>
          <p className="mt-6 text-xl text-gray-600 max-w-2xl mx-auto">
            Non-compliance penalties up to $150,000 per violation.
            95.9% of websites fail. Scan yours in 30 seconds.
          </p>

          <div className="mt-10">
            <CountdownTimer />
          </div>

          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup" className="bg-red-600 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-red-700 transition shadow-lg shadow-red-200">
              Scan Your Website Free
            </Link>
            <Link href="/pricing" className="bg-white text-gray-700 px-8 py-4 rounded-xl text-lg font-medium border border-gray-300 hover:border-gray-400 transition">
              View Pricing
            </Link>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">How PageGuard Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '1', title: 'Enter Your URL', desc: 'Paste your website address. No technical knowledge needed.' },
              { step: '2', title: 'AI Scans for Issues', desc: 'We check every page against WCAG 2.2 Level AA standards.' },
              { step: '3', title: 'Get Fix Suggestions', desc: 'AI generates exact code fixes you can copy and paste.' },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto">
                  {item.step}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">{item.title}</h3>
                <p className="mt-2 text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gray-900 py-16">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white">Don&apos;t Wait Until It&apos;s Too Late</h2>
          <p className="mt-4 text-gray-400 text-lg">
            The ADA deadline is real. The lawsuits are real. Protect your business today.
          </p>
          <Link href="/signup" className="mt-8 inline-block bg-red-600 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-red-700 transition">
            Start Free Scan Now
          </Link>
        </div>
      </section>
    </div>
  );
}

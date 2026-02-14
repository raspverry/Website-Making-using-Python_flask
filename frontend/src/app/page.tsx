import { CountdownTimer } from '@/components/CountdownTimer';
import Link from 'next/link';

const features = [
  {
    title: 'WCAG 2.2 Level AA',
    desc: '13 automated checks covering images, forms, contrast, navigation, ARIA, and more.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
  },
  {
    title: 'AI Fix Suggestions',
    desc: 'Not just "you have a problem" — get exact code snippets to copy, paste, and fix.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  },
  {
    title: 'Multi-Page Crawling',
    desc: 'Automatically discovers and scans internal pages. Up to 100 pages per site.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
    ),
  },
  {
    title: 'PDF Reports',
    desc: 'Professional, branded compliance reports you can share with clients or legal teams.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    title: 'Ongoing Monitoring',
    desc: 'Scheduled re-scans with email alerts when new issues appear on your site.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
    ),
  },
  {
    title: 'Compliance Badge',
    desc: '"Verified Accessible by PageGuard" embed badge for sites that pass — builds trust.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
      </svg>
    ),
  },
];

const faqs = [
  {
    q: 'What does PageGuard check for?',
    a: 'PageGuard runs 13 automated WCAG 2.2 Level AA checks including missing image alt text, form labels, color contrast, heading structure, skip navigation, ARIA names, page titles, language attributes, and more.',
  },
  {
    q: 'Do I need technical skills to use PageGuard?',
    a: 'No. Just paste your website URL and click scan. PageGuard explains every issue in plain English and provides copy-paste code fixes.',
  },
  {
    q: 'Is the free plan really free?',
    a: 'Yes. The free plan includes 1 site, 1 monthly scan, and up to 5 pages. No credit card required. Upgrade anytime for more features.',
  },
  {
    q: 'What is the ADA Title II deadline?',
    a: 'By April 24, 2026, state and local government websites must comply with WCAG 2.1 Level AA. Private businesses are also increasingly targeted by ADA lawsuits — over 4,000 were filed in the past year alone.',
  },
  {
    q: 'How is PageGuard different from free tools like WAVE?',
    a: 'Free tools require technical knowledge, check one page at a time, and just list problems. PageGuard crawls your entire site, explains issues in plain English, generates AI-powered code fixes, and provides PDF compliance reports.',
  },
];

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-slate-900 via-slate-900 to-slate-800 py-24 sm:py-32">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent" aria-hidden="true" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-red-900/10 via-transparent to-transparent" aria-hidden="true" />

        <div className="relative max-w-5xl mx-auto px-4 sm:px-6 text-center">
          <div className="animate-fade-in-up">
            <div className="inline-flex items-center gap-2 bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-medium px-4 py-1.5 rounded-full mb-8">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
              </span>
              ADA Title II Deadline: April 24, 2026
            </div>
          </div>

          <h1 className="animate-fade-in-up text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-white leading-[1.1] tracking-tight">
            Is Your Website{' '}
            <span className="text-gradient">ADA Compliant?</span>
          </h1>

          <p className="animate-fade-in-up-delay-1 mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Non-compliance penalties up to <span className="text-white font-semibold">$150,000</span> per violation.
            95.9% of websites fail basic WCAG checks. Scan yours in 30 seconds.
          </p>

          <div className="animate-fade-in-up-delay-1 mt-8">
            <CountdownTimer />
          </div>

          <div className="animate-fade-in-up-delay-2 mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup"
              className="pulse-glow bg-red-600 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-red-500 transition-all duration-200 shadow-lg shadow-red-900/30"
            >
              Scan Your Website Free &rarr;
            </Link>
            <Link
              href="/pricing"
              className="bg-white/10 text-white px-8 py-4 rounded-xl text-lg font-medium border border-white/10 hover:bg-white/15 hover:border-white/20 transition-all duration-200 backdrop-blur-sm"
            >
              View Pricing
            </Link>
          </div>

          <p className="animate-fade-in-up-delay-2 mt-4 text-sm text-slate-500">
            No credit card required &middot; Free plan available &middot; Results in 30 seconds
          </p>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="relative -mt-8 z-10 max-w-5xl mx-auto px-4 sm:px-6">
        <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 grid grid-cols-2 sm:grid-cols-4 divide-x divide-gray-100">
          {[
            { value: '95.9%', label: 'of websites fail WCAG' },
            { value: '4,000+', label: 'ADA lawsuits per year' },
            { value: '$150K', label: 'max penalty per violation' },
            { value: '13', label: 'WCAG checks automated' },
          ].map((stat) => (
            <div key={stat.label} className="px-4 py-6 sm:px-6 sm:py-8 text-center">
              <div className="text-2xl sm:text-3xl font-black text-gray-900">{stat.value}</div>
              <div className="mt-1 text-xs sm:text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it Works */}
      <section className="py-24 sm:py-28">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-3">Simple Process</p>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">How PageGuard Works</h2>
            <p className="mt-4 text-lg text-gray-500 max-w-2xl mx-auto">Three steps. No technical knowledge required. Get actionable results in under a minute.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 sm:gap-12">
            {[
              {
                step: '1',
                title: 'Enter Your URL',
                desc: 'Paste your website address. We handle the rest — no installation, no browser extension.',
                gradient: 'from-blue-600 to-blue-700',
              },
              {
                step: '2',
                title: 'AI Scans Every Page',
                desc: 'PageGuard crawls your site and checks every page against 13 WCAG 2.2 Level AA rules.',
                gradient: 'from-violet-600 to-violet-700',
              },
              {
                step: '3',
                title: 'Get Code Fixes',
                desc: 'AI generates plain-English explanations and exact code snippets you can copy and paste.',
                gradient: 'from-emerald-600 to-emerald-700',
              },
            ].map((item) => (
              <div key={item.step} className="text-center group">
                <div className={`w-14 h-14 bg-gradient-to-br ${item.gradient} text-white rounded-2xl flex items-center justify-center text-xl font-bold mx-auto shadow-lg group-hover:scale-110 transition-transform duration-200`}>
                  {item.step}
                </div>
                <h3 className="mt-5 text-lg font-semibold text-gray-900">{item.title}</h3>
                <p className="mt-2 text-gray-500 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Product Preview */}
      <section className="py-4 pb-24">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="bg-gray-900 rounded-2xl overflow-hidden shadow-2xl border border-gray-800">
            {/* Browser Chrome */}
            <div className="bg-gray-800 px-4 py-3 flex items-center gap-3">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
              </div>
              <div className="flex-1 bg-gray-700/50 rounded-lg px-4 py-1.5 text-sm text-gray-400 font-mono">
                pageguard.dev/dashboard
              </div>
            </div>
            {/* Mock Dashboard */}
            <div className="p-6 sm:p-8">
              <div className="grid sm:grid-cols-3 gap-4 sm:gap-6">
                {/* Score Card */}
                <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700/50">
                  <div className="text-sm text-gray-400 mb-3">Compliance Score</div>
                  <div className="flex items-end gap-2">
                    <span className="text-5xl font-black text-white">72</span>
                    <span className="text-lg text-yellow-400 font-medium mb-1">/100</span>
                  </div>
                  <div className="mt-3 w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-gradient-to-r from-yellow-400 to-yellow-500 h-2 rounded-full" style={{ width: '72%' }} />
                  </div>
                </div>
                {/* Violations Summary */}
                <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700/50">
                  <div className="text-sm text-gray-400 mb-3">Violations Found</div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-red-400">Critical</span>
                      <span className="text-sm font-bold text-white bg-red-500/20 px-2 py-0.5 rounded">2</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-orange-400">Serious</span>
                      <span className="text-sm font-bold text-white bg-orange-500/20 px-2 py-0.5 rounded">3</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-yellow-400">Moderate</span>
                      <span className="text-sm font-bold text-white bg-yellow-500/20 px-2 py-0.5 rounded">2</span>
                    </div>
                  </div>
                </div>
                {/* AI Fix Preview */}
                <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700/50">
                  <div className="text-sm text-gray-400 mb-3">AI Fix Suggestion</div>
                  <div className="text-xs font-mono text-green-400 bg-gray-900/50 rounded-lg p-3 leading-relaxed">
                    <span className="text-gray-500">{'<!-- Before -->'}</span>
                    <br />
                    <span className="text-red-400">{'<img src="hero.jpg">'}</span>
                    <br /><br />
                    <span className="text-gray-500">{'<!-- After -->'}</span>
                    <br />
                    <span className="text-green-400">{'<img src="hero.jpg"'}</span>
                    <br />
                    <span className="text-green-400">{'  alt="Team meeting">'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-gray-50 border-y border-gray-100">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-3">Features</p>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">Everything You Need to Stay Compliant</h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <div
                key={f.title}
                className="card-hover bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-200"
              >
                <div className="w-11 h-11 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mb-4">
                  {f.icon}
                </div>
                <h3 className="text-base font-semibold text-gray-900">{f.title}</h3>
                <p className="mt-2 text-sm text-gray-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison Section */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-3">Why PageGuard</p>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">Stop Overpaying for Compliance</h2>
          </div>
          <div className="overflow-hidden rounded-2xl border border-gray-200">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-6 py-4 text-sm font-semibold text-gray-900">Feature</th>
                  <th className="px-6 py-4 text-sm font-semibold text-gray-400">Enterprise Tools</th>
                  <th className="px-6 py-4 text-sm font-semibold text-blue-600">PageGuard</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {[
                  ['Starting price', '$500+/mo', 'Free — $29/mo'],
                  ['Setup required', 'Weeks of onboarding', 'Paste URL, done'],
                  ['AI code fixes', 'No', 'Yes, copy-paste ready'],
                  ['Multi-page crawling', 'Limited', 'Up to 100 pages'],
                  ['PDF reports', 'Extra cost', 'Included (Pro)'],
                  ['Target audience', 'Enterprise only', 'SMBs & agencies'],
                ].map(([feature, enterprise, pg]) => (
                  <tr key={feature} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{feature}</td>
                    <td className="px-6 py-4 text-sm text-gray-400">{enterprise}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{pg}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Social Proof / Testimonials */}
      <section className="py-24 bg-gray-50 border-y border-gray-100">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-3">Trusted by Businesses</p>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">What Our Users Say</h2>
          </div>

          <div className="grid sm:grid-cols-3 gap-6 mb-16">
            {[
              {
                quote: 'We found 23 violations we had no idea existed. The AI fix suggestions saved our developer hours of research. Fixed everything before the deadline.',
                name: 'Sarah K.',
                role: 'Marketing Director, E-commerce',
                stars: 5,
              },
              {
                quote: "As a solo web developer, I use PageGuard to audit all my client sites. The PDF reports look professional and clients love seeing the compliance score improve.",
                name: 'James T.',
                role: 'Freelance Web Developer',
                stars: 5,
              },
              {
                quote: "Our legal team needed proof we were addressing ADA compliance. PageGuard's reports and monitoring gave us exactly what we needed for the audit trail.",
                name: 'Maria L.',
                role: 'Operations Manager, SaaS',
                stars: 5,
              },
            ].map((t) => (
              <div key={t.name} className="bg-white rounded-xl border border-gray-200 p-6 hover:border-blue-200 transition-colors">
                <div className="flex gap-0.5 mb-3">
                  {Array.from({ length: t.stars }).map((_, i) => (
                    <svg key={i} className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-sm text-gray-600 leading-relaxed mb-4">&ldquo;{t.quote}&rdquo;</p>
                <div>
                  <p className="text-sm font-semibold text-gray-900">{t.name}</p>
                  <p className="text-xs text-gray-500">{t.role}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Trust Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-3xl font-black text-gray-900">500+</div>
              <div className="mt-1 text-sm text-gray-500">websites scanned</div>
            </div>
            <div>
              <div className="text-3xl font-black text-gray-900">13</div>
              <div className="mt-1 text-sm text-gray-500">WCAG rules checked</div>
            </div>
            <div>
              <div className="text-3xl font-black text-gray-900">30s</div>
              <div className="mt-1 text-sm text-gray-500">average scan time</div>
            </div>
            <div>
              <div className="text-3xl font-black text-gray-900">4.9/5</div>
              <div className="mt-1 text-sm text-gray-500">user satisfaction</div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-24">
        <div className="max-w-3xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-3">FAQ</p>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">Frequently Asked Questions</h2>
          </div>
          <div className="space-y-3">
            {faqs.map((faq) => (
              <details
                key={faq.q}
                className="group bg-white rounded-xl border border-gray-200 hover:border-gray-300 transition-colors"
              >
                <summary className="flex items-center justify-between cursor-pointer px-6 py-5 text-left">
                  <span className="text-base font-medium text-gray-900 pr-4">{faq.q}</span>
                  <svg
                    className="w-5 h-5 text-gray-400 shrink-0 group-open:rotate-180 transition-transform duration-200"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                <div className="px-6 pb-5 text-sm text-gray-500 leading-relaxed">{faq.a}</div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative overflow-hidden bg-gradient-to-b from-slate-900 to-slate-950 py-24">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent" aria-hidden="true" />
        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white">
            Don&apos;t Wait Until It&apos;s Too Late
          </h2>
          <p className="mt-4 text-lg text-slate-400 leading-relaxed">
            The ADA deadline is real. The lawsuits are real. Protect your business today — start with a free scan.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup"
              className="pulse-glow bg-red-600 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-red-500 transition-all duration-200 shadow-lg shadow-red-900/30"
            >
              Start Free Scan Now &rarr;
            </Link>
          </div>
          <p className="mt-4 text-sm text-slate-500">
            Join 500+ businesses already getting ahead of the April 2026 deadline.
          </p>
        </div>
      </section>
    </div>
  );
}

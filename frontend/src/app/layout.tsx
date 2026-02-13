import type { Metadata } from 'next';
import './globals.css';
import Link from 'next/link';
import { AuthNav } from '@/components/AuthNav';

export const metadata: Metadata = {
  title: 'PageGuard - AI Web Accessibility Compliance Scanner',
  description: 'Scan your website for WCAG 2.2 Level AA violations. AI-powered fix suggestions. ADA Title II deadline: April 24, 2026.',
  openGraph: {
    title: 'PageGuard - Is Your Website ADA Compliant?',
    description: 'Free accessibility scan. AI-powered fixes. ADA deadline April 24, 2026.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen flex flex-col antialiased">
        <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg">
          Skip to main content
        </a>

        {/* Announcement Bar */}
        <div className="bg-red-600 text-white text-center text-sm py-2 px-4 font-medium">
          <span className="hidden sm:inline">ADA Title II compliance deadline: </span>
          <span className="font-bold">April 24, 2026</span>
          <span className="hidden sm:inline"> &mdash; Is your website ready?</span>
          <Link href="/signup" className="ml-2 underline underline-offset-2 hover:text-red-100 transition">
            Free scan &rarr;
          </Link>
        </div>

        <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40" aria-label="Main navigation">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link href="/" className="flex items-center space-x-2 group">
                  <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                  </div>
                  <span className="text-xl font-bold text-gray-900 tracking-tight">PageGuard</span>
                </Link>
              </div>
              <AuthNav />
            </div>
          </div>
        </nav>

        <main id="main-content" className="flex-1">{children}</main>

        <footer className="bg-gray-900 text-gray-400 mt-auto" aria-label="Footer">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-8">
              <div className="col-span-2 sm:col-span-1">
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                  </div>
                  <span className="text-white font-bold">PageGuard</span>
                </div>
                <p className="text-sm leading-relaxed">Web accessibility compliance made simple. Scan, fix, and monitor your website&apos;s WCAG compliance.</p>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Product</h2>
                <ul className="space-y-3">
                  <li><Link href="/pricing" className="text-sm hover:text-white transition">Pricing</Link></li>
                  <li><Link href="/dashboard" className="text-sm hover:text-white transition">Dashboard</Link></li>
                  <li><Link href="/signup" className="text-sm hover:text-white transition">Free Scan</Link></li>
                </ul>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Legal</h2>
                <ul className="space-y-3">
                  <li><Link href="/privacy" className="text-sm hover:text-white transition">Privacy Policy</Link></li>
                  <li><Link href="/terms" className="text-sm hover:text-white transition">Terms of Service</Link></li>
                  <li><Link href="/disclaimer" className="text-sm hover:text-white transition">Disclaimer</Link></li>
                </ul>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Support</h2>
                <ul className="space-y-3">
                  <li><a href="mailto:support@pageguard.dev" className="text-sm hover:text-white transition">support@pageguard.dev</a></li>
                </ul>
              </div>
            </div>
            <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col sm:flex-row justify-between items-center gap-4">
              <p className="text-sm">&copy; 2026 PageGuard. All rights reserved.</p>
              <p className="text-xs text-gray-500">Built to help businesses meet the ADA Title II deadline.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}

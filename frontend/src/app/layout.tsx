import type { Metadata } from 'next';
import './globals.css';
import Link from 'next/link';
import { AuthNav } from '@/components/AuthNav';

export const metadata: Metadata = {
  title: 'PageGuard - AI Web Accessibility Compliance Scanner',
  description: 'Scan your website for WCAG 2.2 Level AA violations. AI-powered fix suggestions. ADA Title II deadline: April 24, 2026.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen flex flex-col font-sans antialiased">
        <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg">
          Skip to main content
        </a>

        <nav className="bg-white border-b border-gray-200" aria-label="Main navigation">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link href="/" className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                  </div>
                  <span className="text-xl font-bold text-gray-900">PageGuard</span>
                </Link>
              </div>
              <AuthNav />
            </div>
          </div>
        </nav>

        <main id="main-content" className="flex-1">{children}</main>

        <footer className="bg-white border-t border-gray-200 mt-auto" aria-label="Footer">
          <div className="max-w-7xl mx-auto px-4 py-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
              <div>
                <h2 className="text-sm font-semibold text-gray-900 mb-3">Product</h2>
                <ul className="space-y-2">
                  <li><Link href="/pricing" className="text-sm text-gray-500 hover:text-gray-700">Pricing</Link></li>
                  <li><Link href="/dashboard" className="text-sm text-gray-500 hover:text-gray-700">Dashboard</Link></li>
                </ul>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900 mb-3">Legal</h2>
                <ul className="space-y-2">
                  <li><Link href="/privacy" className="text-sm text-gray-500 hover:text-gray-700">Privacy Policy</Link></li>
                  <li><Link href="/terms" className="text-sm text-gray-500 hover:text-gray-700">Terms of Service</Link></li>
                  <li><Link href="/disclaimer" className="text-sm text-gray-500 hover:text-gray-700">Disclaimer</Link></li>
                </ul>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900 mb-3">Contact</h2>
                <ul className="space-y-2">
                  <li><a href="mailto:support@pageguard.dev" className="text-sm text-gray-500 hover:text-gray-700">support@pageguard.dev</a></li>
                </ul>
              </div>
            </div>
            <div className="mt-8 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-400">&copy; 2026 PageGuard. Web accessibility compliance made simple.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}

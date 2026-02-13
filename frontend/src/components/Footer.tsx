import Link from 'next/link';

export function Footer() {
  return (
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
  );
}

import Link from 'next/link';

export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex justify-between items-center">
          <p className="text-sm text-gray-400">&copy; 2026 PageGuard. Web accessibility compliance made simple.</p>
          <Link href="/pricing" className="text-sm text-gray-400 hover:text-gray-600">Pricing</Link>
        </div>
      </div>
    </footer>
  );
}

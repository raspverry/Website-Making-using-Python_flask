export default async function SiteDetailPage({ params }: { params: Promise<{ uid: string }> }) {
  const { uid } = await params;
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900">Site: {uid}</h1>
      <p className="text-gray-500 mt-2">Site details and scan history will appear here.</p>
    </div>
  );
}

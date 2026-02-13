export function ScoreCircle({ score, size = 'lg' }: { score: number; size?: 'sm' | 'lg' }) {
  const color = score >= 90 ? 'text-green-600 border-green-500' : score >= 70 ? 'text-yellow-600 border-yellow-500' : score >= 50 ? 'text-orange-500 border-orange-500' : 'text-red-600 border-red-500';
  const sizeClass = size === 'lg' ? 'w-24 h-24 text-4xl' : 'w-14 h-14 text-xl';

  return (
    <div className={`${sizeClass} ${color} rounded-full border-4 flex items-center justify-center font-bold`}>
      {score}
    </div>
  );
}

export function ScoreCircle({ score, size = 'lg' }: { score: number; size?: 'sm' | 'lg' }) {
  const getColor = (s: number) => {
    if (s >= 90) return { text: 'text-green-600', ring: 'stroke-green-500' };
    if (s >= 70) return { text: 'text-yellow-600', ring: 'stroke-yellow-500' };
    if (s >= 50) return { text: 'text-orange-500', ring: 'stroke-orange-500' };
    return { text: 'text-red-600', ring: 'stroke-red-500' };
  };

  const color = getColor(score);
  const level = score >= 90 ? 'Excellent' : score >= 70 ? 'Good' : score >= 50 ? 'Needs improvement' : 'Poor';

  if (size === 'sm') {
    const r = 22;
    const c = 2 * Math.PI * r;
    const offset = c - (score / 100) * c;
    return (
      <div
        role="img"
        aria-label={`Compliance score: ${score} out of 100. ${level}.`}
        className="relative w-14 h-14"
      >
        <svg className="w-14 h-14 -rotate-90" viewBox="0 0 56 56" aria-hidden="true">
          <circle cx="28" cy="28" r={r} fill="none" stroke="#e5e7eb" strokeWidth="4" />
          <circle
            cx="28" cy="28" r={r} fill="none"
            className={color.ring}
            strokeWidth="4"
            strokeLinecap="round"
            strokeDasharray={c}
            strokeDashoffset={offset}
          />
        </svg>
        <div className={`absolute inset-0 flex items-center justify-center text-lg font-bold ${color.text}`}>
          {score}
        </div>
      </div>
    );
  }

  const r = 44;
  const c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;

  return (
    <div
      role="img"
      aria-label={`Compliance score: ${score} out of 100. ${level}.`}
      className="relative w-28 h-28"
    >
      <svg className="w-28 h-28 -rotate-90" viewBox="0 0 112 112" aria-hidden="true">
        <circle cx="56" cy="56" r={r} fill="none" stroke="#f3f4f6" strokeWidth="6" />
        <circle
          cx="56" cy="56" r={r} fill="none"
          className={color.ring}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-bold ${color.text}`}>{score}</span>
        <span className="text-[10px] text-gray-400 font-medium">/100</span>
      </div>
    </div>
  );
}

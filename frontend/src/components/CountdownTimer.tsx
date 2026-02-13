'use client';
import { useState, useEffect } from 'react';
import { config } from '@/lib/config';

export function CountdownTimer() {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0 });

  useEffect(() => {
    const update = () => {
      const now = new Date();
      const diff = config.adaDeadline.getTime() - now.getTime();
      if (diff <= 0) {
        setTimeLeft({ days: 0, hours: 0, minutes: 0 });
        return;
      }
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      setTimeLeft({ days, hours, minutes });
    };
    update();
    const interval = setInterval(update, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="inline-flex items-center gap-3 sm:gap-4" aria-label={`${timeLeft.days} days, ${timeLeft.hours} hours, ${timeLeft.minutes} minutes until ADA deadline`}>
      <div className="text-center">
        <div className="text-4xl sm:text-5xl font-black text-white tabular-nums">{timeLeft.days}</div>
        <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">Days</div>
      </div>
      <div className="text-2xl font-bold text-slate-600">:</div>
      <div className="text-center">
        <div className="text-4xl sm:text-5xl font-black text-white tabular-nums">{String(timeLeft.hours).padStart(2, '0')}</div>
        <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">Hours</div>
      </div>
      <div className="text-2xl font-bold text-slate-600">:</div>
      <div className="text-center">
        <div className="text-4xl sm:text-5xl font-black text-white tabular-nums">{String(timeLeft.minutes).padStart(2, '0')}</div>
        <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">Min</div>
      </div>
    </div>
  );
}

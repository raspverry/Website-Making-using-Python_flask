'use client';
import { useState, useEffect } from 'react';
import { config } from '@/lib/config';

export function CountdownTimer() {
  const [days, setDays] = useState(0);

  useEffect(() => {
    const update = () => {
      const now = new Date();
      const diff = config.adaDeadline.getTime() - now.getTime();
      setDays(Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24))));
    };
    update();
    const interval = setInterval(update, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="text-center">
      <div className="text-7xl font-black text-red-600">{days}</div>
      <div className="text-lg text-gray-600 font-medium mt-1">days until ADA deadline</div>
    </div>
  );
}

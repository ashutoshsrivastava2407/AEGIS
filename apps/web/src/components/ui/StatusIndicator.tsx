import React from 'react';
import { clsx } from 'clsx';

export interface StatusIndicatorProps {
  status: 'OPERATIONAL' | 'DEGRADED' | 'CRITICAL' | 'OFFLINE' | string;
  label?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, label }) => {
  const isUp = status.toUpperCase() === 'OPERATIONAL' || status.toUpperCase() === 'UP';
  const isDegraded = status.toUpperCase() === 'DEGRADED';
  const isCritical = status.toUpperCase() === 'CRITICAL' || status.toUpperCase() === 'DOWN';

  return (
    <div className="inline-flex items-center gap-2 text-xs font-medium">
      <span className="relative flex h-2 w-2">
        {isUp && (
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#35C98A] opacity-75"></span>
        )}
        <span
          className={clsx(
            'relative inline-flex rounded-full h-2 w-2',
            isUp && 'bg-[#35C98A]',
            isDegraded && 'bg-[#E6A84A]',
            isCritical && 'bg-[#EF6262]',
            !isUp && !isDegraded && !isCritical && 'bg-gray-500'
          )}
        ></span>
      </span>
      <span className="text-gray-300">{label || status}</span>
    </div>
  );
};

import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'critical' | 'info' | 'neutral' | 'brand';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  className,
}) => {
  const base = 'inline-flex items-center font-medium rounded-full border transition-colors';

  const variants = {
    success: 'bg-[#35C98A]/10 text-[#35C98A] border-[#35C98A]/20',
    warning: 'bg-[#E6A84A]/10 text-[#E6A84A] border-[#E6A84A]/20',
    critical: 'bg-[#EF6262]/10 text-[#EF6262] border-[#EF6262]/20',
    info: 'bg-[#5B9CF6]/10 text-[#5B9CF6] border-[#5B9CF6]/20',
    neutral: 'bg-[#16161C] text-gray-400 border-[rgba(255,255,255,0.08)]',
    brand: 'bg-[#7C6FF2]/10 text-[#7C6FF2] border-[#7C6FF2]/20',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
  };

  return (
    <span className={twMerge(clsx(base, variants[variant], sizes[size], className))}>
      {children}
    </span>
  );
};

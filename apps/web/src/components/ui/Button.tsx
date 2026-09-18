import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'secondary',
  size = 'md',
  icon,
  className,
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-colors rounded-controls focus:outline-none focus:ring-1 focus:ring-[#7C6FF2] disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary: 'bg-[#7C6FF2] text-white hover:bg-[#9186FF] active:bg-[#685BC7]',
    secondary: 'bg-[#16161C] text-gray-200 border border-[rgba(255,255,255,0.08)] hover:bg-[#1B1B22] hover:border-[rgba(255,255,255,0.16)]',
    ghost: 'text-gray-400 hover:text-gray-100 hover:bg-[#16161C]',
    danger: 'bg-[#EF6262]/10 text-[#EF6262] border border-[#EF6262]/20 hover:bg-[#EF6262]/20',
  };

  const sizes = {
    sm: 'text-xs px-2.5 py-1.5 gap-1.5',
    md: 'text-sm px-3.5 py-2 gap-2',
    lg: 'text-base px-4 py-2.5 gap-2.5',
  };

  return (
    <button
      className={twMerge(clsx(baseStyles, variants[variant], sizes[size], className))}
      disabled={disabled}
      {...props}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </button>
  );
};

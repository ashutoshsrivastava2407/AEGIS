import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  className,
  icon,
  ...props
}, ref) => {
  return (
    <div className="relative flex items-center w-full">
      {icon && (
        <span className="absolute left-3 text-gray-500 pointer-events-none">
          {icon}
        </span>
      )}
      <input
        ref={ref}
        className={twMerge(
          clsx(
            'w-full bg-[#111116] text-gray-100 text-sm placeholder-gray-500 rounded-controls border border-[rgba(255,255,255,0.08)] py-2 px-3 focus:outline-none focus:border-[#7C6FF2] transition-colors',
            icon && 'pl-9',
            className
          )
        )}
        {...props}
      />
    </div>
  );
});

Input.displayName = 'Input';

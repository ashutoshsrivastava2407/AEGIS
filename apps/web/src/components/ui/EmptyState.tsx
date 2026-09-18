import React from 'react';
import { Database, ShieldAlert, FileSearch } from 'lucide-react';

export interface EmptyStateProps {
  title: string;
  description: string;
  action?: React.ReactNode;
  icon?: 'search' | 'data' | 'security';
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  action,
  icon = 'search',
}) => {
  const IconComponent =
    icon === 'data' ? Database : icon === 'security' ? ShieldAlert : FileSearch;

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-[rgba(255,255,255,0.08)] rounded-panels bg-[#111116]/50">
      <div className="p-3 bg-[#16161C] rounded-full border border-[rgba(255,255,255,0.08)] text-[#7C6FF2] mb-4">
        <IconComponent size={24} />
      </div>
      <h3 className="text-base font-semibold text-gray-200 mb-1">{title}</h3>
      <p className="text-sm text-gray-400 max-w-sm mb-6">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
};

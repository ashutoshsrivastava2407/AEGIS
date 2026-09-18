import React from 'react';
import { Loader2 } from 'lucide-react';

export interface LoadingStateProps {
  label?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ label = 'Loading workspace data...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-gray-400">
      <Loader2 className="animate-spin text-[#7C6FF2]" size={24} />
      <span className="text-sm font-medium">{label}</span>
    </div>
  );
};

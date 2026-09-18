import React from 'react';
import { Search, Shield, Bell, User } from 'lucide-react';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import { Badge } from '@/components/ui/Badge';

export interface HeaderProps {
  systemStatus: string;
  onOpenCommandPalette: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  systemStatus,
  onOpenCommandPalette,
}) => {
  return (
    <header className="h-12 bg-[#0B0B0F] border-b border-[rgba(255,255,255,0.08)] px-4 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 font-bold text-sm text-gray-100 tracking-wider">
          <Shield size={18} className="text-[#7C6FF2]" />
          <span>AEGIS</span>
        </div>
        <div className="h-4 w-px bg-white/10" />
        <StatusIndicator status={systemStatus} label="System Operational" />
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onOpenCommandPalette}
          className="flex items-center gap-2 px-3 py-1.5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-controls text-xs text-gray-400 hover:text-gray-200 hover:border-[rgba(255,255,255,0.16)] transition-all"
        >
          <Search size={13} />
          <span>Search or Command...</span>
          <kbd className="bg-[#16161C] border border-[rgba(255,255,255,0.1)] px-1.5 py-0.5 rounded text-[10px] text-gray-400 font-mono">
            ⌘K
          </kbd>
        </button>

        <Badge variant="brand" size="sm">Enterprise</Badge>

        <button className="p-1.5 text-gray-400 hover:text-gray-200 transition-colors">
          <Bell size={15} />
        </button>

        <div className="flex items-center gap-2 pl-2 border-l border-white/10">
          <div className="w-6 h-6 rounded-full bg-[#16161C] border border-[rgba(255,255,255,0.12)] flex items-center justify-center text-gray-300">
            <User size={13} />
          </div>
          <span className="text-xs text-gray-300 font-medium">Enterprise Operator</span>
        </div>
      </div>
    </header>
  );
};

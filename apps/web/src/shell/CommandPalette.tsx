import React, { useEffect, useState } from 'react';
import { Search, Command as CmdIcon, Database, Cpu, Shield, Zap, X } from 'lucide-react';
import { DomainId } from '@/types';

export interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectDomain: (domain: DomainId) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onSelectDomain,
}) => {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else setQuery('');
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const quickNavItems: { id: DomainId; label: string; icon: React.ReactNode; category: string }[] = [
    { id: 'command', label: 'Command Overview', icon: <CmdIcon size={14} />, category: 'Platform' },
    { id: 'data', label: 'Data Platform & Catalog', icon: <Database size={14} />, category: 'Data' },
    { id: 'ai', label: 'AI Platform & RAG', icon: <Cpu size={14} />, category: 'Intelligence' },
    { id: 'decisions', label: 'Decision Engine & Simulations', icon: <Zap size={14} />, category: 'Decisions' },
    { id: 'governance', label: 'Multi-Tenant Governance & Audit', icon: <Shield size={14} />, category: 'Security' },
  ];

  const filtered = quickNavItems.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/60 backdrop-blur-xs">
      <div className="w-full max-w-xl bg-[#111116] border border-[rgba(255,255,255,0.12)] rounded-dialogs shadow-2xl overflow-hidden">
        <div className="flex items-center px-4 border-b border-[rgba(255,255,255,0.08)]">
          <Search size={16} className="text-gray-400 mr-3" />
          <input
            autoFocus
            type="text"
            placeholder="Search datasets, models, decisions, or jump to domain... (Esc to close)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent py-3.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none"
          />
          <button onClick={onClose} className="text-gray-500 hover:text-gray-300">
            <X size={16} />
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="py-8 text-center text-xs text-gray-500">
              No matching resources or domains found.
            </div>
          ) : (
            filtered.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  onSelectDomain(item.id);
                  onClose();
                }}
                className="w-full flex items-center justify-between px-3 py-2.5 rounded-controls text-left text-xs hover:bg-[#16161C] transition-colors group"
              >
                <div className="flex items-center gap-3 text-gray-300 group-hover:text-white">
                  <span className="text-[#7C6FF2]">{item.icon}</span>
                  <span>{item.label}</span>
                </div>
                <span className="text-[11px] text-gray-500 uppercase tracking-wider">{item.category}</span>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

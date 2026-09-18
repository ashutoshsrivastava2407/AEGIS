import React, { useState } from 'react';
import { DomainId, EvidenceItem } from '@/types';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { CommandPalette } from './CommandPalette';
import { EvidencePanel } from '@/components/ui/EvidencePanel';

export interface AppShellProps {
  children: React.ReactNode;
  activeDomain: DomainId;
  onSelectDomain: (domain: DomainId) => void;
  systemStatus?: string;
  evidenceItems?: EvidenceItem[];
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  activeDomain,
  onSelectDomain,
  systemStatus = 'OPERATIONAL',
  evidenceItems = [],
}) => {
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  return (
    <div className="flex flex-col h-screen w-screen bg-[#0B0B0F] overflow-hidden text-gray-100">
      <Header
        systemStatus={systemStatus}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
      />

      <div className="flex flex-1 h-[calc(100vh-3rem)] overflow-hidden">
        <Sidebar activeDomain={activeDomain} onSelectDomain={onSelectDomain} />

        <main className="flex-1 flex flex-col h-full bg-[#0B0B0F] overflow-y-auto min-w-0">
          <div className="flex-1 p-6">
            {children}
          </div>
        </main>

        <EvidencePanel items={evidenceItems} />
      </div>

      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onSelectDomain={onSelectDomain}
      />
    </div>
  );
};

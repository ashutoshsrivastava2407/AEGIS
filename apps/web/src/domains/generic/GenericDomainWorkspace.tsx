import React from 'react';
import { DomainId } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';

export interface GenericDomainWorkspaceProps {
  domainId: DomainId;
  title: string;
  description: string;
}

export const GenericDomainWorkspace: React.FC<GenericDomainWorkspaceProps> = ({
  title,
  description,
}) => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.08)] pb-4">
        <div>
          <h1 className="text-xl font-bold text-gray-100 tracking-tight flex items-center gap-2">
            {title}
            <Badge variant="brand" size="sm">AEGIS Domain</Badge>
          </h1>
          <p className="text-xs text-gray-400 mt-1">{description}</p>
        </div>
      </div>

      <EmptyState
        title={`${title} Ready`}
        description="Resource management and active telemetry monitoring for this workspace domain will display here."
        icon="search"
      />
    </div>
  );
};

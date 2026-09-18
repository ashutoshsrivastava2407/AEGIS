import React from 'react';
import { ShieldCheck, GitBranch, FileText, Database, Activity } from 'lucide-react';
import { EvidenceItem } from '@/types';
import { Badge } from './Badge';

export interface EvidencePanelProps {
  items?: EvidenceItem[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ items = [] }) => {
  return (
    <aside className="w-80 bg-[#111116] border-l border-[rgba(255,255,255,0.08)] flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-[rgba(255,255,255,0.08)] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck size={16} className="text-[#7C6FF2]" />
          <h3 className="text-xs font-semibold text-gray-200 uppercase tracking-wider">
            Context &amp; Evidence Trace
          </h3>
        </div>
        <Badge variant="brand" size="sm">Governed</Badge>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {items.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Activity className="mx-auto mb-2 text-gray-600" size={24} />
            <p className="text-xs">No active evidence trace selected.</p>
            <p className="text-[11px] text-gray-600 mt-1">Select a decision, model, or dataset to view lineage trace.</p>
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              className="p-3 bg-[#16161C] rounded-cards border border-[rgba(255,255,255,0.08)] hover:border-[#7C6FF2]/40 transition-colors"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                  {item.type === 'DATASET' && <Database size={12} className="text-[#5B9CF6]" />}
                  {item.type === 'DOCUMENT' && <FileText size={12} className="text-[#E6A84A]" />}
                  {item.type === 'DECISION' && <GitBranch size={12} className="text-[#35C98A]" />}
                  {item.title}
                </span>
                <Badge variant="neutral" size="sm">{item.type}</Badge>
              </div>
              <p className="text-xs text-gray-400 mb-2">{item.summary}</p>
              <div className="flex items-center justify-between text-[11px] text-gray-500">
                <span>Source: {item.source}</span>
                {item.confidence !== undefined && (
                  <span className="text-[#35C98A] font-mono">{(item.confidence * 100).toFixed(0)}% conf</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
};

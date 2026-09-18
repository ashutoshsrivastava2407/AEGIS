import React from 'react';
import { GitBranch, ArrowRight, Database, Server } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { LineageGraph } from '@/services/api/dataApi';

export interface LineageTabProps {
  lineage: LineageGraph;
}

export const LineageTab: React.FC<LineageTabProps> = ({ lineage }) => {
  if (lineage.nodes.length === 0) {
    return (
      <EmptyState
        title="No Lineage Graph Generated"
        description="Lineage edges will populate automatically as ingestion pipelines move records through Bronze, Silver, and Gold layers."
        icon="data"
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
          <GitBranch size={16} className="text-[#7C6FF2]" /> End-to-End Lineage DAG Graph
        </h3>
        <Badge variant="brand" size="sm">Persisted Backend Graph</Badge>
      </div>

      {/* Lineage Flow Visualizer */}
      <div className="p-6 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels overflow-x-auto">
        <div className="flex items-center gap-4 min-w-max justify-around py-4">
          {lineage.nodes.map((node, index) => (
            <React.Fragment key={node.id}>
              <div className="p-4 bg-[#16161C] border border-[rgba(255,255,255,0.12)] rounded-cards w-56 space-y-2 hover:border-[#7C6FF2] transition-colors">
                <div className="flex items-center justify-between">
                  <Badge variant={node.layer === 'BRONZE' ? 'warning' : node.layer === 'SILVER' ? 'neutral' : 'success'} size="sm">
                    {node.layer || node.type}
                  </Badge>
                </div>
                <div className="flex items-center gap-2 text-xs font-semibold text-gray-100">
                  {node.type === 'SOURCE' ? <Server size={14} className="text-[#7C6FF2]" /> : <Database size={14} className="text-[#5B9CF6]" />}
                  <span className="truncate">{node.label}</span>
                </div>
                <p className="text-[11px] font-mono text-gray-500 truncate">ID: {node.id}</p>
              </div>

              {index < lineage.nodes.length - 1 && (
                <div className="flex items-center text-gray-500">
                  <ArrowRight size={20} className="text-[#7C6FF2]" />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};

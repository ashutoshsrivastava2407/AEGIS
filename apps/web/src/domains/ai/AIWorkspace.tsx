import React from 'react';
import { Cpu, ShieldAlert } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';

export const AIWorkspace: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.08)] pb-4">
        <div>
          <h1 className="text-xl font-bold text-gray-100 tracking-tight flex items-center gap-2">
            AI Platform &amp; Agent Hub
            <Badge variant="brand" size="sm">RAG &amp; LLM Gateway</Badge>
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            LLM Gateway routing, document vector indexes, supervisor agents, and controlled tool execution.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            <Cpu size={14} className="text-[#7C6FF2]" /> LLM Gateway Routing
          </h3>
          <div className="space-y-2 text-xs text-gray-300">
            <div className="flex items-center justify-between p-2 bg-[#16161C] rounded-controls border border-white/5">
              <span>Primary Provider</span>
              <Badge variant="success" size="sm">Active</Badge>
            </div>
            <div className="flex items-center justify-between p-2 bg-[#16161C] rounded-controls border border-white/5">
              <span>Fallback Provider</span>
              <Badge variant="neutral" size="sm">Standby</Badge>
            </div>
          </div>
        </div>

        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            <ShieldAlert size={14} className="text-[#E6A84A]" /> Security &amp; Safety Guardrails
          </h3>
          <div className="space-y-1.5 text-xs text-gray-400">
            <p>• Prompt Injection Defense: <span className="text-[#35C98A]">ENFORCED</span></p>
            <p>• PII Redaction &amp; Masking: <span className="text-[#35C98A]">ENFORCED</span></p>
            <p>• Tenant Document Scope: <span className="text-[#35C98A]">ENFORCED</span></p>
          </div>
        </div>
      </div>

      <EmptyState
        title="No Agent Execution Runs Active"
        description="Autonomous supervisor and worker agent tasks will display step duration, tool calls, and evidence references here."
        icon="search"
      />
    </div>
  );
};

import React from 'react';
import { clsx } from 'clsx';
import {
  LayoutDashboard,
  BarChart3,
  Database,
  LineChart,
  BrainCircuit,
  FileText,
  Cpu,
  Bot,
  GitBranch,
  PlaySquare,
  Zap,
  Activity,
  ShieldCheck,
  Server,
} from 'lucide-react';
import { DomainId, DomainMeta } from '@/types';

export interface SidebarProps {
  activeDomain: DomainId;
  onSelectDomain: (domain: DomainId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeDomain,
  onSelectDomain,
}) => {
  const domains: DomainMeta[] = [
    { id: 'command', label: 'Command Overview', category: 'CORE', icon: 'command', description: 'Executive operational summary' },
    { id: 'intelligence', label: 'Intelligence', category: 'CORE', icon: 'intelligence', description: 'Real-time analytical insights' },
    { id: 'data', label: 'Data Platform', category: 'PLATFORM', icon: 'data', description: 'Medallion data & lineage' },
    { id: 'streaming', label: 'Real-Time Streaming', category: 'PLATFORM', icon: 'streaming', description: 'Kafka broker & event streams' },
    { id: 'analytics', label: 'Analytics', category: 'PLATFORM', icon: 'analytics', description: 'Business metrics & aggregations' },
    { id: 'ml', label: 'ML Platform', category: 'PLATFORM', icon: 'ml', description: 'Predictive models & features' },
    { id: 'knowledge', label: 'Knowledge Base', category: 'PLATFORM', icon: 'knowledge', description: 'RAG documents & vectors' },
    { id: 'ai', label: 'AI Platform', category: 'PLATFORM', icon: 'ai', description: 'LLM Gateway & status' },
    { id: 'agents', label: 'Agent Workspace', category: 'PLATFORM', icon: 'agents', description: 'Autonomous agent runs' },
    { id: 'decisions', label: 'Decision Engine', category: 'PLATFORM', icon: 'decisions', description: 'Governed decision logic' },
    { id: 'simulations', label: 'Simulations', category: 'PLATFORM', icon: 'simulations', description: 'Scenario modeling' },
    { id: 'operations', label: 'Action Queue', category: 'PLATFORM', icon: 'operations', description: 'Workflow approval & execution' },
    { id: 'observability', label: 'Observability', category: 'GOVERNANCE', icon: 'observability', description: 'System metrics & telemetry' },
    { id: 'governance', label: 'Governance & Audit', category: 'GOVERNANCE', icon: 'governance', description: 'RBAC policies & audit trail' },
    { id: 'system', label: 'System Admin', category: 'GOVERNANCE', icon: 'system', description: 'Node status & infra configuration' },
  ];

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'command': return <LayoutDashboard size={15} />;
      case 'intelligence': return <BarChart3 size={15} />;
      case 'data': return <Database size={15} />;
      case 'streaming': return <Activity size={15} />;
      case 'analytics': return <LineChart size={15} />;
      case 'ml': return <BrainCircuit size={15} />;
      case 'knowledge': return <FileText size={15} />;
      case 'ai': return <Cpu size={15} />;
      case 'agents': return <Bot size={15} />;
      case 'decisions': return <GitBranch size={15} />;
      case 'simulations': return <PlaySquare size={15} />;
      case 'operations': return <Zap size={15} />;
      case 'observability': return <Activity size={15} />;
      case 'governance': return <ShieldCheck size={15} />;
      case 'system': return <Server size={15} />;
      default: return <LayoutDashboard size={15} />;
    }
  };

  const coreDomains = domains.filter((d) => d.category === 'CORE');
  const platformDomains = domains.filter((d) => d.category === 'PLATFORM');
  const governanceDomains = domains.filter((d) => d.category === 'GOVERNANCE');

  const renderSection = (title: string, items: DomainMeta[]) => (
    <div className="mb-4">
      <div className="px-3 mb-1 text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
        {title}
      </div>
      <div className="space-y-0.5">
        {items.map((domain) => {
          const isActive = activeDomain === domain.id;
          return (
            <button
              key={domain.id}
              onClick={() => onSelectDomain(domain.id)}
              className={clsx(
                'w-full flex items-center gap-2.5 px-3 py-1.5 rounded-controls text-xs font-medium transition-colors text-left',
                isActive
                  ? 'bg-[#7C6FF2]/10 text-[#7C6FF2] font-semibold'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-[#16161C]'
              )}
            >
              <span className={clsx(isActive ? 'text-[#7C6FF2]' : 'text-gray-500')}>
                {getIcon(domain.icon)}
              </span>
              <span className="truncate">{domain.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <aside className="w-56 bg-[#111116] border-r border-[rgba(255,255,255,0.08)] flex flex-col h-full shrink-0 select-none">
      <div className="p-3 border-b border-[rgba(255,255,255,0.08)]">
        <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
          Enterprise Workspaces
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-2">
        {renderSection('Executive', coreDomains)}
        {renderSection('Platform Engine', platformDomains)}
        {renderSection('Governance & Control', governanceDomains)}
      </div>
    </aside>
  );
};

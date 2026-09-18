import React, { useState } from 'react';
import { DomainId, EvidenceItem } from '@/types';
import { AppShell } from '@/shell/AppShell';
import { CommandWorkspace } from '@/domains/command/CommandWorkspace';
import { DataWorkspace } from '@/domains/data/DataWorkspace';
import { StreamingWorkspace } from '@/domains/streaming/StreamingWorkspace';
import { AIWorkspace } from '@/domains/ai/AIWorkspace';
import { DecisionsWorkspace } from '@/domains/decisions/DecisionsWorkspace';
import { GovernanceWorkspace } from '@/domains/governance/GovernanceWorkspace';
import { SystemWorkspace } from '@/domains/system/SystemWorkspace';
import { AnalyticsWorkspace } from '@/domains/analytics/AnalyticsWorkspace';
import { MLWorkspace } from '@/domains/ml/MLWorkspace';
import { KnowledgeWorkspace } from '@/domains/knowledge/KnowledgeWorkspace';
import { AgentWorkspace } from '@/domains/agents/AgentWorkspace';
import { WorkflowsWorkspace } from '@/domains/workflows/WorkflowsWorkspace';
import { OperationsWorkspace } from '@/domains/operations/OperationsWorkspace';

export const App: React.FC = () => {
  const [activeDomain, setActiveDomain] = useState<DomainId>('command');
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([
    {
      id: 'ev_01',
      title: 'AEGIS Security Boundary',
      type: 'DECISION',
      source: 'ServerPolicyEngine',
      confidence: 0.99,
      timestamp: new Date().toISOString(),
      summary: 'Multi-tenant isolation and RBAC policy rules enforced across API routes.',
    },
    {
      id: 'ev_02',
      title: 'PostgreSQL & Redis Probe',
      type: 'LOG',
      source: 'System Health Check',
      confidence: 1.0,
      timestamp: new Date().toISOString(),
      summary: 'Database connection pool and event cache initialized successfully.',
    },
  ]);

  const handleSelectEvidence = (newItem: any) => {
    setEvidenceItems((prev) => [newItem, ...prev.filter((p) => p.id !== newItem.id)].slice(0, 10));
  };

  const renderDomainWorkspace = () => {
    switch (activeDomain) {
      case 'command':
        return (
          <CommandWorkspace
            systemStatus="OPERATIONAL"
            onSelectDomain={(domain) => setActiveDomain(domain)}
            onSelectEvidence={handleSelectEvidence}
          />
        );
      case 'data':
        return <DataWorkspace />;
      case 'streaming':
        return <StreamingWorkspace />;
      case 'ai':
        return <AIWorkspace />;
      case 'decisions':
        return <DecisionsWorkspace />;
      case 'governance':
        return <GovernanceWorkspace />;
      case 'system':
        return <SystemWorkspace />;
      case 'intelligence':
      case 'analytics':
        return <AnalyticsWorkspace />;
      case 'ml':
        return <MLWorkspace />;
      case 'knowledge':
        return <KnowledgeWorkspace />;
      case 'agents':
        return <AgentWorkspace />;
      case 'workflows':
        return <WorkflowsWorkspace />;
      case 'operations':
      case 'observability':
        return <OperationsWorkspace />;
      default:
        return (
          <CommandWorkspace
            systemStatus="OPERATIONAL"
            onSelectDomain={(domain) => setActiveDomain(domain)}
            onSelectEvidence={handleSelectEvidence}
          />
        );
    }
  };

  return (
    <AppShell
      activeDomain={activeDomain}
      onSelectDomain={(domain) => setActiveDomain(domain)}
      systemStatus="OPERATIONAL"
      evidenceItems={evidenceItems}
    >
      {renderDomainWorkspace()}
    </AppShell>
  );
};

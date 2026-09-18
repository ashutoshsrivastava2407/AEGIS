import React, { useState } from 'react';
import { Server, Plus, Play } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { DataSource } from '@/services/api/dataApi';

export interface SourcesTabProps {
  sources: DataSource[];
  onOpenCreateModal: () => void;
  onTestSource: (id: string) => Promise<void>;
  onTriggerIngestion: (id: string) => Promise<void>;
}

export const SourcesTab: React.FC<SourcesTabProps> = ({
  sources,
  onOpenCreateModal,
  onTestSource,
  onTriggerIngestion,
}) => {
  const [testingId, setTestingId] = useState<string | null>(null);
  const [ingestingId, setIngestingId] = useState<string | null>(null);

  const handleTest = async (id: string) => {
    setTestingId(id);
    try {
      await onTestSource(id);
    } finally {
      setTestingId(null);
    }
  };

  const handleIngest = async (id: string) => {
    setIngestingId(id);
    try {
      await onTriggerIngestion(id);
    } finally {
      setIngestingId(null);
    }
  };

  if (sources.length === 0) {
    return (
      <EmptyState
        title="No Data Sources Registered"
        description="Register a tenant CSV, JSON, PostgreSQL, or REST API source to begin batch ingestion."
        icon="data"
        action={
          <Button variant="primary" size="sm" icon={<Plus size={14} />} onClick={onOpenCreateModal}>
            Register Data Source
          </Button>
        }
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Registered Tenant Sources</h3>
        <Button variant="primary" size="sm" icon={<Plus size={14} />} onClick={onOpenCreateModal}>
          Register Source
        </Button>
      </div>

      <div className="border border-[rgba(255,255,255,0.08)] rounded-panels overflow-hidden bg-[#111116]">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#16161C] border-b border-[rgba(255,255,255,0.08)] text-gray-400 font-semibold uppercase tracking-wider">
            <tr>
              <th className="p-3">Source Name</th>
              <th className="p-3">Type</th>
              <th className="p-3">Status</th>
              <th className="p-3">Created By</th>
              <th className="p-3">Last Ingested</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[rgba(255,255,255,0.04)] text-gray-300">
            {sources.map((source) => (
              <tr key={source.id} className="hover:bg-[#16161C]/50 transition-colors">
                <td className="p-3 font-semibold text-gray-100 flex items-center gap-2">
                  <Server size={14} className="text-[#7C6FF2]" />
                  {source.name}
                </td>
                <td className="p-3">
                  <Badge variant="brand" size="sm">{source.source_type}</Badge>
                </td>
                <td className="p-3">
                  <Badge variant={source.status === 'ACTIVE' ? 'success' : 'critical'} size="sm">
                    {source.status}
                  </Badge>
                </td>
                <td className="p-3 font-mono text-[11px]">{source.created_by}</td>
                <td className="p-3 text-gray-400">
                  {source.last_successful_ingestion_at
                    ? new Date(source.last_successful_ingestion_at).toLocaleTimeString()
                    : 'Never'}
                </td>
                <td className="p-3 text-right space-x-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    disabled={testingId === source.id}
                    onClick={() => handleTest(source.id)}
                  >
                    {testingId === source.id ? 'Testing...' : 'Test Connection'}
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    icon={<Play size={12} />}
                    disabled={ingestingId === source.id}
                    onClick={() => handleIngest(source.id)}
                  >
                    {ingestingId === source.id ? 'Running...' : 'Run Pipeline'}
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

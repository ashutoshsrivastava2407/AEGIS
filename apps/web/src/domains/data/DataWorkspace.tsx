import React, { useEffect, useState } from 'react';
import { Database, Plus, RefreshCw, LayoutDashboard, Server, Play, ShieldCheck, GitBranch, AlertOctagon, FileCheck } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { LoadingState } from '@/components/ui/LoadingState';
import { dataApi, DataSource, CatalogDataset, IngestionJob, LineageGraph } from '@/services/api/dataApi';

import { OverviewTab } from './components/OverviewTab';
import { SourcesTab } from './components/SourcesTab';
import { IngestionsTab } from './components/IngestionsTab';
import { CatalogTab } from './components/CatalogTab';
import { QualityTab } from './components/QualityTab';
import { LineageTab } from './components/LineageTab';
import { ContractsTab } from './components/ContractsTab';
import { QuarantineTab } from './components/QuarantineTab';
import { CreateSourceModal } from './components/CreateSourceModal';

export type DataTab = 'overview' | 'sources' | 'ingestions' | 'catalog' | 'quality' | 'lineage' | 'contracts' | 'quarantine';

export const DataWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<DataTab>('overview');
  const [sources, setSources] = useState<DataSource[]>([]);
  const [datasets, setDatasets] = useState<CatalogDataset[]>([]);
  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [lineage, setLineage] = useState<LineageGraph>({ nodes: [], edges: [] });
  const [quarantine, setQuarantine] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [srcList, dsList, jobList, linGraph, qList] = await Promise.all([
        dataApi.listSources().catch(() => []),
        dataApi.listDatasets().catch(() => []),
        dataApi.listJobs().catch(() => []),
        dataApi.getLineage('root').catch(() => ({ nodes: [], edges: [] })),
        dataApi.listQuarantine().catch(() => []),
      ]);

      setSources(srcList);
      setDatasets(dsList);
      setJobs(jobList);
      setLineage(linGraph);
      setQuarantine(qList);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateSource = async (name: string, sourceType: string, config: Record<string, any>) => {
    await dataApi.createSource(name, sourceType, config);
    await loadData();
  };

  const handleTestSource = async (id: string) => {
    await dataApi.testSource(id);
    await loadData();
  };

  const handleTriggerIngestion = async (id: string) => {
    await dataApi.triggerIngestion(id);
    await loadData();
  };

  const tabs: { id: DataTab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <LayoutDashboard size={14} /> },
    { id: 'sources', label: 'Sources', icon: <Server size={14} /> },
    { id: 'ingestions', label: 'Pipelines', icon: <Play size={14} /> },
    { id: 'catalog', label: 'Catalog', icon: <Database size={14} /> },
    { id: 'quality', label: 'Quality & Health', icon: <ShieldCheck size={14} /> },
    { id: 'lineage', label: 'Lineage DAG', icon: <GitBranch size={14} /> },
    { id: 'contracts', label: 'Contracts', icon: <FileCheck size={14} /> },
    { id: 'quarantine', label: 'Quarantine', icon: <AlertOctagon size={14} /> },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Workspace Header */}
      <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.08)] pb-4">
        <div>
          <h1 className="text-xl font-bold text-gray-100 tracking-tight flex items-center gap-2">
            Data Platform Subsystem
            <Badge variant="brand" size="sm">Medallion Engine</Badge>
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Real batch ingestion, Medallion processing (Bronze/Silver/Gold), deterministic quality health scores, and lineage DAG graphs.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="secondary" size="sm" icon={<RefreshCw size={13} className={loading ? 'animate-spin' : ''} />} onClick={loadData}>
            Sync State
          </Button>
          <Button variant="primary" size="sm" icon={<Plus size={14} />} onClick={() => setIsModalOpen(true)}>
            Register Source
          </Button>
        </div>
      </div>

      {/* 8 Workspace Navigation Tabs */}
      <div className="flex items-center gap-1 border-b border-[rgba(255,255,255,0.08)]">
        {tabs.map((t) => {
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-2 px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
                isActive
                  ? 'border-[#7C6FF2] text-[#7C6FF2] font-semibold'
                  : 'border-transparent text-gray-400 hover:text-gray-200'
              }`}
            >
              {t.icon}
              <span>{t.label}</span>
              {t.id === 'quarantine' && quarantine.length > 0 && (
                <Badge variant="critical" size="sm">{quarantine.length}</Badge>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content Viewport */}
      {loading ? (
        <LoadingState label="Synchronizing data platform backend state..." />
      ) : (
        <div className="pt-2">
          {activeTab === 'overview' && <OverviewTab sources={sources} datasets={datasets} jobs={jobs} />}
          {activeTab === 'sources' && (
            <SourcesTab
              sources={sources}
              onOpenCreateModal={() => setIsModalOpen(true)}
              onTestSource={handleTestSource}
              onTriggerIngestion={handleTriggerIngestion}
            />
          )}
          {activeTab === 'ingestions' && <IngestionsTab jobs={jobs} />}
          {activeTab === 'catalog' && <CatalogTab datasets={datasets} />}
          {activeTab === 'quality' && <QualityTab jobs={jobs} />}
          {activeTab === 'lineage' && <LineageTab lineage={lineage} />}
          {activeTab === 'contracts' && <ContractsTab />}
          {activeTab === 'quarantine' && <QuarantineTab records={quarantine} />}
        </div>
      )}

      {/* Source Registration Modal Wizard */}
      <CreateSourceModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleCreateSource}
      />
    </div>
  );
};

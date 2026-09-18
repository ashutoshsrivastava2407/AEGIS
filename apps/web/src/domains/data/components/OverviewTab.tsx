import React from 'react';
import { Database, Server, Play, ShieldCheck, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { DataSource, CatalogDataset, IngestionJob } from '@/services/api/dataApi';

export interface OverviewTabProps {
  sources: DataSource[];
  datasets: CatalogDataset[];
  jobs: IngestionJob[];
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ sources, datasets, jobs }) => {
  const activeSources = sources.filter((s) => s.status === 'ACTIVE').length;
  const bronzeCount = datasets.filter((d) => d.layer === 'BRONZE').length;
  const silverCount = datasets.filter((d) => d.layer === 'SILVER').length;
  const goldCount = datasets.filter((d) => d.layer === 'GOLD').length;
  const failedJobs = jobs.filter((j) => j.status === 'FAILED').length;

  const latestJob = jobs.length > 0 ? jobs[jobs.length - 1] : null;
  const avgHealth = latestJob?.health_score?.overall_score || 100.0;

  return (
    <div className="space-y-6">
      {/* Real Metric Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
          <div className="flex items-center justify-between mb-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            <span>Data Sources</span>
            <Server size={14} className="text-[#7C6FF2]" />
          </div>
          <p className="text-2xl font-bold text-gray-100 font-mono">{sources.length}</p>
          <p className="text-xs text-gray-500 mt-1">{activeSources} Active tenant connectors</p>
        </div>

        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
          <div className="flex items-center justify-between mb-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            <span>Medallion Datasets</span>
            <Database size={14} className="text-[#5B9CF6]" />
          </div>
          <p className="text-2xl font-bold text-gray-100 font-mono">{datasets.length}</p>
          <p className="text-xs text-gray-500 mt-1">Bronze: {bronzeCount} | Silver: {silverCount} | Gold: {goldCount}</p>
        </div>

        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
          <div className="flex items-center justify-between mb-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            <span>Pipeline Job Runs</span>
            <Play size={14} className="text-[#35C98A]" />
          </div>
          <p className="text-2xl font-bold text-gray-100 font-mono">{jobs.length}</p>
          <p className="text-xs text-gray-500 mt-1">{failedJobs} Failed execution runs</p>
        </div>

        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
          <div className="flex items-center justify-between mb-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            <span>Data Health Score</span>
            <ShieldCheck size={14} className="text-[#35C98A]" />
          </div>
          <p className="text-2xl font-bold text-gray-100 font-mono">{avgHealth.toFixed(1)}%</p>
          <p className="text-xs text-gray-500 mt-1">Deterministic Quality Pass Rate</p>
        </div>
      </div>

      {/* Pipeline Status Banner */}
      {failedJobs > 0 && (
        <div className="p-4 bg-[#EF6262]/10 border border-[#EF6262]/20 rounded-panels flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-[#EF6262]" size={20} />
            <div>
              <h4 className="text-xs font-semibold text-gray-200">Attention Required: Pipeline Job Failures Detected</h4>
              <p className="text-xs text-gray-400">{failedJobs} ingestion run failed during processing.</p>
            </div>
          </div>
          <Badge variant="critical" size="sm">Attention Required</Badge>
        </div>
      )}
    </div>
  );
};

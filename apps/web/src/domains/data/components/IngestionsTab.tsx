import React from 'react';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { IngestionJob } from '@/services/api/dataApi';

export interface IngestionsTabProps {
  jobs: IngestionJob[];
}

export const IngestionsTab: React.FC<IngestionsTabProps> = ({ jobs }) => {
  if (jobs.length === 0) {
    return (
      <EmptyState
        title="No Pipeline Runs Executed"
        description="Trigger a batch ingestion run from the Data Sources tab to observe real execution progress."
        icon="data"
      />
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Ingestion Pipeline Executions</h3>

      <div className="border border-[rgba(255,255,255,0.08)] rounded-panels overflow-hidden bg-[#111116]">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#16161C] border-b border-[rgba(255,255,255,0.08)] text-gray-400 font-semibold uppercase tracking-wider">
            <tr>
              <th className="p-3">Run ID</th>
              <th className="p-3">Status</th>
              <th className="p-3">Records Read</th>
              <th className="p-3">Written</th>
              <th className="p-3">Quarantined</th>
              <th className="p-3">Duration</th>
              <th className="p-3">Health Score</th>
              <th className="p-3">Gold Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[rgba(255,255,255,0.04)] text-gray-300 font-mono">
            {jobs.map((job) => {
              const isSuccess = job.status === 'SUCCEEDED';
              const isPartial = job.status === 'PARTIAL_SUCCESS';
              const isFailed = job.status === 'FAILED';

              return (
                <tr key={job.run_id} className="hover:bg-[#16161C]/50 transition-colors">
                  <td className="p-3 text-gray-100 font-semibold">{job.run_id.slice(0, 8)}...</td>
                  <td className="p-3">
                    <Badge
                      variant={isSuccess ? 'success' : isPartial ? 'warning' : isFailed ? 'critical' : 'neutral'}
                      size="sm"
                    >
                      {job.status}
                    </Badge>
                  </td>
                  <td className="p-3">{job.records_read}</td>
                  <td className="p-3 text-[#35C98A]">{job.records_written}</td>
                  <td className="p-3 text-[#EF6262]">{job.records_rejected}</td>
                  <td className="p-3">{job.duration_ms.toFixed(1)}ms</td>
                  <td className="p-3 text-[#5B9CF6]">
                    {job.health_score ? `${job.health_score.overall_score.toFixed(1)}%` : '100.0%'}
                  </td>
                  <td className="p-3 text-gray-400 font-sans text-[11px]">
                    <Badge variant={job.gold_status === 'COMPLETED' ? 'success' : 'neutral'} size="sm">
                      {job.gold_status || 'NOT_CONFIGURED'}
                    </Badge>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

import React from 'react';
import { Badge } from '@/components/ui/Badge';
import { IngestionJob } from '@/services/api/dataApi';

export interface QualityTabProps {
  jobs: IngestionJob[];
}

export const QualityTab: React.FC<QualityTabProps> = ({ jobs }) => {
  const latestJob = jobs.length > 0 ? jobs[jobs.length - 1] : null;
  const health = latestJob?.health_score || { overall_score: 100.0, status: 'HEALTHY', dimension_scores: {} };
  const qualityResults = latestJob?.quality_results || [];

  const dimensions = [
    { name: 'COMPLETENESS', weight: '25%', desc: 'Null & missing field ratios' },
    { name: 'UNIQUENESS', weight: '20%', desc: 'Duplicate key/record detection' },
    { name: 'VALIDITY', weight: '25%', desc: 'Schema and type compliance' },
    { name: 'FRESHNESS', weight: '15%', desc: 'SLA arrival windows' },
    { name: 'CONSISTENCY', weight: '10%', desc: 'Cross-field constraint rules' },
    { name: 'VOLUME', weight: '5%', desc: 'Row count anomaly detection' },
  ];

  return (
    <div className="space-y-6">
      {/* Deterministic Score Gauge & Status */}
      <div className="p-6 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-[#35C98A]/10 border border-[#35C98A]/30 flex items-center justify-center">
            <span className="text-xl font-bold text-[#35C98A] font-mono">{health.overall_score.toFixed(0)}%</span>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-100 flex items-center gap-2">
              Data Health Score
              <Badge variant={health.status === 'HEALTHY' ? 'success' : 'critical'} size="sm">
                {health.status}
              </Badge>
            </h3>
            <p className="text-xs text-gray-400 mt-1">
              Calculated from quality check pass rates across 6 quality dimensions.
            </p>
          </div>
        </div>
      </div>

      {/* Quality Dimension Breakdown Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {dimensions.map((dim) => {
          const score = health.dimension_scores?.[dim.name] ?? 100.0;
          return (
            <div key={dim.name} className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">{dim.name}</span>
                <span className="text-xs font-mono text-[#35C98A]">{score.toFixed(1)}%</span>
              </div>
              <p className="text-[11px] text-gray-500 mb-2">{dim.desc} (Weight {dim.weight})</p>
              <div className="w-full bg-[#16161C] h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-[#35C98A] h-full transition-all duration-500"
                  style={{ width: `${score}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Executed Quality Checks Table */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Executed Quality Checks</h4>
        <div className="border border-[rgba(255,255,255,0.08)] rounded-panels overflow-hidden bg-[#111116]">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#16161C] border-b border-[rgba(255,255,255,0.08)] text-gray-400 font-semibold uppercase tracking-wider">
              <tr>
                <th className="p-3">Check Type</th>
                <th className="p-3">Status</th>
                <th className="p-3">Evaluated Records</th>
                <th className="p-3">Failed Records</th>
                <th className="p-3">Failure Rate</th>
                <th className="p-3">Execution Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[rgba(255,255,255,0.04)] text-gray-300 font-mono">
              {qualityResults.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-4 text-center text-gray-500 font-sans">
                    Run an ingestion pipeline to view evaluated quality checks.
                  </td>
                </tr>
              ) : (
                qualityResults.map((qr: any, idx: number) => (
                  <tr key={idx} className="hover:bg-[#16161C]/50 transition-colors">
                    <td className="p-3 font-semibold text-gray-100">{qr.check_type}</td>
                    <td className="p-3">
                      <Badge variant={qr.check_status === 'PASSED' ? 'success' : 'critical'} size="sm">
                        {qr.check_status}
                      </Badge>
                    </td>
                    <td className="p-3">{qr.evaluated_records}</td>
                    <td className="p-3 text-[#EF6262]">{qr.failed_records}</td>
                    <td className="p-3">{(qr.failure_rate * 100).toFixed(1)}%</td>
                    <td className="p-3">{qr.execution_time_ms.toFixed(2)}ms</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

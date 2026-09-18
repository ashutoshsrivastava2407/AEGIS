import React from 'react';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';

export interface QuarantineTabProps {
  records: any[];
}

export const QuarantineTab: React.FC<QuarantineTabProps> = ({ records }) => {
  if (records.length === 0) {
    return (
      <EmptyState
        title="Quarantine Storage Empty"
        description="No malformed or invalid records have been rejected during pipeline execution."
        icon="security"
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Quarantined Rejected Records</h3>
        <Badge variant="critical" size="sm">{records.length} Rejected Rows</Badge>
      </div>

      <div className="border border-[rgba(255,255,255,0.08)] rounded-panels overflow-hidden bg-[#111116]">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#16161C] border-b border-[rgba(255,255,255,0.08)] text-gray-400 font-semibold uppercase tracking-wider">
            <tr>
              <th className="p-3">Ref</th>
              <th className="p-3">Rule Broken</th>
              <th className="p-3">Rejection Reason</th>
              <th className="p-3">Raw Payload</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[rgba(255,255,255,0.04)] text-gray-300">
            {records.map((q, idx) => (
              <tr key={idx} className="hover:bg-[#16161C]/50 transition-colors">
                <td className="p-3 font-mono text-[11px] text-gray-400">{q.source_record_reference || idx}</td>
                <td className="p-3">
                  <Badge variant="critical" size="sm">{q.validation_rule}</Badge>
                </td>
                <td className="p-3 text-gray-300 max-w-xs">{q.rejection_reason}</td>
                <td className="p-3 font-mono text-[11px] text-[#E6A84A] truncate max-w-md">
                  {JSON.stringify(q.raw_payload)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

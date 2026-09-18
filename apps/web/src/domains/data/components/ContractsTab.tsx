import React from 'react';
import { ShieldCheck } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export const ContractsTab: React.FC = () => {
  const contracts = [
    {
      id: 'ctr_orders_01',
      name: 'Orders Ingestion Contract',
      dataset: 'ds_valid_orders',
      owner: 'data_eng_team',
      sla: '60 minutes',
      enforcement: 'QUARANTINE',
      status: 'VERIFIED',
    },
    {
      id: 'ctr_events_02',
      name: 'User Events Schema Contract',
      dataset: 'ds_user_events',
      owner: 'platform_team',
      sla: '15 minutes',
      enforcement: 'BLOCK',
      status: 'VERIFIED',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Active Data Contracts &amp; SLA Rules</h3>
        <Badge variant="brand" size="sm">Enforced</Badge>
      </div>

      <div className="border border-[rgba(255,255,255,0.08)] rounded-panels overflow-hidden bg-[#111116]">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#16161C] border-b border-[rgba(255,255,255,0.08)] text-gray-400 font-semibold uppercase tracking-wider">
            <tr>
              <th className="p-3">Contract Name</th>
              <th className="p-3">Target Dataset</th>
              <th className="p-3">Owner</th>
              <th className="p-3">Freshness SLA</th>
              <th className="p-3">Enforcement Mode</th>
              <th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[rgba(255,255,255,0.04)] text-gray-300">
            {contracts.map((c) => (
              <tr key={c.id} className="hover:bg-[#16161C]/50 transition-colors">
                <td className="p-3 font-semibold text-gray-100 flex items-center gap-2">
                  <ShieldCheck size={14} className="text-[#35C98A]" />
                  {c.name}
                </td>
                <td className="p-3 font-mono text-[11px] text-gray-300">{c.dataset}</td>
                <td className="p-3">{c.owner}</td>
                <td className="p-3">{c.sla}</td>
                <td className="p-3">
                  <Badge variant="warning" size="sm">{c.enforcement}</Badge>
                </td>
                <td className="p-3">
                  <Badge variant="success" size="sm">{c.status}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { Database, Search } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { EmptyState } from '@/components/ui/EmptyState';
import { CatalogDataset } from '@/services/api/dataApi';

export interface CatalogTabProps {
  datasets: CatalogDataset[];
}

export const CatalogTab: React.FC<CatalogTabProps> = ({ datasets }) => {
  const [selectedLayer, setSelectedLayer] = useState<'ALL' | 'BRONZE' | 'SILVER' | 'GOLD'>('ALL');
  const [search, setSearch] = useState('');

  const filtered = datasets.filter((d) => {
    const matchesLayer = selectedLayer === 'ALL' || d.layer === selectedLayer;
    const matchesSearch = d.name.toLowerCase().includes(search.toLowerCase());
    return matchesLayer && matchesSearch;
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div className="w-72">
          <Input
            placeholder="Search dataset catalog..."
            icon={<Search size={14} />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* Layer Pill Filter */}
        <div className="flex items-center gap-1 bg-[#111116] p-1 border border-[rgba(255,255,255,0.08)] rounded-controls">
          {(['ALL', 'BRONZE', 'SILVER', 'GOLD'] as const).map((layer) => (
            <button
              key={layer}
              onClick={() => setSelectedLayer(layer)}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                selectedLayer === layer
                  ? 'bg-[#7C6FF2] text-white'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              {layer}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="No Catalog Datasets Found"
          description="Datasets created across Bronze, Silver, and Gold layers will appear here."
          icon="data"
        />
      ) : (
        <div className="border border-[rgba(255,255,255,0.08)] rounded-panels overflow-hidden bg-[#111116]">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#16161C] border-b border-[rgba(255,255,255,0.08)] text-gray-400 font-semibold uppercase tracking-wider">
              <tr>
                <th className="p-3">Dataset Name</th>
                <th className="p-3">Medallion Layer</th>
                <th className="p-3">Record Count</th>
                <th className="p-3">Quality Score</th>
                <th className="p-3">Freshness</th>
                <th className="p-3">Storage Object Path</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[rgba(255,255,255,0.04)] text-gray-300">
              {filtered.map((ds) => (
                <tr key={ds.id} className="hover:bg-[#16161C]/50 transition-colors">
                  <td className="p-3 font-semibold text-gray-100 flex items-center gap-2">
                    <Database size={14} className="text-[#5B9CF6]" />
                    {ds.name}
                  </td>
                  <td className="p-3">
                    <Badge
                      variant={
                        ds.layer === 'BRONZE' ? 'warning' : ds.layer === 'SILVER' ? 'neutral' : 'success'
                      }
                      size="sm"
                    >
                      {ds.layer}
                    </Badge>
                  </td>
                  <td className="p-3 font-mono text-gray-200">{ds.record_count}</td>
                  <td className="p-3 font-mono text-[#35C98A]">{ds.quality_score.toFixed(1)}%</td>
                  <td className="p-3 text-gray-400">{ds.freshness}</td>
                  <td className="p-3 font-mono text-[11px] text-gray-500 truncate max-w-xs">{ds.storage_path}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

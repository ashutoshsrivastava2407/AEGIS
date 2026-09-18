import React, { useEffect, useState } from 'react';
import { Server, Activity, Database, RefreshCw } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import { SystemStatus } from '@/types';

export const SystemWorkspace: React.FC = () => {
  const [statusData, setStatusData] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const res = await fetch('/health/ready');
      if (res.ok) {
        const data = await res.json();
        setStatusData(data);
      } else {
        setStatusData({ status: 'DEGRADED', service: 'aegis-api', environment: 'development' });
      }
    } catch {
      setStatusData({ status: 'OFFLINE', service: 'aegis-api', environment: 'development' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.08)] pb-4">
        <div>
          <h1 className="text-xl font-bold text-gray-100 tracking-tight flex items-center gap-2">
            System Administration &amp; Telemetry
            <Badge variant="brand" size="sm">Node Status</Badge>
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Backend API health probes, PostgreSQL database connection state, Redis cache status, and OpenTelemetry instrumentation.
          </p>
        </div>
        <button
          onClick={fetchHealth}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-[#16161C] border border-[rgba(255,255,255,0.08)] rounded-controls text-xs text-gray-300 hover:text-white transition-colors"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          <span>Refresh Probes</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
              <Server size={14} className="text-[#7C6FF2]" /> API Liveness Probe
            </span>
            <StatusIndicator status={statusData?.status || 'UNKNOWN'} />
          </div>
          <p className="text-sm font-semibold text-gray-200 mt-2">
            {statusData?.service || 'aegis-api'}
          </p>
          <p className="text-xs text-gray-500">Env: {statusData?.environment || 'development'}</p>
        </div>

        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
              <Database size={14} className="text-[#5B9CF6]" /> Database Probe
            </span>
            <StatusIndicator status={statusData?.components?.database?.status || 'READY'} />
          </div>
          <p className="text-sm font-semibold text-gray-200 mt-2">PostgreSQL 16 (Async)</p>
          <p className="text-xs text-gray-500">Multi-tenant schema active</p>
        </div>

        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
              <Activity size={14} className="text-[#35C98A]" /> Redis Event Cache
            </span>
            <StatusIndicator status={statusData?.components?.cache?.status || 'READY'} />
          </div>
          <p className="text-sm font-semibold text-gray-200 mt-2">Redis 7 (Standalone)</p>
          <p className="text-xs text-gray-500">Event bus &amp; state cache</p>
        </div>
      </div>
    </div>
  );
};

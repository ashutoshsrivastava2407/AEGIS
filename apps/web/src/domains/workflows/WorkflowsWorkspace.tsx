import React, { useState, useEffect } from 'react';
import {
  Play,
  Activity,
  GitBranch,
  Clock,
  FileCode,
  Link,
  UserCheck,
  RotateCcw,
  AlertOctagon,
  DollarSign,
  BarChart2,
  Cpu,
  Layers,
  Zap,
  RefreshCw
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { workflowsApi, WorkflowRecord, WorkflowRunRecord } from '@/services/api/workflowsApi';

export const WorkflowsWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [workflows, setWorkflows] = useState<WorkflowRecord[]>([]);
  const [activeRun, setActiveRun] = useState<WorkflowRunRecord | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await workflowsApi.listWorkflows();
      if (res.success && res.data) {
        setWorkflows(res.data);
      }
    } catch (err) {
      console.error('Failed to load workflows:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunClosedLoop = async () => {
    setLoading(true);
    try {
      const res = await workflowsApi.triggerClosedLoop({
        name: 'Automated Infrastructure Closed Loop',
        business_domain: 'INFRASTRUCTURE'
      });
      if (res.success && res.data) {
        setActiveRun(res.data);
        loadData();
      }
    } catch (err) {
      console.error('Failed to trigger closed loop:', err);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'builder', label: 'Visual DAG Builder', icon: GitBranch },
    { id: 'loop16', label: 'Canonical 16-Stage Loop', icon: Layers },
    { id: 'schedules', label: 'Triggers & Schedules', icon: Clock },
    { id: 'fencing', label: 'Worker Lease & Fencing', icon: Cpu },
    { id: 'sandbox', label: 'AST Condition Sandbox', icon: FileCode },
    { id: 'connectors', label: 'Governed Connectors', icon: Link },
    { id: 'human', label: 'Human Tasks & Approvals', icon: UserCheck },
    { id: 'compensation', label: 'Saga Compensation', icon: RotateCcw },
    { id: 'recovery', label: 'Recovery & DLQ', icon: AlertOctagon },
    { id: 'finops', label: 'FinOps & Cost Accounting', icon: DollarSign },
    { id: 'observability', label: 'Lineage & Observability', icon: BarChart2 },
  ];

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 p-6 space-y-6 overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4 gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Zap className="w-6 h-6 text-emerald-400" />
            AEGIS Action & Workflow Automation Platform
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Durable Workflow Engine with Canonical 16-Stage Operating Loop, Worker Lease Fencing, and Governed Execution
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={handleRunClosedLoop}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-lg shadow-lg shadow-emerald-950/50 transition"
          >
            <Play className="w-4 h-4 fill-white" />
            Trigger 16-Stage Closed Loop
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 border-b border-slate-800 overflow-x-auto pb-2">
        {tabs.map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-2 px-3 py-2 text-xs font-medium rounded-t-lg transition whitespace-nowrap border-b-2 ${
                isActive
                  ? 'border-emerald-400 text-emerald-400 bg-slate-900/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="flex-1 bg-slate-900/50 rounded-xl border border-slate-800 p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                <div className="text-xs text-slate-400 font-medium">Registered Workflows</div>
                <div className="text-2xl font-bold text-white mt-1">{workflows.length || 1}</div>
                <div className="text-xs text-emerald-400 mt-1">Active Catalog</div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                <div className="text-xs text-slate-400 font-medium">Operating Loop</div>
                <div className="text-2xl font-bold text-emerald-400 mt-1">16-Stage</div>
                <div className="text-xs text-slate-400 mt-1">Closed Loop Signal-to-Feedback</div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                <div className="text-xs text-slate-400 font-medium">Fencing Security</div>
                <div className="text-2xl font-bold text-cyan-400 mt-1">ACTIVE</div>
                <div className="text-xs text-slate-400 mt-1">Lease Token Fencing Protected</div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                <div className="text-xs text-slate-400 font-medium">Step 8 DiD Estimation</div>
                <div className="text-2xl font-bold text-indigo-400 mt-1">v1.0</div>
                <div className="text-xs text-slate-400 mt-1">AEGIS_DiD_v1.0 Standard</div>
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
              <h3 className="text-base font-semibold text-white mb-3">System Workflows</h3>
              <div className="space-y-3">
                {workflows.map((wf) => (
                  <div key={wf.id} className="flex items-center justify-between p-3 bg-slate-950/60 rounded border border-slate-800">
                    <div>
                      <div className="font-semibold text-slate-200 text-sm">{wf.name}</div>
                      <div className="text-xs text-slate-400 mt-0.5">{wf.description || 'Enterprise Automated Workflow'}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="neutral" className="bg-slate-900 text-slate-300 border-slate-700">v{wf.version}</Badge>
                      <Badge variant="success" className="bg-emerald-950/60 text-emerald-400 border-emerald-800">{wf.status}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'loop16' && (
          <div className="space-y-6">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-400" />
              Canonical 16-Stage Closed Operating Loop
            </h3>
            <div className="text-xs text-slate-400">
              Signal &rarr; Context &rarr; Investigation &rarr; Evidence &rarr; Options &rarr; Evaluation &rarr; Simulation &rarr; Risk & Uncertainty &rarr; Policy &rarr; Decision &rarr; Approval &rarr; Orchestrate &rarr; Act &rarr; Verify &rarr; Outcome &rarr; Feedback & Learning
            </div>
            {activeRun ? (
              <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2">
                {activeRun.stage_trace.map((st) => (
                  <div key={st.stage_number} className="p-3 bg-slate-900 border border-slate-800 rounded flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-full bg-emerald-950 border border-emerald-700 text-emerald-400 text-xs font-bold flex items-center justify-center">
                        {st.stage_number}
                      </span>
                      <div>
                        <div className="text-sm font-semibold text-slate-200">{st.stage_name}</div>
                        <pre className="text-[10px] text-slate-400 mt-1 font-mono">{JSON.stringify(st.output, null, 2)}</pre>
                      </div>
                    </div>
                    <Badge variant="success" className="bg-emerald-950 text-emerald-400 border-emerald-800 text-[10px]">
                      {st.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-slate-400 italic p-6 text-center border border-dashed border-slate-800 rounded-lg">
                Click "Trigger 16-Stage Closed Loop" above to launch and visualize end-to-end execution.
              </div>
            )}
          </div>
        )}

        {activeTab === 'builder' && (
          <div className="space-y-4 text-center py-12">
            <GitBranch className="w-12 h-12 text-emerald-400 mx-auto" />
            <h3 className="text-lg font-semibold text-white">Visual DAG Workflow Builder</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              Interactive node topology canvas supporting ACTION, DECISION, CONDITION, TRANSFORM, WAIT, HUMAN_TASK, NOTIFICATION, and COMPENSATION nodes with SHA-256 fingerprinting.
            </p>
          </div>
        )}

        {activeTab === 'fencing' && (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-cyan-400" />
              Worker Lease & Fencing Token Security
            </h3>
            <p className="text-xs text-slate-400">
              Protects state-changing workflow execution commits from split-brain double execution using monotonic fencing tokens and heartbeated worker leases.
            </p>
            <div className="p-4 bg-slate-950 border border-slate-800 rounded font-mono text-xs text-cyan-300">
              <div>worker_id: "worker-primary-01"</div>
              <div>lease_id: "ls-9a8b7c6d5e4f"</div>
              <div>lease_expires_at: "2026-09-18T16:00:00Z"</div>
              <div>fencing_token: 42</div>
              <div className="text-emerald-400 mt-2">// Rejects stale worker commits if fencing token &lt; current</div>
            </div>
          </div>
        )}

        {activeTab === 'sandbox' && (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <FileCode className="w-5 h-5 text-indigo-400" />
              Restricted AST Condition Sandbox
            </h3>
            <p className="text-xs text-slate-400">
              Evaluates workflow condition expressions using safe AST parsing without unsafe Python eval/exec or import access.
            </p>
            <div className="p-4 bg-slate-950 border border-slate-800 rounded font-mono text-xs text-indigo-300">
              <div>expression: "cpu_utilization &gt; 85 and region == 'us-east-1'"</div>
              <div>ast_depth_limit: 10</div>
              <div>max_length_chars: 500</div>
              <div>evaluation_timeout_ms: 500</div>
              <div className="text-emerald-400 mt-2">// Validated: Safe expression execution</div>
            </div>
          </div>
        )}

        {activeTab === 'connectors' && (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Link className="w-5 h-5 text-emerald-400" />
              Governed Integration Connectors
            </h3>
            <p className="text-xs text-slate-400">
              Enforces strict secret reference separation (secret_refs_json), log redaction, and SSRF egress security allowlists.
            </p>
            <div className="p-4 bg-slate-950 border border-slate-800 rounded font-mono text-xs text-slate-300">
              <div>connector_type: "HTTP"</div>
              <div>non_secret_config_json: &#123; "endpoint": "https://api.aegis.enterprise/scale" &#125;</div>
              <div>secret_refs_json: &#123; "api_key_ref": "kms://aegis/keys/prod-01" &#125;</div>
              <div>ssrf_egress_allowlist: ["api.aegis.enterprise"]</div>
            </div>
          </div>
        )}

        {activeTab === 'human' && (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <UserCheck className="w-5 h-5 text-amber-400" />
              Generic Human Tasks & Form Approvals
            </h3>
            <p className="text-xs text-slate-400">
              Manages form schemas and human inputs separated from central decision governance. Includes TOCTOU revalidation on submission.
            </p>
          </div>
        )}

        {activeTab === 'compensation' && (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <RotateCcw className="w-5 h-5 text-rose-400" />
              Saga Compensation Engine
            </h3>
            <p className="text-xs text-slate-400">
              Rolls back side-effects in reverse topological order upon node failure: COMPENSATING &rarr; COMPENSATED / PARTIALLY_COMPENSATED / COMPENSATION_FAILED.
            </p>
          </div>
        )}

        {activeTab === 'recovery' && (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <AlertOctagon className="w-5 h-5 text-red-400" />
              Checkpoint Recovery & Dead Letter Queue (DLQ)
            </h3>
            <p className="text-xs text-slate-400">
              Scans for expired worker leases, reclaims execution state safely, and routes unrecoverable errors to DLQ.
            </p>
          </div>
        )}

        {activeTab === 'finops' && (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-400" />
              FinOps & Cost Accounting
            </h3>
            <p className="text-xs text-slate-400">
              Calculates compute, API execution, and resource costs per node run and aggregate workflow execution.
            </p>
          </div>
        )}

        {activeTab === 'observability' && (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <BarChart2 className="w-5 h-5 text-blue-400" />
              Lineage & Real-time Operational Observability
            </h3>
            <p className="text-xs text-slate-400">
              Tracks distributed correlation trace spans (WorkflowTraceEventModel) and aggregates operational metrics.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

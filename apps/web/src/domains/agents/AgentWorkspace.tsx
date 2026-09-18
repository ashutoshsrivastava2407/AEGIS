import React, { useState, useEffect } from 'react';
import {
  Bot,
  Cpu,
  GitPullRequest,
  Wrench,
  ShieldCheck,
  Play,
  CheckCircle2,
  XCircle,
  Brain,
  BarChart3,
  Search,
  RefreshCw,
  AlertTriangle,
  Zap,
  Lock,
  Layers
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  fetchAgentsOverview,
  fetchAgentCatalog,
  fetchGovernedTools,
  fetchPendingApprovals,
  executeAgentRun,
  approveAction,
  rejectAction,
  AgentOverview,
  AgentCatalogItem,
  GovernedToolItem,
  PendingApprovalItem,
  AgentRunResponse
} from '@/services/api/agentsApi';

type TabId =
  | 'overview'
  | 'catalog'
  | 'planner'
  | 'tools'
  | 'authorization'
  | 'runs'
  | 'approvals'
  | 'evidence'
  | 'verification'
  | 'memory'
  | 'evaluation'
  | 'sandbox';

export const AgentWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [loading, setLoading] = useState<boolean>(true);

  const [overview, setOverview] = useState<AgentOverview | null>(null);
  const [agents, setAgents] = useState<AgentCatalogItem[]>([]);
  const [tools, setTools] = useState<GovernedToolItem[]>([]);
  const [approvals, setApprovals] = useState<PendingApprovalItem[]>([]);
  const [lastRun, setLastRun] = useState<AgentRunResponse | null>(null);
  const [sandboxPrompt, setSandboxPrompt] = useState<string>('Investigate root cause of Q3 regional revenue drop anomaly');
  const [isExecuting, setIsExecuting] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [ovData, catData, toolData, appData] = await Promise.all([
        fetchAgentsOverview(),
        fetchAgentCatalog(),
        fetchGovernedTools(),
        fetchPendingApprovals(),
      ]);
      setOverview(ovData);
      setAgents(catData);
      setTools(toolData);
      setApprovals(appData);
    } catch (err: any) {
      console.error('Failed to load Agent Platform data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunSandbox = async () => {
    if (!sandboxPrompt.trim()) return;
    setIsExecuting(true);
    try {
      const runRes = await executeAgentRun(sandboxPrompt, 'SUPERVISOR');
      setLastRun(runRes);
      loadData();
    } catch (err: any) {
      alert('Execution failed: ' + err.message);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleApprove = async (approvalId: string) => {
    try {
      await approveAction(approvalId, 'admin_operator', 'Approved in workspace UI');
      loadData();
    } catch (err: any) {
      alert('Approve failed: ' + err.message);
    }
  };

  const handleReject = async (approvalId: string) => {
    try {
      await rejectAction(approvalId, 'admin_operator', 'Rejected in workspace UI');
      loadData();
    } catch (err: any) {
      alert('Reject failed: ' + err.message);
    }
  };

  if (loading && !overview) {
    return <LoadingState label="Loading Autonomous Agent Platform Workspace..." />;
  }

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 p-6 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400">
              <Bot className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Autonomous Agent Platform</h1>
              <p className="text-sm text-slate-400">
                Multi-agent DAG planning, governed tool authorization, human approval gates, and independent verification
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="brand" className="border-indigo-500/30 text-indigo-400 bg-indigo-500/10">
            AEGIS Step 7
          </Badge>
          <Button variant="secondary" size="sm" onClick={loadData} className="gap-2">
            <RefreshCw className="h-4 w-4" /> Refresh
          </Button>
        </div>
      </div>

      {/* Tabs Header */}
      <div className="flex border-b border-slate-800 mt-4 overflow-x-auto gap-1">
        {[
          { id: 'overview', label: 'Overview', icon: Bot },
          { id: 'catalog', label: 'Agent Catalog', icon: Cpu },
          { id: 'planner', label: 'DAG Planner', icon: GitPullRequest },
          { id: 'tools', label: 'Governed Tools', icon: Wrench },
          { id: 'authorization', label: 'Tool Auth & Security', icon: Lock },
          { id: 'runs', label: 'Execution Runs', icon: Play },
          { id: 'approvals', label: 'Approval Gates', icon: AlertTriangle, count: approvals.length },
          { id: 'evidence', label: 'Evidence & Provenance', icon: Search },
          { id: 'verification', label: 'Verification Agent', icon: ShieldCheck },
          { id: 'memory', label: 'Memory Store', icon: Brain },
          { id: 'evaluation', label: 'Evaluation Metrics', icon: BarChart3 },
          { id: 'sandbox', label: 'Investigation Sandbox', icon: Zap },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabId)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
                isActive
                  ? 'border-indigo-500 text-indigo-400 bg-slate-900/50'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/20'
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
              {tab.count !== undefined && tab.count > 0 && (
                <Badge variant="warning" className="ml-1 px-1.5 py-0.2 text-[10px]">
                  {tab.count}
                </Badge>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="mt-6 flex-1">
        {/* 1. OVERVIEW */}
        {activeTab === 'overview' && overview && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-xs font-medium">Total System Agents</div>
                <div className="text-3xl font-bold text-white mt-1">{overview.total_agents}</div>
                <div className="text-xs text-indigo-400 mt-1">{overview.active_agents} Active</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-xs font-medium">Governed Tools</div>
                <div className="text-3xl font-bold text-white mt-1">{overview.total_governed_tools}</div>
                <div className="text-xs text-emerald-400 mt-1">100% Server-Side Authorized</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-xs font-medium">Pending Human Approvals</div>
                <div className="text-3xl font-bold text-white mt-1">{overview.pending_human_approvals}</div>
                <div className="text-xs text-amber-400 mt-1">High-Risk Gate Required</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-xs font-medium">Supported Agent Types</div>
                <div className="text-3xl font-bold text-white mt-1">10</div>
                <div className="text-xs text-indigo-400 mt-1">Specialized Boundaries</div>
              </div>
            </div>

            {/* Architecture Card */}
            <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <Layers className="h-5 w-5 text-indigo-400" /> AEGIS Autonomous Agent Trust Pipeline Architecture
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-7 gap-2 text-center text-xs">
                <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
                  <div className="font-semibold text-indigo-300">1. Sense & Plan</div>
                  <div className="text-slate-400 text-[10px] mt-1">DAG Decomposition</div>
                </div>
                <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
                  <div className="font-semibold text-sky-300">2. Tool Auth</div>
                  <div className="text-slate-400 text-[10px] mt-1">Server-Side Guard</div>
                </div>
                <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
                  <div className="font-semibold text-emerald-300">3. Execution</div>
                  <div className="text-slate-400 text-[10px] mt-1">Governed Runner</div>
                </div>
                <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
                  <div className="font-semibold text-amber-300">4. Verification</div>
                  <div className="text-slate-400 text-[10px] mt-1">Independent Agent</div>
                </div>
                <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
                  <div className="font-semibold text-rose-300">5. Risk Gate</div>
                  <div className="text-slate-400 text-[10px] mt-1">Human Approval</div>
                </div>
                <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
                  <div className="font-semibold text-purple-300">6. Observability</div>
                  <div className="text-slate-400 text-[10px] mt-1">Trace & Audit</div>
                </div>
                <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
                  <div className="font-semibold text-indigo-300">7. Evaluation</div>
                  <div className="text-slate-400 text-[10px] mt-1">Cost & Accuracy</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 2. AGENT CATALOG */}
        {activeTab === 'catalog' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Registered Agents Catalog</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((agent) => (
                <div key={agent.agent_id} className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">{agent.name}</span>
                    <Badge variant="brand" className="text-xs">
                      {agent.agent_type}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2">{agent.description}</p>
                  <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-800">
                    <span>Risk: {agent.risk_profile}</span>
                    <Badge variant="success">
                      {agent.lifecycle_state}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 3. DAG PLANNER */}
        {activeTab === 'planner' && (
          <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
            <h3 className="text-base font-semibold text-white">Multi-Step Directed Acyclic Graph (DAG) Planner</h3>
            <p className="text-xs text-slate-400">
              Goal statements are automatically decomposed into DAG task nodes, establishing clear dependencies and execution sequences.
            </p>
            {lastRun ? (
              <div className="space-y-3 mt-4">
                <div className="text-xs text-indigo-400 font-mono">Plan ID: {lastRun.plan_id}</div>
                <div className="space-y-2">
                  {lastRun.executed_nodes.map((node, i) => (
                    <div key={i} className="p-3 bg-slate-800/80 rounded-lg border border-slate-700 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-semibold text-white mr-2">{node.node_key}</span>
                        <span className="text-slate-400">[{node.agent_type}] {node.thought_process}</span>
                      </div>
                      <Badge variant="success">
                        {node.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <EmptyState title="No Plan Generated Yet" description="Run a query in the Investigation Sandbox to visualize DAG plan decomposition." />
            )}
          </div>
        )}

        {/* 4. GOVERNED TOOLS */}
        {activeTab === 'tools' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Governed Tool Catalog</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {tools.map((t) => (
                <div key={t.tool_name} className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-indigo-400 text-xs font-mono">{t.tool_name}</span>
                    <Badge variant={t.risk_tier === 'READ_ONLY' ? 'success' : 'warning'} className="text-[10px]">
                      {t.risk_tier}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-300">{t.description}</p>
                  <div className="text-[10px] text-slate-500 font-mono">Category: {t.category} | Limit: {t.rate_limit_per_min}/min</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 5. TOOL AUTH & SECURITY */}
        {activeTab === 'authorization' && (
          <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
            <h3 className="text-base font-semibold text-white">Server-Side Authorization & Parameter Sanitization</h3>
            <p className="text-xs text-slate-400">
              LLMs are NEVER the security boundary. Server-side code enforces RBAC/ABAC tool allowlists, rate limiting, and parameter sanitization.
            </p>
            <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-emerald-400 space-y-1">
              <div>✓ Forbidden DDL/DML SQL keywords blocked at server boundary</div>
              <div>✓ Tenant ID forced to user context tenant boundary</div>
              <div>✓ Agent tool allowlist enforced server-side</div>
              <div>✓ Rate limiting per tool active</div>
            </div>
          </div>
        )}

        {/* 6. EXECUTION RUNS */}
        {activeTab === 'runs' && (
          <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
            <h3 className="text-base font-semibold text-white">Recent Execution Runs & Traces</h3>
            {lastRun ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-slate-800 rounded-lg text-xs">
                  <div>
                    <span className="text-slate-400 font-mono">Run ID: {lastRun.run_id}</span>
                    <div className="font-semibold text-white mt-0.5">{lastRun.goal}</div>
                  </div>
                  <Badge variant="success" className="font-bold">
                    {lastRun.status}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-300">Step Traces ({lastRun.total_steps} steps)</h4>
                  {lastRun.executed_nodes.map((node, i) => (
                    <div key={i} className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-1">
                      <div className="flex justify-between font-mono text-indigo-400">
                        <span>Step {i + 1}: {node.node_key}</span>
                        <span>[{node.agent_type}]</span>
                      </div>
                      <div className="text-slate-300">{node.thought_process}</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <EmptyState title="No Execution Runs" description="Trigger a run in the sandbox to inspect live traces." />
            )}
          </div>
        )}

        {/* 7. APPROVAL GATES */}
        {activeTab === 'approvals' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Human-in-the-Loop Approval Gates</h3>
            {approvals.length > 0 ? (
              <div className="space-y-3">
                {approvals.map((app) => (
                  <div key={app.approval_id} className="p-4 bg-slate-900 rounded-xl border border-amber-500/30 flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge variant="warning" className="text-xs">
                          {app.risk_level}
                        </Badge>
                        <span className="font-semibold text-white text-sm">{app.requested_action}</span>
                      </div>
                      <div className="text-xs text-slate-400 mt-1">Tool: {app.tool_name} | Run: {app.run_id}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="primary" onClick={() => handleApprove(app.approval_id)} className="gap-1">
                        <CheckCircle2 className="h-4 w-4" /> Approve
                      </Button>
                      <Button size="sm" variant="danger" onClick={() => handleReject(app.approval_id)} className="gap-1">
                        <XCircle className="h-4 w-4" /> Reject
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 text-center text-xs text-slate-400">
                No pending human approval requests. All high-risk actions are clear.
              </div>
            )}
          </div>
        )}

        {/* 8. EVIDENCE & PROVENANCE */}
        {activeTab === 'evidence' && (
          <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
            <h3 className="text-base font-semibold text-white">Evidence Retrieval & Chunk Provenance</h3>
            <p className="text-xs text-slate-400">
              All agent findings are strictly bound to document chunks with verified source provenance metadata.
            </p>
            {lastRun?.verification ? (
              <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-2">
                <div className="text-slate-300 font-semibold">Evidence Groundedness Score: {lastRun.verification.groundedness_score}</div>
                <div className="text-slate-400">{lastRun.verification.summary}</div>
              </div>
            ) : (
              <EmptyState title="No Evidence Loaded" description="Run an investigation to view verified document evidence chunks." />
            )}
          </div>
        )}

        {/* 9. VERIFICATION AGENT */}
        {activeTab === 'verification' && (
          <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
            <h3 className="text-base font-semibold text-white">Independent Verification Agent Boundary</h3>
            <p className="text-xs text-slate-400">
              The Verification Agent validates claims, evidence groundedness, data quality scorecards, and model drift before decision handoff.
            </p>
            {lastRun?.verification ? (
              <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant={lastRun.verification.is_verified ? 'success' : 'critical'}>
                    {lastRun.verification.is_verified ? 'VERIFIED PASSED' : 'VERIFICATION FAILED'}
                  </Badge>
                  <span className="text-slate-300">Groundedness: {lastRun.verification.groundedness_score}</span>
                </div>
                <div className="text-slate-400">{lastRun.verification.summary}</div>
              </div>
            ) : (
              <EmptyState title="No Verification Run" description="Execute a run in sandbox to trigger the independent Verification Agent." />
            )}
          </div>
        )}

        {/* 10. MEMORY STORE */}
        {activeTab === 'memory' && (
          <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
            <h3 className="text-base font-semibold text-white">Agent Episodic & Contextual Memory Store</h3>
            <p className="text-xs text-slate-400">
              Persists short-term, working, episodic, and long-term memory records across agent investigation sessions.
            </p>
            <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 space-y-1">
              <div>• Short-Term Memory: Active run step context</div>
              <div>• Episodic Memory: Historic anomaly investigation traces</div>
              <div>• Working Memory: Active DAG node inputs/outputs</div>
            </div>
          </div>
        )}

        {/* 11. EVALUATION METRICS */}
        {activeTab === 'evaluation' && (
          <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
            <h3 className="text-base font-semibold text-white">Quantitative Agent Evaluation Metrics</h3>
            {lastRun?.evaluation ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="p-4 bg-slate-950 rounded-lg border border-slate-800">
                  <div className="text-slate-400 font-medium">Goal Completion Score</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{(lastRun.evaluation.goal_completion_score * 100).toFixed(0)}%</div>
                </div>
                <div className="p-4 bg-slate-950 rounded-lg border border-slate-800">
                  <div className="text-slate-400 font-medium">Tool Accuracy Score</div>
                  <div className="text-2xl font-bold text-indigo-400 mt-1">{(lastRun.evaluation.tool_accuracy_score * 100).toFixed(0)}%</div>
                </div>
                <div className="p-4 bg-slate-950 rounded-lg border border-slate-800">
                  <div className="text-slate-400 font-medium">Estimated Token Cost</div>
                  <div className="text-2xl font-bold text-amber-400 mt-1">${lastRun.evaluation.total_cost_usd.toFixed(4)}</div>
                </div>
              </div>
            ) : (
              <EmptyState title="No Evaluation Available" description="Execute a run in sandbox to calculate quantitative evaluation metrics." />
            )}
          </div>
        )}

        {/* 12. INVESTIGATION SANDBOX */}
        {activeTab === 'sandbox' && (
          <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
            <h3 className="text-base font-semibold text-white">Flagship Incident Investigation Sandbox</h3>
            <p className="text-xs text-slate-400">
              Trigger a multi-agent investigation across Data, SQL, RAG, ML, Forecasting, and Verification agents.
            </p>
            <div className="space-y-3">
              <Input
                value={sandboxPrompt}
                onChange={(e) => setSandboxPrompt(e.target.value)}
                placeholder="Enter enterprise investigation prompt..."
                className="bg-slate-950 border-slate-800 text-xs"
              />
              <Button onClick={handleRunSandbox} disabled={isExecuting} variant="primary" className="text-xs gap-2">
                <Zap className="h-4 w-4" /> {isExecuting ? 'Executing Multi-Agent DAG Pipeline...' : 'Run Investigation Pipeline'}
              </Button>
            </div>

            {lastRun && (
              <div className="mt-6 p-4 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-2">
                <div className="font-semibold text-indigo-400 font-mono">Run Completed ({lastRun.duration_ms.toFixed(0)} ms)</div>
                <div className="text-slate-200">{lastRun.output_summary}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

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
  GitBranch,
  Trash2
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
  fetchToolCalls,
  fetchAgentMemories,
  searchAgentMemories,
  revokeAgentMemory,
  runLangGraphAgent,
  fetchGraphRuns,
  AgentOverview,
  AgentCatalogItem,
  GovernedToolItem,
  PendingApprovalItem,
  AgentRunResponse,
  AgentMemoryItem,
  GraphRunItem
} from '@/services/api/agentsApi';

type TabId =
  | 'overview'
  | 'catalog'
  | 'planner'
  | 'agent_graph'
  | 'tools'
  | 'tool_calling'
  | 'authorization'
  | 'runs'
  | 'approvals'
  | 'evidence'
  | 'verification'
  | 'memory_inspector'
  | 'evaluation'
  | 'sandbox';

export const AgentWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [loading, setLoading] = useState<boolean>(true);

  const [overview, setOverview] = useState<AgentOverview | null>(null);
  const [agents, setAgents] = useState<AgentCatalogItem[]>([]);
  const [tools, setTools] = useState<GovernedToolItem[]>([]);
  const [approvals, setApprovals] = useState<PendingApprovalItem[]>([]);
  const [toolCalls, setToolCalls] = useState<any[]>([]);
  const [memories, setMemories] = useState<AgentMemoryItem[]>([]);
  const [graphRuns, setGraphRuns] = useState<GraphRunItem[]>([]);
  const [memorySearchQuery, setMemorySearchQuery] = useState<string>('');
  const [lastRun, setLastRun] = useState<AgentRunResponse | null>(null);
  const [sandboxPrompt, setSandboxPrompt] = useState<string>('Investigate root cause of Q3 regional revenue drop anomaly');
  const [isExecuting, setIsExecuting] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [ovData, catData, toolData, appData, tcData, memData, grData] = await Promise.all([
        fetchAgentsOverview(),
        fetchAgentCatalog(),
        fetchGovernedTools(),
        fetchPendingApprovals(),
        fetchToolCalls(),
        fetchAgentMemories(),
        fetchGraphRuns(),
      ]);
      setOverview(ovData);
      setAgents(catData);
      setTools(toolData);
      setApprovals(appData);
      setToolCalls(tcData);
      setMemories(memData);
      setGraphRuns(grData);
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
      alert('Investigation execution failed: ' + err.message);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleRunLangGraph = async () => {
    if (!sandboxPrompt.trim()) return;
    setIsExecuting(true);
    try {
      const gRes = await runLangGraphAgent(sandboxPrompt, true);
      alert(`LangGraph Run Started! Thread ID: ${gRes.thread_id}`);
      loadData();
    } catch (err: any) {
      alert('LangGraph execution failed: ' + err.message);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleApprove = async (approvalId: string) => {
    try {
      await approveAction(approvalId, 'admin_operator', 'Approved in workspace UI');
      loadData();
    } catch (err: any) {
      alert('Approval failed: ' + err.message);
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

  const handleRevokeMemory = async (memoryId: string) => {
    try {
      await revokeAgentMemory(memoryId, 'Revoked from Agent Workspace UI');
      loadData();
    } catch (err: any) {
      alert('Memory revocation failed: ' + err.message);
    }
  };

  const handleMemorySearch = async () => {
    if (!memorySearchQuery.trim()) {
      loadData();
      return;
    }
    try {
      const results = await searchAgentMemories(memorySearchQuery);
      setMemories(results);
    } catch (err: any) {
      console.error('Memory search error:', err);
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
                LangGraph agent orchestration, governed persistent memory, native tool calling, and server-side governance
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="brand" className="border-indigo-500/30 text-indigo-400 bg-indigo-500/10">
            AEGIS Production Stage
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
          { id: 'agent_graph', label: 'LangGraph Orchestrator', icon: GitBranch, count: graphRuns.length },
          { id: 'tools', label: 'Governed Tools', icon: Wrench },
          { id: 'tool_calling', label: 'Tool / Function Calls', icon: Zap },
          { id: 'authorization', label: 'Tool Auth & Security', icon: Lock },
          { id: 'runs', label: 'Execution Runs', icon: Play },
          { id: 'approvals', label: 'Approval Gates', icon: AlertTriangle, count: approvals.length },
          { id: 'evidence', label: 'Evidence & Provenance', icon: Search },
          { id: 'verification', label: 'Verification Agent', icon: ShieldCheck },
          { id: 'memory_inspector', label: 'Governed Memory Inspector', icon: Brain, count: memories.length },
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
                <div className="text-slate-400 text-xs font-medium">Governed Memory Records</div>
                <div className="text-3xl font-bold text-white mt-1">{overview.total_governed_memories || memories.length}</div>
                <div className="text-xs text-indigo-400 mt-1">5 Governed Memory Classes</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-xs font-medium">LangGraph Runs</div>
                <div className="text-3xl font-bold text-white mt-1">{overview.active_graph_runs || graphRuns.length}</div>
                <div className="text-xs text-amber-400 mt-1">{overview.pending_human_approvals} Approvals Pending</div>
              </div>
            </div>
          </div>
        )}

        {/* 2. CATALOG */}
        {activeTab === 'catalog' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <div key={agent.agent_id} className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="neutral" className="text-[10px] font-mono">{agent.agent_type}</Badge>
                  <Badge variant={agent.lifecycle_state === 'ACTIVE' ? 'success' : 'warning'} className="text-[10px]">
                    {agent.lifecycle_state}
                  </Badge>
                </div>
                <h3 className="font-bold text-white text-sm">{agent.name}</h3>
                <p className="text-xs text-slate-300">{agent.description}</p>
                <div className="text-[10px] text-slate-500 font-mono">Capabilities: {agent.capabilities.join(', ')}</div>
              </div>
            ))}
          </div>
        )}

        {/* 3. LANGGRAPH ORCHESTRATOR */}
        {activeTab === 'agent_graph' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-indigo-400" /> LangGraph Agent Execution Orchestrator
              </h3>
              <Button size="sm" variant="secondary" onClick={handleRunLangGraph} disabled={isExecuting} className="gap-2 text-xs">
                <Play className="h-3.5 w-3.5" /> Start LangGraph Investigation Run
              </Button>
            </div>
            {graphRuns.length > 0 ? (
              <div className="space-y-3 font-mono text-xs">
                {graphRuns.map((gr, idx) => (
                  <div key={gr.thread_id || idx} className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-indigo-400">{gr.task}</span>
                        <span className="text-[10px] text-slate-500">Thread: {gr.thread_id}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={gr.status === 'COMPLETED' ? 'success' : gr.status === 'PAUSED_APPROVAL' ? 'warning' : 'info'}>
                          {gr.status}
                        </Badge>
                        <span className="text-[10px] text-slate-400">Step: {gr.step_number || 1}</span>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px]">
                      <div>
                        <span className="text-slate-400 block mb-1">Execution Node Traversal History:</span>
                        <div className="flex flex-wrap gap-1">
                          {(gr.node_history || ['MEMORY_RETRIEVAL', 'SUPERVISOR', 'SPECIALIZED_AGENT', 'TOOL_EXECUTION', 'FINAL_RESPONSE']).map((n, i) => (
                            <span key={i} className="px-2 py-0.5 bg-slate-950 border border-slate-800 text-indigo-300 rounded text-[10px]">
                              {n}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <span className="text-slate-400 block mb-1">State & Trace Info:</span>
                        <div className="p-2 bg-slate-950 rounded border border-slate-800 space-y-1 text-slate-300">
                          <div>Correlation ID: <span className="text-indigo-400">{gr.correlation_id || 'corr_01'}</span></div>
                          <div>Trace ID: <span className="text-indigo-400">{gr.trace_id || 'tr_01'}</span></div>
                          <div>Executed Tools: <span className="text-emerald-400">{gr.completed_tool_results?.length || 1}</span></div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No Graph Runs Found" description="Start a LangGraph investigation run to visualize graph state transitions." />
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

        {/* 4.5 GOVERNED TOOL / FUNCTION CALLS INSPECTION PANEL */}
        {activeTab === 'tool_calling' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Zap className="h-5 w-5 text-indigo-400" /> Governed Tool / Function Call Executions
              </h3>
              <Button size="sm" variant="secondary" onClick={loadData}>
                <RefreshCw className="h-3.5 w-3.5 mr-1" /> Refresh Calls
              </Button>
            </div>
            {toolCalls.length > 0 ? (
              <div className="space-y-3">
                {toolCalls.map((tc, idx) => (
                  <div key={tc.call_id || idx} className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-3 font-mono text-xs">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-indigo-400">{tc.tool_name}</span>
                        <span className="text-[10px] text-slate-500">{tc.call_id}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={tc.execution_status === 'SUCCEEDED' ? 'success' : 'critical'}>
                          {tc.execution_status}
                        </Badge>
                        <Badge variant={tc.risk_tier === 'READ_ONLY' ? 'success' : 'warning'}>
                          {tc.risk_tier}
                        </Badge>
                        <span className="text-[10px] text-slate-400">{tc.duration_ms?.toFixed(1)}ms</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No Tool Calls Executed Yet" description="Execute a query in the Investigation Sandbox to observe live tool calls." />
            )}
          </div>
        )}

        {/* 5. MEMORY INSPECTOR */}
        {activeTab === 'memory_inspector' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Brain className="h-5 w-5 text-indigo-400" /> Governed Agent Memory Inspector
              </h3>
              <div className="flex items-center gap-2">
                <Input
                  value={memorySearchQuery}
                  onChange={(e) => setMemorySearchQuery(e.target.value)}
                  placeholder="Search memory records..."
                  className="bg-slate-950 border-slate-800 text-xs w-64"
                />
                <Button size="sm" variant="secondary" onClick={handleMemorySearch}>
                  <Search className="h-3.5 w-3.5 mr-1" /> Search
                </Button>
              </div>
            </div>

            {memories.length > 0 ? (
              <div className="space-y-3 font-mono text-xs">
                {memories.map((m) => (
                  <div key={m.memory_id} className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-indigo-400">{m.memory_key}</span>
                        <span className="text-[10px] text-slate-500">{m.memory_id}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={m.status === 'ACTIVE' ? 'success' : 'critical'}>{m.status}</Badge>
                        <Badge variant="brand" className="text-[10px]">{m.memory_type}</Badge>
                        <Badge variant="neutral" className="text-[10px]">{m.data_classification}</Badge>
                        {m.status === 'ACTIVE' && (
                          <Button size="sm" variant="danger" onClick={() => handleRevokeMemory(m.memory_id)} className="text-[10px] py-0.5 px-2">
                            <Trash2 className="h-3 w-3 mr-1" /> Soft Revoke
                          </Button>
                        )}
                      </div>
                    </div>
                    <div className="text-slate-300 font-sans text-xs bg-slate-950 p-2 rounded border border-slate-800">
                      {m.content}
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <div>Confidence: <span className="text-emerald-400">{(m.confidence * 100).toFixed(0)}%</span> | Namespace: {m.memory_namespace}</div>
                      <div>Source: {m.source_type} | Trace ID: <span className="text-indigo-400">{m.source_trace_id || 'tr_01'}</span></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No Memory Records Found" description="Execute an investigation run to generate governed episodic and semantic memories." />
            )}
          </div>
        )}

        {/* 6. APPROVALS */}
        {activeTab === 'approvals' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Pending Human Approval Gates</h3>
            {approvals.length > 0 ? (
              <div className="space-y-3 font-mono text-xs">
                {approvals.map((app) => (
                  <div key={app.approval_id} className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <span className="font-bold text-amber-400">{app.tool_name}</span>
                      <Badge variant="warning">{app.risk_level}</Badge>
                    </div>
                    <p className="text-xs text-slate-300 font-sans">{app.justification}</p>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="primary" onClick={() => handleApprove(app.approval_id)} className="text-xs gap-1">
                        <CheckCircle2 className="h-3.5 w-3.5" /> Approve
                      </Button>
                      <Button size="sm" variant="danger" onClick={() => handleReject(app.approval_id)} className="text-xs gap-1">
                        <XCircle className="h-3.5 w-3.5" /> Reject
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No Approvals Pending" description="High-risk actions requiring human authorization will appear here." />
            )}
          </div>
        )}

        {/* 7. INVESTIGATION SANDBOX */}
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
              <div className="flex items-center gap-3">
                <Button onClick={handleRunSandbox} disabled={isExecuting} variant="primary" className="text-xs gap-2">
                  <Zap className="h-4 w-4" /> {isExecuting ? 'Executing Multi-Agent DAG Pipeline...' : 'Run Standard Investigation'}
                </Button>
                <Button onClick={handleRunLangGraph} disabled={isExecuting} variant="secondary" className="text-xs gap-2">
                  <GitBranch className="h-4 w-4 text-indigo-400" /> Run LangGraph Orchestrator
                </Button>
              </div>
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

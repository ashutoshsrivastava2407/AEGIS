export interface AgentOverview {
  platform_status: string;
  total_agents: number;
  active_agents: number;
  total_governed_tools: number;
  pending_human_approvals: number;
  supported_agent_types: string[];
}

export interface AgentCatalogItem {
  agent_id: string;
  name: string;
  agent_type: string;
  description: string;
  risk_profile: string;
  lifecycle_state: string;
  current_version: number;
  capabilities: string[];
}

export interface GovernedToolItem {
  tool_name: string;
  category: string;
  description: string;
  risk_tier: string;
  is_governed: boolean;
  rate_limit_per_min: number;
  schema_json: Record<string, any>;
}

export interface PendingApprovalItem {
  approval_id: string;
  run_id: string;
  tool_name: string;
  risk_level: string;
  requested_action: string;
  justification: string;
  approval_status: string;
  created_at: string;
  expires_at?: string;
}

export interface AgentRunResponse {
  run_id: string;
  goal: string;
  status: string;
  plan_id: string;
  total_steps: number;
  executed_nodes: Record<string, any>[];
  verification?: {
    is_verified: boolean;
    groundedness_score: number;
    data_quality_passed: boolean;
    model_drift_passed: boolean;
    summary: string;
    issues: string[];
  };
  pending_approval?: Record<string, any>;
  output_summary: string;
  duration_ms: number;
  evaluation?: {
    goal_completion_score: number;
    tool_accuracy_score: number;
    reasoning_quality_score: number;
    safety_compliance_score: number;
    total_cost_usd: number;
    total_latency_ms: number;
  };
}

const API_BASE = '/api/v1/agents';

export async function fetchAgentsOverview(): Promise<AgentOverview> {
  const res = await fetch(`${API_BASE}/overview`);
  if (!res.ok) throw new Error('Failed to fetch agents overview');
  return res.json();
}

export async function fetchAgentCatalog(): Promise<AgentCatalogItem[]> {
  const res = await fetch(`${API_BASE}/catalog`);
  if (!res.ok) throw new Error('Failed to fetch agent catalog');
  const data = await res.json();
  return data.agents || [];
}

export async function createAgent(payload: { name: string; agent_type: string; role_prompt: string; description?: string; risk_profile?: string }): Promise<AgentCatalogItem> {
  const res = await fetch(`${API_BASE}/catalog`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to create agent');
  return res.json();
}

export async function transitionAgentState(agentId: string, newState: string): Promise<any> {
  const res = await fetch(`${API_BASE}/catalog/${agentId}/transition`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ new_state: newState }),
  });
  if (!res.ok) throw new Error('Failed to transition agent state');
  return res.json();
}

export async function fetchGovernedTools(): Promise<GovernedToolItem[]> {
  const res = await fetch(`${API_BASE}/tools`);
  if (!res.ok) throw new Error('Failed to fetch governed tools');
  const data = await res.json();
  return data.tools || [];
}

export async function executeAgentRun(goal: string, agentType: string = 'SUPERVISOR', context?: Record<string, any>): Promise<AgentRunResponse> {
  const res = await fetch(`${API_BASE}/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal, agent_type: agentType, context }),
  });
  if (!res.ok) throw new Error('Failed to execute agent run');
  return res.json();
}

export async function fetchPendingApprovals(): Promise<PendingApprovalItem[]> {
  const res = await fetch(`${API_BASE}/approvals`);
  if (!res.ok) throw new Error('Failed to fetch pending approvals');
  const data = await res.json();
  return data.approvals || [];
}

export async function approveAction(approvalId: string, operator: string = 'admin', comments: string = 'Approved'): Promise<any> {
  const res = await fetch(`${API_BASE}/approvals/${approvalId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ operator, comments }),
  });
  if (!res.ok) throw new Error('Failed to approve action');
  return res.json();
}

export async function rejectAction(approvalId: string, operator: string = 'admin', comments: string = 'Rejected'): Promise<any> {
  const res = await fetch(`${API_BASE}/approvals/${approvalId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ operator, comments }),
  });
  if (!res.ok) throw new Error('Failed to reject action');
  return res.json();
}

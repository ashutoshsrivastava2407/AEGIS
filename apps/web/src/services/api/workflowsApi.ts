/**
 * AEGIS Workflow Automation Platform API Service
 */

const API_BASE = '/api/v1/workflows';

export interface WorkflowRecord {
  id: string;
  name: string;
  description?: string;
  status: string;
  business_domain: string;
  owner: string;
  version: number;
  trigger_type: string;
  risk_profile: string;
}

export interface WorkflowRunRecord {
  pipeline_run_id: string;
  workflow_run_id: string;
  status: string;
  operating_loop: string;
  total_stages: number;
  completed_stages: number;
  did_estimation_model: string;
  stage_trace: Array<{
    stage_number: number;
    stage_name: string;
    status: string;
    output: any;
  }>;
}

export const workflowsApi = {
  listWorkflows: async (): Promise<{ success: boolean; data: WorkflowRecord[] }> => {
    const res = await fetch(API_BASE);
    if (!res.ok) return { success: false, data: [] };
    const json = await res.json();
    return { success: true, data: json.data || [] };
  },

  createWorkflow: async (payload: any): Promise<{ success: boolean; data: WorkflowRecord }> => {
    const res = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to create workflow');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  triggerClosedLoop: async (payload: any): Promise<{ success: boolean; data: WorkflowRunRecord }> => {
    const res = await fetch(`${API_BASE}/runs/closed-loop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to trigger 16-stage closed loop workflow');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  getObservabilityMetrics: async (): Promise<{ success: boolean; data: any }> => {
    const res = await fetch(`${API_BASE}/observability/metrics`);
    if (!res.ok) return { success: false, data: {} };
    const json = await res.json();
    return { success: true, data: json.data || {} };
  }
};

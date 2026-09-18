/**
 * AEGIS Governance, Security, and Compliance Platform API Service
 */

const API_BASE = '/api/v1/governance';

export interface AuditRecord {
  id: string;
  actor_id: string;
  action: string;
  previous_hash: string;
  current_hash: string;
  details?: any;
}

export interface GovernedPipelineRecord {
  pipeline_id: string;
  tenant_id: string;
  status: string;
  control_chain: string;
  authentication: any;
  auth_strength_required: string;
  authorization: any;
  policy_evaluation: any;
  workflow_closed_loop: any;
  evidence_checksum: string;
  audit_chain_verified: boolean;
  governance_lineage: any;
}

export const governanceApi = {
  getAuditTrail: async (): Promise<{ success: boolean; data: AuditRecord[] }> => {
    const res = await fetch(`${API_BASE}/audit`);
    if (!res.ok) return { success: false, data: [] };
    const json = await res.json();
    return { success: true, data: json.data || [] };
  },

  getTenantPolicies: async (): Promise<{ success: boolean; data: any }> => {
    const res = await fetch(`${API_BASE}/policies`);
    if (!res.ok) return { success: false, data: {} };
    const json = await res.json();
    return { success: true, data: json.data || {} };
  },

  runGovernedPipeline: async (payload: any): Promise<{ success: boolean; data: GovernedPipelineRecord }> => {
    const res = await fetch(`${API_BASE}/pipeline/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to run governed enterprise pipeline');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  simulatePolicy: async (payload: any): Promise<{ success: boolean; data: any }> => {
    const res = await fetch(`${API_BASE}/policies/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to simulate policy impact');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  activateBreakGlass: async (payload: any): Promise<{ success: boolean; data: any }> => {
    const res = await fetch(`${API_BASE}/break-glass`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to activate break glass session');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  getCompliancePosture: async (): Promise<{ success: boolean; data: any }> => {
    const res = await fetch('/api/v1/compliance/posture');
    if (!res.ok) return { success: false, data: {} };
    const json = await res.json();
    return { success: true, data: json.data || {} };
  }
};

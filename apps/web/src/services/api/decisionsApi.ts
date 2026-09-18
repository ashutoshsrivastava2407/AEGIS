/**
 * AEGIS Decision Platform API Service
 */

const API_BASE = '/api/v1/decisions';

export interface DecisionRecord {
  decision_id: string;
  tenant_id: string;
  objective: string;
  status: string;
  stages_completed: number;
  context_fingerprint: string;
  integrity_status: string;
  eligibility_status: string;
  verification_status: string;
  toctou_revalidation?: any;
  action_execution?: any;
  outcome?: any;
  calibration_proposal?: any;
  dossier?: any;
}

export const decisionsApi = {
  listDecisions: async (): Promise<{ success: boolean; data: DecisionRecord[] }> => {
    const res = await fetch(API_BASE);
    if (!res.ok) return { success: false, data: [] };
    const json = await res.json();
    return { success: true, data: json.data || [] };
  },

  createDecision: async (payload: any): Promise<{ success: boolean; data: DecisionRecord }> => {
    const res = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to create decision pipeline');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  getDecision: async (decisionId: string): Promise<{ success: boolean; data: DecisionRecord }> => {
    const res = await fetch(`${API_BASE}/${decisionId}`);
    if (!res.ok) throw new Error('Failed to get decision details');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  runSimulation: async (params: any): Promise<{ success: boolean; data: any }> => {
    const res = await fetch(`${API_BASE}/simulation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to run simulation');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  approveDecision: async (decisionId: string, payload: any): Promise<{ success: boolean; data: any }> => {
    const res = await fetch(`${API_BASE}/${decisionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to approve decision');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  executeAction: async (decisionId: string, payload: any): Promise<{ success: boolean; data: any }> => {
    const res = await fetch(`${API_BASE}/${decisionId}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to execute decision action');
    const json = await res.json();
    return { success: true, data: json.data };
  },

  submitFeedback: async (decisionId: string, payload: any): Promise<{ success: boolean; data: any }> => {
    const res = await fetch(`${API_BASE}/${decisionId}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to submit feedback calibration proposal');
    const json = await res.json();
    return { success: true, data: json.data };
  }
};

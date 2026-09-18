/**
 * AEGIS Machine Learning Platform REST API Client.
 */

export interface MLOverview {
  status: string;
  total_features: number;
  total_feature_sets: number;
  total_experiments: number;
  total_training_jobs: number;
  total_models: number;
  production_models_count: number;
  active_deployments_count: number;
  drift_events_count: number;
  total_predictions: number;
  average_latency_ms: number;
  timestamp: string;
}

export interface FeatureDefinition {
  id: string;
  name: string;
  description?: string;
  data_type: string;
  entity_key: string;
  transformation_definition: string;
  source_dataset_id?: string;
  owner: string;
  status: string;
  version: number;
  created_at?: string;
}

export interface FeatureSet {
  id: string;
  name: string;
  description?: string;
  feature_ids: string[];
  version: number;
  purpose: string;
  owner: string;
  status: string;
  created_at?: string;
}

export interface MLExperiment {
  id: string;
  name: string;
  description?: string;
  objective: string;
  owner: string;
  status: string;
  created_at?: string;
}

export interface MLExperimentRun {
  id: string;
  experiment_id: string;
  algorithm: string;
  hyperparameters: Record<string, any>;
  metrics: Record<string, number>;
  status: string;
  dataset_version: string;
  feature_set_version: number;
  created_at?: string;
}

export interface MLTrainingJob {
  id: string;
  experiment_id: string;
  run_id: string;
  algorithm: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  error_info?: string;
}

export interface MLModel {
  id: string;
  name: string;
  description?: string;
  task_type: string;
  owner: string;
  status: string;
  current_version: number;
  created_at?: string;
}

export interface MLModelVersion {
  id: string;
  model_id: string;
  version: number;
  experiment_run_id: string;
  algorithm: string;
  status: string;
  evaluation_summary: Record<string, any>;
  artifact_reference: Record<string, any>;
  created_at?: string;
}

export interface MLDeployment {
  id: string;
  model_version_id: string;
  environment: string;
  deployment_status: string;
  endpoint_reference: string;
  deployed_at?: string;
}

export interface MLDriftRecord {
  id: string;
  model_id: string;
  feature_name: string;
  method: string;
  score: number;
  threshold: number;
  status: string;
  evidence: Record<string, any>;
  detected_at?: string;
}

export interface MLLineageNode {
  id: string;
  label: string;
  type: string;
  layer: string;
}

export interface MLLineageEdge {
  source: string;
  target: string;
  relation: string;
}

export interface MLLineageDAG {
  root_id: string;
  nodes: MLLineageNode[];
  edges: MLLineageEdge[];
}

const API_BASE = '/api/v1/ml';

export const mlApi = {
  getOverview: async (): Promise<MLOverview> => {
    const res = await fetch(`${API_BASE}/overview`);
    if (!res.ok) throw new Error('Failed to fetch ML overview');
    return res.json();
  },

  getFeatures: async (): Promise<{ features: FeatureDefinition[]; total: number }> => {
    const res = await fetch(`${API_BASE}/features`);
    if (!res.ok) throw new Error('Failed to fetch features');
    return res.json();
  },

  createFeature: async (data: Partial<FeatureDefinition>): Promise<{ id: string; name: string; version: number }> => {
    const res = await fetch(`${API_BASE}/features`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create feature');
    return res.json();
  },

  getFeatureSets: async (): Promise<{ feature_sets: FeatureSet[]; total: number }> => {
    const res = await fetch(`${API_BASE}/feature-sets`);
    if (!res.ok) throw new Error('Failed to fetch feature sets');
    return res.json();
  },

  createFeatureSet: async (data: Partial<FeatureSet>): Promise<{ id: string; name: string; version: number }> => {
    const res = await fetch(`${API_BASE}/feature-sets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create feature set');
    return res.json();
  },

  getExperiments: async (): Promise<{ experiments: MLExperiment[]; total: number }> => {
    const res = await fetch(`${API_BASE}/experiments`);
    if (!res.ok) throw new Error('Failed to fetch experiments');
    return res.json();
  },

  createExperiment: async (data: Partial<MLExperiment>): Promise<{ id: string; name: string }> => {
    const res = await fetch(`${API_BASE}/experiments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create experiment');
    return res.json();
  },

  getExperimentRuns: async (expId: string): Promise<{ runs: MLExperimentRun[]; total: number }> => {
    const res = await fetch(`${API_BASE}/experiments/${expId}/runs`);
    if (!res.ok) throw new Error('Failed to fetch experiment runs');
    return res.json();
  },

  getTrainingJobs: async (): Promise<{ training_jobs: MLTrainingJob[]; total: number }> => {
    const res = await fetch(`${API_BASE}/training-jobs`);
    if (!res.ok) throw new Error('Failed to fetch training jobs');
    return res.json();
  },

  getModels: async (): Promise<{ models: MLModel[]; total: number }> => {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error('Failed to fetch models');
    return res.json();
  },

  createModel: async (data: Partial<MLModel>): Promise<{ id: string; name: string; task_type: string }> => {
    const res = await fetch(`${API_BASE}/models`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create model');
    return res.json();
  },

  getModelVersions: async (modelId: string): Promise<{ versions: MLModelVersion[]; total: number }> => {
    const res = await fetch(`${API_BASE}/models/${modelId}/versions`);
    if (!res.ok) throw new Error('Failed to fetch model versions');
    return res.json();
  },

  promoteModelVersion: async (versionId: string, targetStatus: string): Promise<{ id: string; status: string }> => {
    const res = await fetch(`${API_BASE}/models/dummy/versions/${versionId}/promote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_status: targetStatus }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to promote model version');
    }
    return res.json();
  },

  evaluateModelVersion: async (modelId: string, version: number): Promise<{ evaluation_id: string; metrics: Record<string, number> }> => {
    const res = await fetch(`${API_BASE}/models/${modelId}/versions/${version}/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error('Failed to evaluate model version');
    return res.json();
  },

  getDeployments: async (): Promise<{ deployments: MLDeployment[]; total: number }> => {
    const res = await fetch(`${API_BASE}/deployments`);
    if (!res.ok) throw new Error('Failed to fetch deployments');
    return res.json();
  },

  createDeployment: async (modelVersionId: string, environment: string): Promise<{ id: string; endpoint_reference: string }> => {
    const res = await fetch(`${API_BASE}/deployments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_version_id: modelVersionId, environment }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to deploy model version');
    }
    return res.json();
  },

  predictOnline: async (modelId: string, version: number, features: Record<string, any>): Promise<any> => {
    const res = await fetch(`${API_BASE}/models/${modelId}/versions/${version}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Online prediction failed');
    }
    return res.json();
  },

  getMonitoring: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/monitoring`);
    if (!res.ok) throw new Error('Failed to fetch monitoring');
    return res.json();
  },

  getDriftRecords: async (): Promise<{ drift_records: MLDriftRecord[]; total: number }> => {
    const res = await fetch(`${API_BASE}/drift`);
    if (!res.ok) throw new Error('Failed to fetch drift records');
    return res.json();
  },

  evaluateDrift: async (modelId: string, featureName: string): Promise<{ id: string; status: string; score: number }> => {
    const res = await fetch(`${API_BASE}/drift/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, feature_name: featureName }),
    });
    if (!res.ok) throw new Error('Failed to evaluate drift');
    return res.json();
  },

  getLineage: async (versionId: string): Promise<MLLineageDAG> => {
    const res = await fetch(`${API_BASE}/lineage/${versionId}`);
    if (!res.ok) throw new Error('Failed to fetch lineage');
    return res.json();
  },

  triggerRetraining: async (modelId: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/retraining`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId }),
    });
    if (!res.ok) throw new Error('Failed to trigger retraining');
    return res.json();
  },
};

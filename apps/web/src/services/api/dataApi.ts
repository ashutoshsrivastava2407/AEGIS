import { APIResponse } from '@/types';

export interface DataSource {
  id: string;
  tenant_id: string;
  name: string;
  source_type: 'CSV' | 'JSON' | 'POSTGRESQL' | 'REST_API';
  config_metadata: Record<string, any>;
  status: string;
  created_by: string;
  created_at: string;
  last_tested_at?: string;
  last_successful_ingestion_at?: string;
  last_error?: string;
}

export interface IngestionJob {
  run_id: string;
  tenant_id: string;
  source_id: string;
  dataset_id: string;
  status: 'PENDING' | 'RUNNING' | 'SUCCEEDED' | 'PARTIAL_SUCCESS' | 'FAILED' | 'CANCELLED';
  records_read: number;
  records_written: number;
  records_rejected: number;
  bytes_processed: number;
  checksum: string;
  duration_ms: number;
  bronze_key?: string;
  silver_key?: string;
  gold_key?: string;
  gold_status?: string;
  health_score?: {
    overall_score: number;
    dimension_scores: Record<string, number>;
    status: string;
  };
  quality_results?: Array<{
    check_type: string;
    check_status: string;
    evaluated_records: number;
    failed_records: number;
    failure_rate: number;
    execution_time_ms: number;
  }>;
}

export interface CatalogDataset {
  id: string;
  tenant_id: string;
  name: string;
  layer: 'BRONZE' | 'SILVER' | 'GOLD';
  source_id?: string;
  record_count: number;
  quality_score: number;
  freshness: string;
  storage_path?: string;
  updated_at: string;
}

export interface LineageGraph {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    layer?: string;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    relationship: string;
  }>;
}

export const dataApi = {
  async listSources(): Promise<DataSource[]> {
    const res = await fetch('/api/v1/data/sources');
    if (!res.ok) throw new Error('Failed to fetch data sources');
    const json: APIResponse<DataSource[]> = await res.json();
    return json.data || [];
  },

  async createSource(name: string, sourceType: string, config: Record<string, any>): Promise<DataSource> {
    const res = await fetch('/api/v1/data/sources', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, source_type: sourceType, config }),
    });
    if (!res.ok) throw new Error('Failed to register data source');
    const json: APIResponse<DataSource> = await res.json();
    return json.data!;
  },

  async testSource(sourceId: string): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`/api/v1/data/sources/${sourceId}/test`, { method: 'POST' });
    if (!res.ok) throw new Error('Source connectivity test failed');
    const json = await res.json();
    return json.data;
  },

  async triggerIngestion(sourceId: string, goldTransform?: Record<string, any>): Promise<IngestionJob> {
    const res = await fetch('/api/v1/data/ingestions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_id: sourceId, gold_transform: goldTransform }),
    });
    if (!res.ok) throw new Error('Failed to trigger ingestion pipeline');
    const json: APIResponse<IngestionJob> = await res.json();
    return json.data!;
  },

  async listJobs(): Promise<IngestionJob[]> {
    const res = await fetch('/api/v1/data/ingestions');
    if (!res.ok) throw new Error('Failed to fetch ingestion runs');
    const json: APIResponse<IngestionJob[]> = await res.json();
    return json.data || [];
  },

  async listDatasets(layer?: string): Promise<CatalogDataset[]> {
    const url = layer ? `/api/v1/data/datasets?layer=${layer}` : '/api/v1/data/datasets';
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch catalog datasets');
    const json: APIResponse<CatalogDataset[]> = await res.json();
    return json.data || [];
  },

  async getLineage(resourceId: string): Promise<LineageGraph> {
    const res = await fetch(`/api/v1/data/datasets/${resourceId}/lineage`);
    if (!res.ok) throw new Error('Failed to fetch dataset lineage DAG');
    const json: APIResponse<LineageGraph> = await res.json();
    return json.data || { nodes: [], edges: [] };
  },

  async listQuarantine(): Promise<any[]> {
    const res = await fetch('/api/v1/data/quarantine');
    if (!res.ok) throw new Error('Failed to fetch quarantined records');
    const json = await res.json();
    return json.data || [];
  },
};

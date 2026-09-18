export interface AnalyticsOverview {
  status: string;
  total_analytical_datasets: number;
  total_metrics: number;
  active_anomalies: number;
  open_insights: number;
  active_alerts: number;
  total_queries_executed: number;
  timestamp: string;
}

export interface AnalyticalDataset {
  id: string;
  name: string;
  description?: string;
  source_dataset_id?: string;
  source_layer: string;
  version: string;
  schema_json: Record<string, any>;
  owner: string;
  status: string;
  created_at?: string;
}

export interface MetricDefinition {
  id: string;
  name: string;
  description?: string;
  owner: string;
  unit: string;
  aggregation_type: string;
  dimensions: string[];
  time_grain: string;
  calculation_formula: string;
  version: number;
  status: string;
  created_at?: string;
}

export interface QueryExecutionResult {
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  duration_ms: number;
  referenced_tables: string[];
  secured_sql: string;
}

export interface QueryExecutionRecord {
  id: string;
  user_id: string;
  sql_text: string;
  duration_ms: number;
  status: string;
  row_count: number;
  error_message?: string;
  created_at?: string;
}

export interface SavedQuery {
  id: string;
  name: string;
  description?: string;
  sql_text: string;
  owner: string;
  tags: string[];
  created_at?: string;
}

export interface Dashboard {
  id: string;
  title: string;
  description?: string;
  owner: string;
  widgets_count: number;
  created_at?: string;
}

export interface AnomalyRecord {
  id: string;
  metric_id: string;
  observed_value: number;
  expected_value: number;
  expected_min: number;
  expected_max: number;
  z_score: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  detection_method: string;
  status: string;
  evidence_json: Record<string, any>;
  detected_at?: string;
}

export interface InsightRecord {
  id: string;
  insight_type: string;
  title: string;
  description: string;
  metric_id?: string;
  severity: string;
  evidence_json: Record<string, any>;
  status: string;
  created_at?: string;
}

export interface AlertRule {
  id: string;
  metric_id: string;
  name: string;
  description?: string;
  condition_type: string;
  threshold_value: number;
  severity: string;
  status: string;
  created_at?: string;
}

export interface AlertEvent {
  id: string;
  rule_id: string;
  metric_id: string;
  triggered_value: number;
  threshold_value: number;
  severity: string;
  status: string;
  triggered_at?: string;
}

const API_BASE = '/api/v1/analytics';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error (${response.status}): ${errorText}`);
  }

  return response.json();
}

export const analyticsApi = {
  getOverview: (): Promise<AnalyticsOverview> => fetchJson<AnalyticsOverview>(`${API_BASE}/overview`),

  getDatasets: (): Promise<{ datasets: AnalyticalDataset[]; total: number }> =>
    fetchJson(`${API_BASE}/datasets`),

  createDataset: (data: any): Promise<AnalyticalDataset> =>
    fetchJson(`${API_BASE}/datasets`, { method: 'POST', body: JSON.stringify(data) }),

  getMetrics: (): Promise<{ metrics: MetricDefinition[]; total: number }> =>
    fetchJson(`${API_BASE}/metrics`),

  createMetric: (data: any): Promise<MetricDefinition> =>
    fetchJson(`${API_BASE}/metrics`, { method: 'POST', body: JSON.stringify(data) }),

  evaluateMetric: (metricId: string, history?: number[]): Promise<any> =>
    fetchJson(`${API_BASE}/metrics/${encodeURIComponent(metricId)}/evaluate`, {
      method: 'POST',
      body: JSON.stringify({ history }),
    }),

  executeQuery: (sqlText: string, parameters?: any): Promise<QueryExecutionResult> =>
    fetchJson(`${API_BASE}/query`, {
      method: 'POST',
      body: JSON.stringify({ sql_text: sqlText, parameters }),
    }),

  getQueryHistory: (): Promise<{ query_history: QueryExecutionRecord[]; total: number }> =>
    fetchJson(`${API_BASE}/queries`),

  getSavedQueries: (): Promise<{ saved_queries: SavedQuery[]; total: number }> =>
    fetchJson(`${API_BASE}/saved-queries`),

  createSavedQuery: (data: any): Promise<SavedQuery> =>
    fetchJson(`${API_BASE}/saved-queries`, { method: 'POST', body: JSON.stringify(data) }),

  getDashboards: (): Promise<{ dashboards: Dashboard[]; total: number }> =>
    fetchJson(`${API_BASE}/dashboards`),

  createDashboard: (data: any): Promise<Dashboard> =>
    fetchJson(`${API_BASE}/dashboards`, { method: 'POST', body: JSON.stringify(data) }),

  getAnomalies: (): Promise<{ anomalies: AnomalyRecord[]; total: number }> =>
    fetchJson(`${API_BASE}/anomalies`),

  getInsights: (): Promise<{ insights: InsightRecord[]; total: number }> =>
    fetchJson(`${API_BASE}/insights`),

  getAlertRules: (): Promise<{ alert_rules: AlertRule[]; total: number }> =>
    fetchJson(`${API_BASE}/alerts/rules`),

  createAlertRule: (data: any): Promise<AlertRule> =>
    fetchJson(`${API_BASE}/alerts/rules`, { method: 'POST', body: JSON.stringify(data) }),

  getAlertEvents: (): Promise<{ alert_events: AlertEvent[]; total: number }> =>
    fetchJson(`${API_BASE}/alerts/events`),
};

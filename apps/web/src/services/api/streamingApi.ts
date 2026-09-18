export interface StreamOverview {
  status: string;
  broker: {
    broker_type: string;
    status: string;
    bootstrap_servers?: string;
    topic_count: number;
  };
  active_sources: number;
  active_topics: number;
  active_consumer_groups: number;
  total_consumer_lag: number;
  pending_dlq_records: number;
  streaming_quality_score: number;
  timestamp: string;
}

export interface StreamSource {
  id: string;
  name: string;
  description?: string;
  source_type: string;
  connection_config: Record<string, any>;
  format: string;
  status: string;
  created_at?: string;
}

export interface StreamTopic {
  id: string;
  name: string;
  partitions: number;
  retention_ms: number;
  retention_bytes: number;
  cleanup_policy: string;
  schema_id?: string;
  description?: string;
  status: string;
  total_messages: number;
  partition_offsets: Record<number, number>;
  created_at?: string;
}

export interface PartitionOffsetInfo {
  partition_id: number;
  current_offset: number;
  log_end_offset: number;
  lag: number;
}

export interface ConsumerGroup {
  id: string;
  group_id: string;
  topic_name: string;
  state: string;
  members_count: number;
  total_lag: number;
  partitions: PartitionOffsetInfo[];
  updated_at?: string;
}

export interface LiveEvent {
  topic: string;
  partition: number;
  offset: number;
  timestamp: string;
  envelope: {
    event_id: string;
    event_type: string;
    event_version: string;
    tenant_id: string;
    source: string;
    entity_type: string;
    entity_id: string;
    occurred_at: string;
    produced_at: string;
    correlation_id?: string;
    schema_version: string;
    payload: Record<string, any>;
    metadata: Record<string, any>;
  };
  key: string;
}

export interface DLQRecord {
  id: string;
  event_id?: string;
  topic_name: string;
  partition_id: number;
  offset: number;
  error_category: string;
  error_message: string;
  stack_trace?: string;
  raw_payload: Record<string, any>;
  retry_count: number;
  status: 'PENDING' | 'REPLAYED' | 'DISCARDED';
  replayed_at?: string;
  created_at?: string;
}

export interface StreamQualityMetric {
  id: string;
  topic_name: string;
  window_start: string;
  window_end: string;
  total_events: number;
  valid_events: number;
  invalid_schema_events: number;
  duplicate_events: number;
  late_events: number;
  avg_latency_ms: number;
  quality_score: number;
  created_at?: string;
}

const API_BASE = '/api/v1/streaming';

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

export const streamingApi = {
  getOverview: (): Promise<StreamOverview> => fetchJson<StreamOverview>(`${API_BASE}/overview`),
  
  getSources: (): Promise<{ sources: StreamSource[]; total: number }> =>
    fetchJson(`${API_BASE}/sources`),
    
  createSource: (data: any): Promise<StreamSource> =>
    fetchJson(`${API_BASE}/sources`, { method: 'POST', body: JSON.stringify(data) }),

  getTopics: (): Promise<{ topics: StreamTopic[]; total: number }> =>
    fetchJson(`${API_BASE}/topics`),

  createTopic: (data: any): Promise<StreamTopic> =>
    fetchJson(`${API_BASE}/topics`, { method: 'POST', body: JSON.stringify(data) }),

  produceEvent: (topicName: string, payload: any): Promise<any> =>
    fetchJson(`${API_BASE}/topics/${encodeURIComponent(topicName)}/produce`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getConsumerGroups: (): Promise<{ consumer_groups: ConsumerGroup[]; total: number }> =>
    fetchJson(`${API_BASE}/consumers`),

  getLiveEvents: (topicName: string, partition: number = 0, limit: number = 50): Promise<{ events: LiveEvent[]; total: number }> =>
    fetchJson(`${API_BASE}/events?topic_name=${encodeURIComponent(topicName)}&partition=${partition}&limit=${limit}`),

  getDLQRecords: (status?: string, category?: string): Promise<{ dlq_records: DLQRecord[]; total: number }> => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (category) params.append('category', category);
    return fetchJson(`${API_BASE}/dlq?${params.toString()}`);
  },

  replayDLQRecord: (dlqId: string): Promise<any> =>
    fetchJson(`${API_BASE}/dlq/${encodeURIComponent(dlqId)}/replay`, { method: 'POST' }),

  getQualityMetrics: (topicName?: string): Promise<{ quality_metrics: StreamQualityMetric[]; total: number }> => {
    const query = topicName ? `?topic_name=${encodeURIComponent(topicName)}` : '';
    return fetchJson(`${API_BASE}/quality${query}`);
  },
};

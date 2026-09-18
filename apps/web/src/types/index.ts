export type DomainId =
  | 'command'
  | 'intelligence'
  | 'data'
  | 'streaming'
  | 'analytics'
  | 'ml'
  | 'knowledge'
  | 'ai'
  | 'agents'
  | 'decisions'
  | 'simulations'
  | 'operations'
  | 'workflows'
  | 'observability'
  | 'governance'
  | 'system';

export interface DomainMeta {
  id: DomainId;
  label: string;
  category: 'CORE' | 'PLATFORM' | 'GOVERNANCE';
  icon: string;
  description: string;
}

export interface APIResponse<T> {
  success: boolean;
  status_code: number;
  message: string;
  data: T | null;
  correlation_id: string;
  timestamp: string;
}

export interface SystemStatus {
  status: string;
  service: string;
  environment: string;
  components?: Record<string, { status: string; detail?: string }>;
}

export interface EvidenceItem {
  id: string;
  title: string;
  type: 'METRIC' | 'DATASET' | 'MODEL' | 'DOCUMENT' | 'DECISION' | 'LOG';
  source: string;
  confidence?: number;
  timestamp: string;
  summary: string;
}

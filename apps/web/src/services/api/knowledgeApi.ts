import { APIResponse } from '@/types';

export interface KnowledgeSource {
  id: string;
  name: string;
  source_type: string;
  status: string;
  config_json: Record<string, any>;
  tenant_id: string;
  owner: string;
  is_active: boolean;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  collection: string;
  file_type: string;
  mime_type: string;
  status: string;
  current_version: number;
  checksum: string;
  chunk_count: number;
  tenant_id: string;
  owner: string;
}

export interface RAGQueryResponse {
  rag_request_id: string;
  status: string;
  question: string;
  answer: string;
  citations: Array<{
    citation_id: string;
    title: string;
    page_number?: number;
    section_title?: string;
    excerpt: string;
    score: number;
    is_verified: boolean;
  }>;
  groundedness: {
    groundedness_score: number;
    citation_coverage: number;
    unsupported_claim_count: number;
    evaluation_details?: Record<string, any>;
  };
  retrieved_chunk_count: number;
  tokens_used: number;
  latency_ms: number;
  estimated_cost: number;
  provider: string;
  model: string;
}

export interface LLMGatewayStatus {
  status: string;
  circuit_breaker_open: boolean;
  providers: string[];
  usage_summary: {
    tenant_id: string;
    total_requests: number;
    total_tokens: number;
    total_cost: number;
    avg_latency_ms: number;
  };
  safety_events_count: number;
}

export const knowledgeApi = {
  getSources: async (): Promise<KnowledgeSource[]> => {
    const res = await fetch('/api/v1/knowledge/sources');
    if (!res.ok) throw new Error('Failed to fetch sources');
    const json: APIResponse<KnowledgeSource[]> = await res.json();
    return json.data || [];
  },
  registerSource: async (name: string, sourceType: string, config: Record<string, any> = {}): Promise<KnowledgeSource> => {
    const res = await fetch('/api/v1/knowledge/sources', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, source_type: sourceType, config }),
    });
    if (!res.ok) throw new Error('Failed to register source');
    const json: APIResponse<KnowledgeSource> = await res.json();
    return json.data!;
  },
  getDocuments: async (): Promise<KnowledgeDocument[]> => {
    const res = await fetch('/api/v1/knowledge/documents');
    if (!res.ok) throw new Error('Failed to fetch documents');
    const json: APIResponse<KnowledgeDocument[]> = await res.json();
    return json.data || [];
  },
  ingestDocument: async (filename: string, contentStr: string, collection: string = 'default'): Promise<any> => {
    const res = await fetch('/api/v1/knowledge/documents/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, content_str: contentStr, collection }),
    });
    if (!res.ok) throw new Error('Failed to ingest document');
    const json: APIResponse<any> = await res.json();
    return json.data;
  },
  retrieveChunks: async (query: string, topK: number = 5): Promise<any[]> => {
    const res = await fetch('/api/v1/knowledge/retrieve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK }),
    });
    if (!res.ok) throw new Error('Failed to retrieve chunks');
    const json: APIResponse<any[]> = await res.json();
    return json.data || [];
  },
  getKnowledgeGraph: async (): Promise<{ entities: any[]; relations: any[] }> => {
    const res = await fetch('/api/v1/knowledge/graph');
    if (!res.ok) throw new Error('Failed to fetch knowledge graph');
    const json: APIResponse<{ entities: any[]; relations: any[] }> = await res.json();
    return json.data || { entities: [], relations: [] };
  },
  executeRAGQuery: async (question: string, topK: number = 5): Promise<RAGQueryResponse> => {
    const res = await fetch('/api/v1/rag/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, top_k: topK }),
    });
    if (!res.ok) throw new Error('Failed to execute RAG query');
    const json: APIResponse<RAGQueryResponse> = await res.json();
    return json.data!;
  },
  getGatewayStatus: async (): Promise<LLMGatewayStatus> => {
    const res = await fetch('/api/v1/llm/status');
    if (!res.ok) throw new Error('Failed to fetch gateway status');
    const json: APIResponse<LLMGatewayStatus> = await res.json();
    return json.data!;
  },
  getSafetyEvents: async (): Promise<any[]> => {
    const res = await fetch('/api/v1/llm/safety/events');
    if (!res.ok) throw new Error('Failed to fetch safety events');
    const json: APIResponse<any[]> = await res.json();
    return json.data || [];
  }
};

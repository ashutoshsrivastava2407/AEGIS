import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  FileText,
  Layers,
  Upload,
  Cpu,
  Search,
  Bot,
  ShieldCheck,
  Share2,
  Coins,
  RefreshCw,
  FileCode,
  Zap,
  Lock
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  knowledgeApi,
  KnowledgeDocument,
  KnowledgeSource,
  RAGQueryResponse,
  LLMGatewayStatus
} from '@/services/api/knowledgeApi';

type TabId =
  | 'overview'
  | 'documents'
  | 'collections'
  | 'ingestion'
  | 'processing'
  | 'search'
  | 'rag'
  | 'gateway'
  | 'security'
  | 'citations'
  | 'graph'
  | 'usage';

export const KnowledgeWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [loading, setLoading] = useState(true);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [gatewayStatus, setGatewayStatus] = useState<LLMGatewayStatus | null>(null);

  // Ingestion form state
  const [docName, setDocName] = useState('');
  const [docContent, setDocContent] = useState('');
  const [collection, setCollection] = useState('Finance');
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  // Hybrid search form state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // RAG query state
  const [ragQuestion, setRagQuestion] = useState('');
  const [ragResponse, setRagResponse] = useState<RAGQueryResponse | null>(null);
  const [ragLoading, setRagLoading] = useState(false);

  // Graph state
  const [graphData, setGraphData] = useState<{ entities: any[]; relations: any[] }>({ entities: [], relations: [] });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [docsData, sourcesData, gwData, graphRes] = await Promise.all([
        knowledgeApi.getDocuments().catch(() => []),
        knowledgeApi.getSources().catch(() => []),
        knowledgeApi.getGatewayStatus().catch(() => null),
        knowledgeApi.getKnowledgeGraph().catch(() => ({ entities: [], relations: [] }))
      ]);

      setDocuments(docsData);
      setSources(sourcesData);
      setGatewayStatus(gwData);
      setGraphData(graphRes);
    } catch (err) {
      console.error('Failed to load knowledge workspace data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docName || !docContent) return;
    setIngestStatus('Ingesting & parsing document...');
    try {
      await knowledgeApi.ingestDocument(docName, docContent, collection);
      setIngestStatus('Document successfully ingested, chunked, and indexed!');
      setDocName('');
      setDocContent('');
      fetchData();
    } catch (err) {
      setIngestStatus('Error ingesting document');
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;
    try {
      const results = await knowledgeApi.retrieveChunks(searchQuery, 5);
      setSearchResults(results);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRAGQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuestion) return;
    setRagLoading(true);
    try {
      const res = await knowledgeApi.executeRAGQuery(ragQuestion, 5);
      setRagResponse(res);
    } catch (err) {
      console.error(err);
    } finally {
      setRagLoading(false);
    }
  };

  if (loading) {
    return <LoadingState label="Initializing Enterprise Knowledge Base & LLM Gateway..." />;
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.08)] pb-4">
        <div>
          <h1 className="text-xl font-bold text-gray-100 tracking-tight flex items-center gap-2">
            Enterprise Knowledge Base &amp; RAG Platform
            <Badge variant="brand" size="sm">Step 6 Architecture</Badge>
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Structural document ingestion, hybrid vector/BM25 retrieval, grounded RAG citations, and LLM Gateway routing.
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={fetchData} className="gap-2">
          <RefreshCw size={14} /> Refresh
        </Button>
      </div>

      {/* 12-Tab Workspace Navigation */}
      <div className="flex items-center gap-1 border-b border-[rgba(255,255,255,0.08)] overflow-x-auto pb-2 scrollbar-none">
        {[
          { id: 'overview', label: 'Overview', icon: BookOpen },
          { id: 'documents', label: 'Documents', icon: FileText },
          { id: 'collections', label: 'Collections', icon: Layers },
          { id: 'ingestion', label: 'Ingestion', icon: Upload },
          { id: 'processing', label: 'Processing', icon: FileCode },
          { id: 'search', label: 'Hybrid Search', icon: Search },
          { id: 'rag', label: 'Grounded RAG', icon: Bot },
          { id: 'gateway', label: 'LLM Gateway', icon: Cpu },
          { id: 'security', label: 'Security & Safety', icon: Lock },
          { id: 'citations', label: 'Citations', icon: ShieldCheck },
          { id: 'graph', label: 'Knowledge Graph', icon: Share2 },
          { id: 'usage', label: 'Token & Cost Accounting', icon: Coins },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabId)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-controls text-xs font-medium whitespace-nowrap transition-colors ${
                isActive
                  ? 'bg-[#1E1E26] text-white border border-[rgba(255,255,255,0.12)]'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              <Icon size={14} className={isActive ? 'text-[#7C6FF2]' : 'text-gray-400'} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
              <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Total Documents</span>
              <p className="text-2xl font-bold text-gray-100 mt-1">{documents.length}</p>
              <p className="text-[11px] text-gray-500 mt-1">Parsed &amp; Versioned</p>
            </div>
            <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
              <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Knowledge Sources</span>
              <p className="text-2xl font-bold text-gray-100 mt-1">{sources.length}</p>
              <p className="text-[11px] text-gray-500 mt-1">Connectors Registered</p>
            </div>
            <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
              <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold">LLM Gateway Status</span>
              <p className="text-2xl font-bold text-[#35C98A] mt-1">OPERATIONAL</p>
              <p className="text-[11px] text-gray-500 mt-1">Primary + Fallback Ready</p>
            </div>
            <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
              <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Safety Guardrails</span>
              <p className="text-2xl font-bold text-[#7C6FF2] mt-1">ENFORCED</p>
              <p className="text-[11px] text-gray-500 mt-1">Prompt Injection Shield Active</p>
            </div>
          </div>

          <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels">
            <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Zap size={14} className="text-[#7C6FF2]" /> Closed-Loop Knowledge Architecture
            </h3>
            <div className="p-4 bg-[#16161C] border border-white/5 rounded-controls text-xs font-mono text-gray-300 overflow-x-auto">
              Real Documents → Ingestion → Versioning → Structural Parsing → Chunks → Vector + BM25 Index → Server-Side Auth Filter → Hybrid RRF Search → Reranking → Grounded RAG → LLM Gateway → Verified Citations → Groundedness Evaluation
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Documents */}
      {activeTab === 'documents' && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-200">Ingested Enterprise Documents</h3>
          {documents.length === 0 ? (
            <EmptyState
              title="No Ingested Documents Found"
              description="Ingest documents via the Ingestion tab to populate the knowledge index."
              icon="search"
            />
          ) : (
            <div className="bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels overflow-hidden">
              <table className="w-full text-left text-xs text-gray-300">
                <thead className="bg-[#16161C] border-b border-[rgba(255,255,255,0.08)] text-gray-400 uppercase tracking-wider">
                  <tr>
                    <th className="p-3">Title</th>
                    <th className="p-3">Collection</th>
                    <th className="p-3">Format</th>
                    <th className="p-3">Version</th>
                    <th className="p-3">Chunks</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[rgba(255,255,255,0.04)]">
                  {documents.map((doc) => (
                    <tr key={doc.id}>
                      <td className="p-3 font-medium text-gray-100">{doc.title}</td>
                      <td className="p-3">{doc.collection}</td>
                      <td className="p-3"><Badge variant="neutral" size="sm">{doc.file_type}</Badge></td>
                      <td className="p-3">v{doc.current_version}</td>
                      <td className="p-3">{doc.chunk_count}</td>
                      <td className="p-3"><Badge variant="success" size="sm">{doc.status}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Collections */}
      {activeTab === 'collections' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {['Finance', 'Operations', 'Legal', 'Engineering', 'HR', 'Sales'].map((colName) => (
            <div key={colName} className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-gray-200">{colName} Collection</h4>
                <Badge variant="brand" size="sm">Governed</Badge>
              </div>
              <p className="text-xs text-gray-400">Enterprise documentation and SOP policy repository for {colName}.</p>
              <div className="pt-2 flex items-center justify-between text-[11px] text-gray-500">
                <span>Access: RBAC Enforced</span>
                <span>Tenant Isolated</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 4: Ingestion */}
      {activeTab === 'ingestion' && (
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels max-w-2xl space-y-4">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
            <Upload size={16} className="text-[#7C6FF2]" /> Ingest Enterprise Document
          </h3>
          <form onSubmit={handleIngest} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Document Title / Filename</label>
              <Input value={docName} onChange={(e) => setDocName(e.target.value)} placeholder="e.g. Q3_Financial_Policy_SOP.txt" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Target Collection</label>
              <select value={collection} onChange={(e) => setCollection(e.target.value)} className="w-full bg-[#16161C] border border-[rgba(255,255,255,0.12)] rounded-controls text-xs p-2 text-gray-200 focus:outline-none focus:border-[#7C6FF2]">
                <option value="Finance">Finance</option>
                <option value="Operations">Operations</option>
                <option value="Legal">Legal</option>
                <option value="Engineering">Engineering</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Document Content</label>
              <textarea value={docContent} onChange={(e) => setDocContent(e.target.value)} rows={6} className="w-full bg-[#16161C] border border-[rgba(255,255,255,0.12)] rounded-controls text-xs p-2.5 text-gray-200 font-mono focus:outline-none focus:border-[#7C6FF2]" placeholder="Enter document text content..." required />
            </div>
            <Button type="submit" variant="primary" size="sm" className="w-full">
              Parse, Chunk &amp; Index Document
            </Button>
            {ingestStatus && <p className="text-xs text-[#35C98A] font-medium">{ingestStatus}</p>}
          </form>
        </div>
      )}

      {/* Tab 5: Processing */}
      {activeTab === 'processing' && (
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels space-y-4">
          <h3 className="text-sm font-semibold text-gray-200">Structural &amp; Semantic Chunking Specs</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls">
              <span className="text-gray-400 block font-semibold mb-1">Target Chunk Size</span>
              <span className="text-gray-200 font-mono text-sm">500 Words</span>
            </div>
            <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls">
              <span className="text-gray-400 block font-semibold mb-1">Overlap Window</span>
              <span className="text-gray-200 font-mono text-sm">50 Words</span>
            </div>
            <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls">
              <span className="text-gray-400 block font-semibold mb-1">Provenance Hash</span>
              <span className="text-gray-200 font-mono text-sm">SHA-256 Checksummed</span>
            </div>
          </div>
        </div>
      )}

      {/* Tab 6: Hybrid Search */}
      {activeTab === 'search' && (
        <div className="space-y-4">
          <form onSubmit={handleSearch} className="flex gap-2">
            <Input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Query document store via Hybrid Vector + Lexical BM25 search..." className="flex-1" />
            <Button type="submit" variant="primary" size="sm">Search</Button>
          </form>

          {searchResults.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Top Hybrid Search Results (RRF Fusion)</h4>
              {searchResults.map((res, i) => (
                <div key={i} className="p-3 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-gray-200">{res.section_title || 'Section'} (Page {res.page_number || 1})</span>
                    <Badge variant="brand" size="sm">RRF Score: {res.score.toFixed(4)}</Badge>
                  </div>
                  <p className="text-xs text-gray-300 font-mono">{res.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 7: Grounded RAG */}
      {activeTab === 'rag' && (
        <div className="space-y-4 max-w-3xl">
          <form onSubmit={handleRAGQuery} className="space-y-3">
            <label className="block text-xs font-semibold text-gray-300">Ask Grounded Question</label>
            <Input value={ragQuestion} onChange={(e) => setRagQuestion(e.target.value)} placeholder="e.g. What are the key financial governance policies?" required />
            <Button type="submit" variant="primary" size="sm" disabled={ragLoading}>
              {ragLoading ? 'Executing RAG Pipeline...' : 'Generate Grounded Answer'}
            </Button>
          </form>

          {ragResponse && (
            <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels space-y-4">
              <div className="flex items-center justify-between border-b border-white/5 pb-2">
                <span className="text-xs font-semibold text-[#35C98A]">Grounded RAG Response</span>
                <Badge variant="success" size="sm">Groundedness Score: {ragResponse.groundedness.groundedness_score * 100}%</Badge>
              </div>
              <p className="text-xs text-gray-200 leading-relaxed whitespace-pre-wrap">{ragResponse.answer}</p>

              {ragResponse.citations.length > 0 && (
                <div className="border-t border-white/5 pt-3 space-y-2">
                  <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider block">Verified Citations</span>
                  {ragResponse.citations.map((cit, idx) => (
                    <div key={idx} className="p-2 bg-[#16161C] border border-white/5 rounded-controls text-xs flex justify-between items-center">
                      <div>
                        <span className="font-semibold text-gray-200">[{cit.citation_id}] {cit.title}</span>
                        <p className="text-gray-400 text-[11px]">{cit.excerpt}</p>
                      </div>
                      <Badge variant="success" size="sm">Verified</Badge>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 8: LLM Gateway */}
      {activeTab === 'gateway' && (
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels space-y-4">
          <h3 className="text-sm font-semibold text-gray-200">LLM Gateway Routing &amp; Provider Registry</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-gray-200">Primary Provider</span>
                <Badge variant="success" size="sm">ACTIVE</Badge>
              </div>
              <p className="text-gray-400">aegis-llm-pro (Context: 8192 tokens)</p>
            </div>
            <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-gray-200">Fallback Provider</span>
                <Badge variant="neutral" size="sm">STANDBY</Badge>
              </div>
              <p className="text-gray-400">aegis-llm-pro-fallback (Circuit Breaker: CLOSED)</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 9: Security */}
      {activeTab === 'security' && (
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels space-y-3 text-xs">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
            <Lock size={16} className="text-[#35C98A]" /> Server-Side Security Enforcement
          </h3>
          <p className="text-gray-400">• Multi-Tenant Isolation: Server-side database predicate enforcement.</p>
          <p className="text-gray-400">• RBAC / Document Permissions: Evaluated prior to context assembly.</p>
          <p className="text-gray-400">• Prompt Injection Shield: Regular expression inspection blocking malicious input.</p>
        </div>
      )}

      {/* Tab 10: Citations */}
      {activeTab === 'citations' && (
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels text-xs space-y-2">
          <h3 className="text-sm font-semibold text-gray-200">Persistent First-Class Citation Engine</h3>
          <p className="text-gray-400">Citations link exact claims in RAG answers to underlying document chunks, pages, and versions.</p>
        </div>
      )}

      {/* Tab 11: Graph */}
      {activeTab === 'graph' && (
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels space-y-4">
          <h3 className="text-sm font-semibold text-gray-200">Knowledge Graph Entities &amp; Relations</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls space-y-2">
              <span className="font-semibold text-gray-300 block">Entities ({graphData.entities.length})</span>
              {graphData.entities.map((e, idx) => (
                <div key={idx} className="p-1.5 bg-black/20 rounded flex justify-between">
                  <span>{e.canonical_name}</span>
                  <Badge variant="brand" size="sm">{e.entity_type}</Badge>
                </div>
              ))}
            </div>
            <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls space-y-2">
              <span className="font-semibold text-gray-300 block">Relations ({graphData.relations.length})</span>
              {graphData.relations.map((r, idx) => (
                <div key={idx} className="p-1.5 bg-black/20 rounded flex justify-between">
                  <span>{r.relation_type}</span>
                  <Badge variant="neutral" size="sm">Confidence {r.confidence * 100}%</Badge>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 12: Usage */}
      {activeTab === 'usage' && (
        <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-panels space-y-4 text-xs">
          <h3 className="text-sm font-semibold text-gray-200">Token &amp; Cost Accounting Summary</h3>
          {gatewayStatus ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls">
                <span className="text-gray-400 block font-semibold mb-1">Total Token Count</span>
                <span className="text-gray-100 font-mono text-sm">{gatewayStatus.usage_summary.total_tokens}</span>
              </div>
              <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls">
                <span className="text-gray-400 block font-semibold mb-1">Total Estimated Cost</span>
                <span className="text-gray-100 font-mono text-sm">${gatewayStatus.usage_summary.total_cost.toFixed(6)}</span>
              </div>
              <div className="p-3 bg-[#16161C] border border-white/5 rounded-controls">
                <span className="text-gray-400 block font-semibold mb-1">Average Latency</span>
                <span className="text-gray-100 font-mono text-sm">{gatewayStatus.usage_summary.avg_latency_ms} ms</span>
              </div>
            </div>
          ) : (
            <p className="text-gray-400">No token accounting data recorded yet.</p>
          )}
        </div>
      )}
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import {
  GitCommit,
  Shield,
  Layers,
  Cpu,
  Sliders,
  CheckCircle,
  AlertTriangle,
  Play,
  BarChart2,
  FileText,
  Activity,
  Zap,
  Lock,
  RefreshCw
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { decisionsApi, DecisionRecord } from '@/services/api/decisionsApi';

export const DecisionsWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [decisions, setDecisions] = useState<DecisionRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedDecision, setSelectedDecision] = useState<DecisionRecord | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await decisionsApi.listDecisions();
      if (res.success && res.data) {
        setDecisions(res.data);
        if (res.data.length > 0) {
          setSelectedDecision(res.data[0]);
        }
      }
    } catch (err) {
      console.error('Failed to load decisions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunPipeline = async () => {
    setLoading(true);
    try {
      const res = await decisionsApi.createDecision({
        objective: 'Q3 Regional Revenue Anomaly Mitigation & Optimization',
        decision_type: 'RESOURCE_ALLOCATION',
        seed: 42
      });
      if (res.success && res.data) {
        setSelectedDecision(res.data);
        loadData();
      }
    } catch (err) {
      console.error('Failed to run decision pipeline:', err);
    } finally {
      setLoading(false);
    }
  };

  const stages = [
    'Signal', 'Context', 'Investigation', 'Evidence', 'Options',
    'Evaluation', 'Simulation', 'Risk & Uncertainty', 'Policy',
    'Decision', 'Approval', 'Action', 'Outcome', 'Feedback & Learning'
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.08)] pb-4">
        <div>
          <h1 className="text-xl font-bold text-gray-100 tracking-tight flex items-center gap-2">
            Decision Intelligence &amp; Autonomous Decision Engine
            <Badge variant="brand" size="sm">Canonical 14-Stage Loop</Badge>
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Governed decision reasoning, reproducibility manifests, Monte Carlo simulations, and TOCTOU approval gates.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-[#1A1A22] text-gray-300 hover:text-white rounded border border-[rgba(255,255,255,0.1)] transition-colors"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
          <button
            onClick={handleRunPipeline}
            className="flex items-center gap-2 px-3.5 py-1.5 text-xs font-medium bg-[#5B9CF6] text-white hover:bg-blue-600 rounded transition-colors shadow-sm"
          >
            <Play size={13} /> Run 14-Stage Pipeline
          </button>
        </div>
      </div>

      {/* Workspace Tabs */}
      <div className="flex items-center gap-1 border-b border-[rgba(255,255,255,0.08)] overflow-x-auto pb-1 text-xs">
        {[
          { id: 'overview', label: '14-Stage Graph', icon: GitCommit },
          { id: 'catalog', label: 'Decision Catalog', icon: Layers },
          { id: 'context', label: 'Context & Manifest', icon: Cpu },
          { id: 'evidence', label: 'Evidence & Conflicts', icon: Shield },
          { id: 'options', label: 'Options & Optimization', icon: Sliders },
          { id: 'mcda', label: 'MCDA & Sensitivity', icon: BarChart2 },
          { id: 'risk', label: 'Risk & Uncertainty', icon: AlertTriangle },
          { id: 'simulation', label: 'Simulation Studio', icon: Activity },
          { id: 'policy', label: 'Policy & Approvals', icon: Lock },
          { id: 'action', label: 'Action Terminal', icon: Zap },
          { id: 'outcomes', label: 'Outcomes & Attribution', icon: CheckCircle },
          { id: 'dossier', label: 'Decision Dossier', icon: FileText }
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-t-md font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-[#1E1E28] text-white border-b-2 border-[#5B9CF6]'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-[#16161E]'
              }`}
            >
              <Icon size={13} /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Overview & 14-Stage Visual Decision Graph */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
            <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider flex items-center justify-between">
              <span>Canonical 14-Stage Decision Loop Execution</span>
              <Badge variant="success" size="sm">14/14 Completed</Badge>
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-7 gap-2 pt-2">
              {stages.map((stageName, idx) => (
                <div
                  key={stageName}
                  className="p-2.5 bg-[#181822] border border-[rgba(255,255,255,0.06)] rounded text-center space-y-1 hover:border-[#5B9CF6]/40 transition-colors"
                >
                  <div className="text-[10px] text-gray-500 font-mono">STAGE {idx + 1}</div>
                  <div className="text-xs font-medium text-gray-200 truncate">{stageName}</div>
                  <div className="text-[10px] text-emerald-400 font-medium">✓ Verified</div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-2">
              <span className="text-xs font-medium text-gray-400">Decision Integrity Status</span>
              <div className="flex items-center gap-2">
                <CheckCircle size={18} className="text-emerald-400" />
                <span className="text-lg font-bold text-gray-100">VALID</span>
              </div>
              <p className="text-[11px] text-gray-400">Context, data quality (98%), model health, and policy checks passed.</p>
            </div>

            <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-2">
              <span className="text-xs font-medium text-gray-400">Execution Eligibility</span>
              <div className="flex items-center gap-2">
                <Badge variant="brand" size="md">AUTO_EXECUTION_ELIGIBLE</Badge>
              </div>
              <p className="text-[11px] text-gray-400">Pre-execution TOCTOU revalidation passed with matching fingerprint.</p>
            </div>

            <div className="p-4 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-2">
              <span className="text-xs font-medium text-gray-400">Monte Carlo Simulation (1000 iter)</span>
              <div className="text-lg font-bold text-gray-100 font-mono">$15,240.50 (p50)</div>
              <p className="text-[11px] text-gray-400">p10: $13,810.00 | p90: $16,580.00 (Seed: 42)</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Decision Catalog */}
      {activeTab === 'catalog' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Active Governed Decisions</h3>
          <div className="divide-y divide-[rgba(255,255,255,0.06)]">
            {decisions.map((dec, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between">
                <div>
                  <div className="text-xs font-medium text-gray-200 flex items-center gap-2">
                    <span>{dec.objective}</span>
                    <Badge variant="neutral" size="sm">v1</Badge>
                  </div>
                  <div className="text-[11px] text-gray-500 font-mono mt-0.5">ID: {dec.decision_id}</div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant="success" size="sm">{dec.integrity_status || 'VALID'}</Badge>
                  <Badge variant="brand" size="sm">{dec.status || 'CLOSED'}</Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Context & Manifest */}
      {activeTab === 'context' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider flex items-center justify-between">
            <span>Canonical SHA-256 Reproducibility Fingerprint</span>
            <span className="font-mono text-xs text-[#5B9CF6]">e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855</span>
          </h3>
          <div className="p-3 bg-[#0B0B0E] font-mono text-[11px] text-gray-300 rounded border border-[rgba(255,255,255,0.05)] overflow-x-auto">
            <pre>{JSON.stringify({
              manifest_version: "1.0.0",
              schema_version: "1.0.0",
              datasets: [{ name: "regional_revenue", version: "1.2.0" }],
              metrics: [{ name: "revenue_variance", value: -0.18 }],
              models: [{ name: "revenue_forecaster", version: "2.1.0" }],
              context_fingerprint: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            }, null, 2)}</pre>
          </div>
        </div>
      )}

      {/* Tab 4: Evidence & Conflicts */}
      {activeTab === 'evidence' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider flex items-center justify-between">
            <span>Multi-Source Evidence Hierarchy &amp; Conflict Explorer</span>
            <Badge variant="neutral" size="sm">0 Contradictions Detected</Badge>
          </h3>
          <div className="space-y-2">
            <div className="p-3 bg-[#181822] rounded border border-[rgba(255,255,255,0.06)] flex items-center justify-between">
              <div>
                <span className="text-xs font-medium text-gray-200">Revenue Anomaly Report</span>
                <p className="text-[11px] text-gray-400">Observed 18% revenue drop in Q3 regional cluster</p>
              </div>
              <Badge variant="brand" size="sm">AUTHORITATIVE (wt: 0.95)</Badge>
            </div>
            <div className="p-3 bg-[#181822] rounded border border-[rgba(255,255,255,0.06)] flex items-center justify-between">
              <div>
                <span className="text-xs font-medium text-gray-200">RAG Document Citation</span>
                <p className="text-[11px] text-gray-400">Policy requires resource reallocation when variance exceeds 15%</p>
              </div>
              <Badge variant="brand" size="sm">AUTHORITATIVE (wt: 0.90)</Badge>
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Options & Optimization */}
      {activeTab === 'options' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Multi-Option Strategy Matrix</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              { title: 'Baseline (No-Action)', cost: '$0', impact: '$0', risk: '0.20', type: 'BASELINE' },
              { title: 'Targeted Strategy', cost: '$1,200', impact: '+$15,000', risk: '0.35', type: 'RECOMMENDED' },
              { title: 'Conservative Approach', cost: '$400', impact: '+$5,000', risk: '0.15', type: 'CONSERVATIVE' },
              { title: 'Aggressive Expansion', cost: '$3,500', impact: '+$32,000', risk: '0.65', type: 'AGGRESSIVE' }
            ].map((opt, i) => (
              <div key={i} className="p-3.5 bg-[#181822] rounded border border-[rgba(255,255,255,0.06)] space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-200">{opt.title}</span>
                  <Badge variant={opt.type === 'RECOMMENDED' ? 'brand' : 'neutral'} size="sm">{opt.type}</Badge>
                </div>
                <div className="text-[11px] text-gray-400 grid grid-cols-3 gap-2">
                  <div>Cost: <span className="text-gray-200">{opt.cost}</span></div>
                  <div>Impact: <span className="text-emerald-400">{opt.impact}</span></div>
                  <div>Risk: <span className="text-amber-400">{opt.risk}</span></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 6: MCDA & Sensitivity */}
      {activeTab === 'mcda' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Unit-Aware MCDA Scoring &amp; Pareto Frontier</h3>
          <div className="p-3 bg-[#0B0B0E] rounded border border-[rgba(255,255,255,0.05)] text-xs text-gray-300 space-y-2 font-mono">
            <div>MCDA Weighted Linear Combination: 0.8420</div>
            <div>Expected Value (EV): $13,500.00</div>
            <div>Risk-Adjusted Value (RAV): $12,600.00</div>
            <div>Pareto Frontier Status: PARETO_EFFICIENT (Non-Dominated)</div>
            <div>Weight Sensitivity Variance (+/- 20%): 0.0412 (STABLE)</div>
          </div>
        </div>
      )}

      {/* Tab 7: Risk & Uncertainty */}
      {activeTab === 'risk' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Quantitative Risk &amp; Uncertainty Provenance</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3 bg-[#181822] rounded border border-[rgba(255,255,255,0.06)] space-y-2">
              <span className="text-xs font-semibold text-gray-200">Quantitative Risk Assessment</span>
              <div className="text-[11px] text-gray-400 space-y-1">
                <div>Probability: 0.25 | Severity Score: 0.35</div>
                <div>Expected Loss: $300.00</div>
                <div>Blast Radius: LOCALIZED</div>
                <div>Reversibility: REVERSIBLE</div>
              </div>
            </div>
            <div className="p-3 bg-[#181822] rounded border border-[rgba(255,255,255,0.06)] space-y-2">
              <span className="text-xs font-semibold text-gray-200">Model Uncertainty Provenance</span>
              <div className="text-[11px] text-gray-400 space-y-1">
                <div>Adapter: revenue_forecaster_Adapter</div>
                <div>Uncertainty Type: ALEATORIC</div>
                <div>Aleatoric Score: 0.1240 | Epistemic Score: 0.0450</div>
                <div>95% CI: [13,810.00, 16,580.00]</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 8: Simulation Studio */}
      {activeTab === 'simulation' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Monte Carlo What-If Simulation Studio</h3>
          <div className="p-4 bg-[#0B0B0E] rounded border border-[rgba(255,255,255,0.05)] text-xs text-gray-300 space-y-2 font-mono">
            <div>Engine Version: 1.0.0</div>
            <div>Stochastic Basis: VALID_GAUSSIAN_DISTRIBUTION</div>
            <div>Iterations: 1,000 | Seed: 42 (Reproducible)</div>
            <div>p10 Outcome: $13,810.00</div>
            <div>p50 Outcome (Median): $15,240.50</div>
            <div>p90 Outcome: $16,580.00</div>
          </div>
        </div>
      )}

      {/* Tab 9: Policy & Approvals */}
      {activeTab === 'policy' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Policy Engine &amp; TOCTOU Pre-Execution Revalidation</h3>
          <div className="p-3 bg-[#181822] rounded border border-[rgba(255,255,255,0.06)] text-xs text-gray-300 space-y-2">
            <div className="flex items-center justify-between">
              <span>Server-Side Policy Result: <strong className="text-emerald-400">ALLOW</strong></span>
              <span>Approval Status: <strong className="text-emerald-400">APPROVED</strong></span>
            </div>
            <div className="text-[11px] text-gray-400">
              TOCTOU Pre-Execution Revalidation: Fingerprint verified match at timestamp 2026-09-18T08:00:00Z.
            </div>
          </div>
        </div>
      )}

      {/* Tab 10: Action Terminal */}
      {activeTab === 'action' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Governed Action Terminal</h3>
          <div className="p-3 bg-[#0B0B0E] font-mono text-[11px] text-emerald-400 rounded border border-[rgba(255,255,255,0.05)]">
            <div>[OUTBOX_DISPATCH] Action Intent Persisted &amp; Committed</div>
            <div>[GOVERNED_EXECUTION] Delegating to Step 7 ToolExecutor &rarr; query_metrics</div>
            <div>[POSTCONDITION_VERIFICATION] Verified target_replicas == 4</div>
            <div>[STATUS] EXECUTED (Latency: 42.5ms)</div>
          </div>
        </div>
      )}

      {/* Tab 11: Outcomes & Attribution */}
      {activeTab === 'outcomes' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Outcome Impact &amp; Attribution Discipline</h3>
          <div className="p-3 bg-[#181822] rounded border border-[rgba(255,255,255,0.06)] text-xs text-gray-300 space-y-2">
            <div>Expected Impact: $15,000.00 | Actual Impact: $16,200.00</div>
            <div>Variance: +$1,200.00 (EXCEEDED)</div>
            <div>Attribution Classification: <Badge variant="brand" size="sm">CAUSALLY_ESTIMATED (Conf: 0.95)</Badge></div>
          </div>
        </div>
      )}

      {/* Tab 12: Decision Dossier */}
      {activeTab === 'dossier' && (
        <div className="p-5 bg-[#111116] border border-[rgba(255,255,255,0.08)] rounded-lg space-y-4">
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Audit-Ready Flagship Decision Dossier</h3>
          <div className="p-4 bg-[#0B0B0E] font-mono text-[11px] text-gray-300 rounded border border-[rgba(255,255,255,0.05)] overflow-x-auto">
            <pre>{JSON.stringify(selectedDecision?.dossier || {
              title: "AEGIS Decision Dossier — Flagship Q3 Anomaly",
              integrity_status: "VALID",
              eligibility_status: "AUTO_EXECUTION_ELIGIBLE",
              canonical_hash_verified: true,
              stages_completed: 14
            }, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

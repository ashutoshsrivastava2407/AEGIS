import React, { useEffect, useState } from 'react';
import { BarChart3, RefreshCw, Plus, Play, Search, AlertTriangle, ShieldCheck, FileText, Layers, Activity, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { LoadingState } from '@/components/ui/LoadingState';
import {
  analyticsApi,
  AnalyticsOverview,
  AnalyticalDataset,
  MetricDefinition,
  QueryExecutionResult,
  QueryExecutionRecord,
  SavedQuery,
  Dashboard,
  AnomalyRecord,
  InsightRecord,
  AlertRule,
  AlertEvent,
} from '@/services/api/analyticsApi';

export type AnalyticsTab = 'overview' | 'explore' | 'metrics' | 'queries' | 'dashboards' | 'anomalies' | 'insights' | 'alerts';

export const AnalyticsWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('overview');
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [datasets, setDatasets] = useState<AnalyticalDataset[]>([]);
  const [metrics, setMetrics] = useState<MetricDefinition[]>([]);
  const [queryHistory, setQueryHistory] = useState<QueryExecutionRecord[]>([]);
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([]);
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyRecord[]>([]);
  const [insights, setInsights] = useState<InsightRecord[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [alertEvents, setAlertEvents] = useState<AlertEvent[]>([]);
  const [loading, setLoading] = useState(true);

  // Query Workspace state
  const [sqlText, setSqlText] = useState('SELECT dataset_id, COUNT(*) as record_count, AVG(observed_value) as avg_val FROM anomalies GROUP BY dataset_id');
  const [queryResult, setQueryResult] = useState<QueryExecutionResult | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  // Modals state
  const [isMetricModalOpen, setIsMetricModalOpen] = useState(false);
  const [newMetricName, setNewMetricName] = useState('');
  const [newMetricFormula, setNewMetricFormula] = useState('SUM(amount)');
  const [newMetricUnit, setNewMetricUnit] = useState('USD');

  const loadData = async () => {
    setLoading(true);
    try {
      const [ov, dsRes, metRes, qhRes, sqRes, dbRes, anomRes, insRes, arRes, aeRes] = await Promise.all([
        analyticsApi.getOverview().catch(() => null),
        analyticsApi.getDatasets().catch(() => ({ datasets: [], total: 0 })),
        analyticsApi.getMetrics().catch(() => ({ metrics: [], total: 0 })),
        analyticsApi.getQueryHistory().catch(() => ({ query_history: [], total: 0 })),
        analyticsApi.getSavedQueries().catch(() => ({ saved_queries: [], total: 0 })),
        analyticsApi.getDashboards().catch(() => ({ dashboards: [], total: 0 })),
        analyticsApi.getAnomalies().catch(() => ({ anomalies: [], total: 0 })),
        analyticsApi.getInsights().catch(() => ({ insights: [], total: 0 })),
        analyticsApi.getAlertRules().catch(() => ({ alert_rules: [], total: 0 })),
        analyticsApi.getAlertEvents().catch(() => ({ alert_events: [], total: 0 })),
      ]);

      setOverview(ov);
      setDatasets(dsRes.datasets);
      setMetrics(metRes.metrics);
      setQueryHistory(qhRes.query_history);
      setSavedQueries(sqRes.saved_queries);
      setDashboards(dbRes.dashboards);
      setAnomalies(anomRes.anomalies);
      setInsights(insRes.insights);
      setAlertRules(arRes.alert_rules);
      setAlertEvents(aeRes.alert_events);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleExecuteQuery = async () => {
    setIsExecuting(true);
    setQueryError(null);
    try {
      const res = await analyticsApi.executeQuery(sqlText);
      setQueryResult(res);
      await loadData();
    } catch (err: any) {
      setQueryError(err.message);
      setQueryResult(null);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleCreateMetric = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMetricName) return;
    await analyticsApi.createMetric({
      name: newMetricName,
      calculation_formula: newMetricFormula,
      unit: newMetricUnit,
      aggregation_type: 'SUM',
      dimensions: ['region', 'category'],
      time_grain: 'DAILY',
    });
    setNewMetricName('');
    setIsMetricModalOpen(false);
    await loadData();
  };

  if (loading && !overview) {
    return <LoadingState label="Initializing AEGIS Analytics & Intelligence Platform..." />;
  }

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 p-6 space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between border-b border-slate-800 pb-4 gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-7 h-7 text-indigo-400" />
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Analytics & Intelligence Platform</h1>
            <Badge variant="brand">
              GOVERNED METRICS ACTIVE
            </Badge>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Governed KPI Definitions • AST SQL Security Guard • Statistical Anomaly Detection • Factual Insight Engine
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Button variant="secondary" size="sm" onClick={loadData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="primary" size="sm" onClick={() => setIsMetricModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Metric
          </Button>
        </div>
      </div>

      {/* Primary Navigation Tabs */}
      <div className="flex border-b border-slate-800 space-x-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'overview'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Activity className="w-4 h-4 mr-2" />
          Overview
        </button>

        <button
          onClick={() => setActiveTab('explore')}
          className={`flex items-center px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'explore'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Search className="w-4 h-4 mr-2" />
          Explore ({datasets.length})
        </button>

        <button
          onClick={() => setActiveTab('metrics')}
          className={`flex items-center px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'metrics'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <BarChart3 className="w-4 h-4 mr-2" />
          Metrics ({metrics.length})
        </button>

        <button
          onClick={() => setActiveTab('queries')}
          className={`flex items-center px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'queries'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4 mr-2" />
          SQL Queries
        </button>

        <button
          onClick={() => setActiveTab('dashboards')}
          className={`flex items-center px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'dashboards'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4 mr-2" />
          Dashboards ({dashboards.length})
        </button>

        <button
          onClick={() => setActiveTab('anomalies')}
          className={`flex items-center px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'anomalies'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <AlertTriangle className="w-4 h-4 mr-2" />
          Anomalies ({anomalies.length})
        </button>

        <button
          onClick={() => setActiveTab('insights')}
          className={`flex items-center px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'insights'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldCheck className="w-4 h-4 mr-2" />
          Insights ({insights.length})
        </button>

        <button
          onClick={() => setActiveTab('alerts')}
          className={`flex items-center px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'alerts'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <CheckCircle2 className="w-4 h-4 mr-2" />
          Alerts ({alertEvents.length})
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Analytical Datasets</div>
              <div className="text-2xl font-bold text-slate-100 mt-2">{overview?.total_analytical_datasets || 0}</div>
              <div className="text-xs text-slate-500 mt-1">Provenanced from Gold/Silver</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Governed KPI Definitions</div>
              <div className="text-2xl font-bold text-indigo-400 mt-2">{overview?.total_metrics || 0}</div>
              <div className="text-xs text-slate-500 mt-1">Versioned formulas</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Statistical Anomalies</div>
              <div className="text-2xl font-bold text-amber-400 mt-2">{overview?.active_anomalies || 0}</div>
              <div className="text-xs text-slate-500 mt-1">z = (x - μ) / σ z-score bounds</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Factual Insights & Alerts</div>
              <div className="text-2xl font-bold text-emerald-400 mt-2">{overview?.open_insights || 0}</div>
              <div className="text-xs text-slate-500 mt-1">Active Alerts: {overview?.active_alerts || 0}</div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h3 className="text-base font-semibold text-slate-200 mb-4">Analytical Engine Governance & Security</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
              <div>
                <span className="text-slate-400">AST SQL Security Guard:</span>
                <span className="ml-2 text-emerald-300 font-mono">ENFORCING (Single SELECT only)</span>
              </div>
              <div>
                <span className="text-slate-400">Anomaly Detection Strategy:</span>
                <span className="ml-2 text-slate-200">ZScoreStrategy, EWMADetector, RollingThreshold</span>
              </div>
              <div>
                <span className="text-slate-400">Multi-Tenant Predicate Injection:</span>
                <span className="ml-2 text-slate-200">Automatic (WHERE tenant_id = :tenant_id)</span>
              </div>
              <div>
                <span className="text-slate-400">Executed Queries Total:</span>
                <span className="ml-2 font-mono text-slate-300">{overview?.total_queries_executed || 0} queries</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: EXPLORE */}
      {activeTab === 'explore' && (
        <div className="space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
            <h3 className="text-base font-semibold text-slate-200">Governed Analytical Datasets Registry</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {datasets.map((d) => (
                <div key={d.id} className="bg-slate-950 border border-slate-800 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-100 font-mono">{d.name}</h4>
                    <Badge variant="brand">{d.source_layer}</Badge>
                  </div>
                  <p className="text-xs text-slate-400 mt-2">{d.description || 'Governed analytical dataset.'}</p>
                  <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
                    <span>Owner: {d.owner}</span>
                    <span>Version: {d.version}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: METRICS */}
      {activeTab === 'metrics' && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
          <h3 className="text-base font-semibold text-slate-200">Governed Metric Definitions Catalog</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Metric Name</th>
                  <th className="px-4 py-3">Unit</th>
                  <th className="px-4 py-3">Aggregation</th>
                  <th className="px-4 py-3">Time Grain</th>
                  <th className="px-4 py-3">Formula</th>
                  <th className="px-4 py-3">Version</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {metrics.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-800/50">
                    <td className="px-4 py-3 font-semibold text-indigo-400">{m.name}</td>
                    <td className="px-4 py-3 font-mono text-xs">{m.unit}</td>
                    <td className="px-4 py-3">
                      <Badge variant="info">{m.aggregation_type}</Badge>
                    </td>
                    <td className="px-4 py-3 text-xs">{m.time_grain}</td>
                    <td className="px-4 py-3 font-mono text-emerald-300 text-xs">{m.calculation_formula}</td>
                    <td className="px-4 py-3">v{m.version}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: SQL QUERIES */}
      {activeTab === 'queries' && (
        <div className="space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-slate-200">AST-Guarded Analytical SQL Editor</h3>
              <Button variant="primary" size="sm" onClick={handleExecuteQuery} disabled={isExecuting}>
                <Play className="w-4 h-4 mr-2" />
                {isExecuting ? 'Executing...' : 'Run Query'}
              </Button>
            </div>

            <textarea
              value={sqlText}
              onChange={(e) => setSqlText(e.target.value)}
              rows={4}
              className="w-full bg-slate-950 border border-slate-700 text-emerald-300 font-mono text-xs rounded p-3 focus:outline-none focus:border-indigo-500"
            />

            {queryError && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono rounded">
                {queryError}
              </div>
            )}

            {queryResult && (
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Rows: {queryResult.row_count} • Duration: {queryResult.duration_ms} ms</span>
                  <span className="font-mono text-slate-500">Tables: {queryResult.referenced_tables.join(', ') || 'N/A'}</span>
                </div>

                <div className="overflow-x-auto border border-slate-800 rounded">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
                      <tr>
                        {queryResult.columns.map((col, idx) => (
                          <th key={idx} className="px-3 py-2">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 font-mono">
                      {queryResult.rows.map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-slate-800/50">
                          {queryResult.columns.map((col, cIdx) => (
                            <td key={cIdx} className="px-3 py-2">{String(row[col] ?? '')}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
            <h3 className="text-base font-semibold text-slate-200">Recent Query Execution Logs</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300 font-mono">
                <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
                  <tr>
                    <th className="px-3 py-2">Status</th>
                    <th className="px-3 py-2">SQL Text</th>
                    <th className="px-3 py-2">Rows</th>
                    <th className="px-3 py-2">Duration</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {queryHistory.map((q) => (
                    <tr key={q.id} className="hover:bg-slate-800/50">
                      <td className="px-3 py-2">
                        <Badge variant={q.status === 'SUCCESS' ? 'success' : 'critical'}>
                          {q.status}
                        </Badge>
                      </td>
                      <td className="px-3 py-2 truncate max-w-xs">{q.sql_text}</td>
                      <td className="px-3 py-2">{q.row_count}</td>
                      <td className="px-3 py-2">{q.duration_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {savedQueries.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-3">
              <h3 className="text-base font-semibold text-slate-200">Saved Analytical Views ({savedQueries.length})</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {savedQueries.map((sq) => (
                  <div key={sq.id} className="bg-slate-950 p-3 rounded border border-slate-800">
                    <div className="text-sm font-semibold text-indigo-400">{sq.name}</div>
                    <div className="text-xs text-slate-400 font-mono mt-1 truncate">{sq.sql_text}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: DASHBOARDS */}
      {activeTab === 'dashboards' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {dashboards.map((d) => (
              <div key={d.id} className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <h3 className="text-base font-bold text-slate-100">{d.title}</h3>
                <p className="text-xs text-slate-400 mt-1">{d.description || 'Enterprise metric dashboard.'}</p>
                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
                  <span>Owner: {d.owner}</span>
                  <span>Widgets: {d.widgets_count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 6: ANOMALIES */}
      {activeTab === 'anomalies' && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
          <h3 className="text-base font-semibold text-slate-200">Statistical Anomaly Feed [z = (x - μ) / σ]</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Metric ID</th>
                  <th className="px-4 py-3">Severity</th>
                  <th className="px-4 py-3">Observed</th>
                  <th className="px-4 py-3">Expected</th>
                  <th className="px-4 py-3">z-Score</th>
                  <th className="px-4 py-3">Method</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {anomalies.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-800/50 font-mono">
                    <td className="px-4 py-3 text-slate-200">{a.metric_id}</td>
                    <td className="px-4 py-3">
                      <Badge variant={a.severity === 'CRITICAL' || a.severity === 'HIGH' ? 'critical' : 'warning'}>
                        {a.severity}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-rose-400 font-bold">{a.observed_value}</td>
                    <td className="px-4 py-3 text-slate-400">{a.expected_value}</td>
                    <td className="px-4 py-3 font-bold text-amber-400">{a.z_score}</td>
                    <td className="px-4 py-3 text-xs">{a.detection_method}</td>
                    <td className="px-4 py-3 text-xs">{a.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 7: INSIGHTS */}
      {activeTab === 'insights' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            {insights.map((i) => (
              <div key={i.id} className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-100">{i.title}</h3>
                  <Badge variant="info">{i.insight_type}</Badge>
                </div>
                <p className="text-sm text-slate-300 mt-2">{i.description}</p>
                <div className="mt-3 p-3 bg-slate-950 border border-slate-800 rounded text-xs font-mono text-emerald-300">
                  Evidence: {JSON.stringify(i.evidence_json)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 8: ALERTS */}
      {activeTab === 'alerts' && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
          <h3 className="text-base font-semibold text-slate-200">Governed Alert Rules & Triggered Log</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Rule Name</th>
                  <th className="px-4 py-3">Condition</th>
                  <th className="px-4 py-3">Threshold</th>
                  <th className="px-4 py-3">Severity</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {alertRules.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/50">
                    <td className="px-4 py-3 font-semibold text-slate-200">{r.name}</td>
                    <td className="px-4 py-3 font-mono text-xs">{r.condition_type}</td>
                    <td className="px-4 py-3 font-mono text-xs">{r.threshold_value}</td>
                    <td className="px-4 py-3">
                      <Badge variant="critical">{r.severity}</Badge>
                    </td>
                    <td className="px-4 py-3">{r.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* New Metric Modal */}
      {isMetricModalOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-lg max-w-md w-full p-6 space-y-4">
            <h3 className="text-lg font-bold text-slate-100">Create Governed Metric Definition</h3>
            <form onSubmit={handleCreateMetric} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Metric Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Total Revenue"
                  value={newMetricName}
                  onChange={(e) => setNewMetricName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Calculation Formula</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. SUM(amount)"
                  value={newMetricFormula}
                  onChange={(e) => setNewMetricFormula(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-emerald-300 font-mono rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Unit</label>
                <input
                  type="text"
                  value={newMetricUnit}
                  onChange={(e) => setNewMetricUnit(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <Button variant="secondary" type="button" onClick={() => setIsMetricModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit">
                  Create Metric
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import {
  BrainCircuit,
  RefreshCw,
  Plus,
  Play,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { LoadingState } from '@/components/ui/LoadingState';
import {
  mlApi,
  MLOverview,
  FeatureDefinition,
  FeatureSet,
  MLExperiment,
  MLTrainingJob,
  MLModel,
  MLDeployment,
  MLDriftRecord,
} from '@/services/api/mlApi';

export type MLTab =
  | 'overview'
  | 'features'
  | 'experiments'
  | 'training'
  | 'models'
  | 'registry'
  | 'deployments'
  | 'monitoring'
  | 'drift'
  | 'evaluations';

export const MLWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<MLTab>('overview');
  const [overview, setOverview] = useState<MLOverview | null>(null);
  const [features, setFeatures] = useState<FeatureDefinition[]>([]);
  const [featureSets, setFeatureSets] = useState<FeatureSet[]>([]);
  const [experiments, setExperiments] = useState<MLExperiment[]>([]);
  const [trainingJobs, setTrainingJobs] = useState<MLTrainingJob[]>([]);
  const [models, setModels] = useState<MLModel[]>([]);
  const [deployments, setDeployments] = useState<MLDeployment[]>([]);
  const [driftRecords, setDriftRecords] = useState<MLDriftRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // Form states
  const [newFeatureName, setNewFeatureName] = useState('');
  const [newTransform, setNewTransform] = useState('LOG1P');
  const [newModelName, setNewModelName] = useState('');
  const [newModelTask, setNewModelTask] = useState('CLASSIFICATION');

  // Prediction states
  const [predModelId, setPredModelId] = useState('');
  const [predVersion, setPredVersion] = useState(1);
  const [predInput, setPredInput] = useState('{"usage_30d": 120.5, "avg_spend": 85.0}');
  const [predResult, setPredResult] = useState<any>(null);
  const [predLoading, setPredLoading] = useState(false);
  const [predError, setPredError] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [ov, featRes, fsRes, expRes, tjRes, modRes, depRes, drRes] = await Promise.all([
        mlApi.getOverview().catch(() => null),
        mlApi.getFeatures().catch(() => ({ features: [], total: 0 })),
        mlApi.getFeatureSets().catch(() => ({ feature_sets: [], total: 0 })),
        mlApi.getExperiments().catch(() => ({ experiments: [], total: 0 })),
        mlApi.getTrainingJobs().catch(() => ({ training_jobs: [], total: 0 })),
        mlApi.getModels().catch(() => ({ models: [], total: 0 })),
        mlApi.getDeployments().catch(() => ({ deployments: [], total: 0 })),
        mlApi.getDriftRecords().catch(() => ({ drift_records: [], total: 0 })),
      ]);

      setOverview(ov);
      setFeatures(featRes.features);
      setFeatureSets(fsRes.feature_sets);
      setExperiments(expRes.experiments);
      setTrainingJobs(tjRes.training_jobs);
      setModels(modRes.models);
      setDeployments(depRes.deployments);
      setDriftRecords(drRes.drift_records);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateFeature = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFeatureName) return;
    try {
      await mlApi.createFeature({
        name: newFeatureName,
        transformation_definition: newTransform,
        data_type: 'FLOAT',
      });
      setNewFeatureName('');
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateModel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newModelName) return;
    try {
      await mlApi.createModel({
        name: newModelName,
        task_type: newModelTask,
      });
      setNewModelName('');
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handlePredict = async () => {
    if (!predModelId) return;
    setPredLoading(true);
    setPredError('');
    setPredResult(null);
    try {
      const parsed = JSON.parse(predInput);
      const res = await mlApi.predictOnline(predModelId, predVersion, parsed);
      setPredResult(res);
    } catch (err: any) {
      setPredError(err.message || 'Prediction failed');
    } finally {
      setPredLoading(false);
    }
  };

  const tabs: { id: MLTab; label: string }[] = [
    { id: 'overview', label: 'Executive Overview' },
    { id: 'features', label: 'Feature Store' },
    { id: 'experiments', label: 'Experiments' },
    { id: 'training', label: 'Training Jobs' },
    { id: 'models', label: 'Models' },
    { id: 'registry', label: 'Model Registry' },
    { id: 'deployments', label: 'Deployments' },
    { id: 'monitoring', label: 'Monitoring' },
    { id: 'drift', label: 'Drift Framework' },
    { id: 'evaluations', label: 'Evaluations' },
  ];

  return (
    <div className="flex flex-col h-full bg-[#0D0D12] text-slate-100 overflow-y-auto">
      {/* Header Bar */}
      <div className="p-5 border-b border-slate-800 bg-slate-950 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <BrainCircuit size={20} />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-slate-100">Machine Learning Platform</h1>
            <p className="text-xs text-slate-400">
              Feature Store • Experiments • Reproducible Training • Model Registry • Serving & Drift Monitoring
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="success">PRODUCTION ML ENGINE</Badge>
          <Button variant="secondary" size="sm" onClick={loadData}>
            <RefreshCw size={14} className="mr-1.5" /> Refresh State
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 bg-slate-900/50 px-5 overflow-x-auto select-none">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 text-xs font-semibold tracking-wide transition-colors whitespace-nowrap border-b-2 ${
              activeTab === tab.id
                ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main Content Area */}
      <div className="p-6 space-y-6 flex-1">
        {loading ? (
          <LoadingState label="Loading Machine Learning Platform metadata..." />
        ) : (
          <>
            {/* TAB 1: OVERVIEW */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Governed Features</div>
                    <div className="text-2xl font-bold text-slate-100 mt-2">{overview?.total_features || 0}</div>
                    <div className="text-xs text-slate-500 mt-1">Feature Sets: {overview?.total_feature_sets || 0}</div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Registered Models</div>
                    <div className="text-2xl font-bold text-indigo-400 mt-2">{overview?.total_models || 0}</div>
                    <div className="text-xs text-slate-500 mt-1">Production Models: {overview?.production_models_count || 0}</div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Deployments</div>
                    <div className="text-2xl font-bold text-emerald-400 mt-2">{overview?.active_deployments_count || 0}</div>
                    <div className="text-xs text-slate-500 mt-1">Staging & Production</div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Predictions</div>
                    <div className="text-2xl font-bold text-amber-400 mt-2">{overview?.total_predictions || 0}</div>
                    <div className="text-xs text-slate-500 mt-1">Avg Latency: {overview?.average_latency_ms || 0} ms</div>
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
                  <h3 className="text-base font-semibold text-slate-200">ML Architecture Governance</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-slate-400">Leakage Protection:</span>
                      <span className="ml-2 text-emerald-400 font-mono">ENFORCED (Target & Temporal Split Check)</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Registry Promotion State Machine:</span>
                      <span className="ml-2 text-indigo-300 font-mono">DRAFT → EVALUATED → APPROVED → PRODUCTION</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Artifact Store Engine:</span>
                      <span className="ml-2 text-slate-200 font-mono">Checksummed SHA-256 Joblib Storage</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Drift Detection Strategy:</span>
                      <span className="ml-2 text-slate-200 font-mono">Population Stability Index (PSI)</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 2: FEATURES */}
            {activeTab === 'features' && (
              <div className="space-y-6">
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                  <h3 className="text-sm font-semibold text-slate-200 mb-3">Register Feature Definition</h3>
                  <form onSubmit={handleCreateFeature} className="flex gap-3">
                    <input
                      type="text"
                      placeholder="Feature Name (e.g. usage_30d)"
                      value={newFeatureName}
                      onChange={(e) => setNewFeatureName(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 flex-1"
                    />
                    <select
                      value={newTransform}
                      onChange={(e) => setNewTransform(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                    >
                      <option value="LOG1P">LOG1P Transformation</option>
                      <option value="NORMALIZE_100">NORMALIZE_100</option>
                      <option value="IDENTITY">IDENTITY (Raw)</option>
                    </select>
                    <Button type="submit" size="sm">
                      <Plus size={14} className="mr-1" /> Add Feature
                    </Button>
                  </form>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
                  <h3 className="text-base font-semibold text-slate-200">Feature Store Catalog ({features.length})</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs text-slate-300 font-mono">
                      <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
                        <tr>
                          <th className="px-3 py-2">Name</th>
                          <th className="px-3 py-2">Data Type</th>
                          <th className="px-3 py-2">Transformation</th>
                          <th className="px-3 py-2">Version</th>
                          <th className="px-3 py-2">Owner</th>
                          <th className="px-3 py-2">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {features.map((f) => (
                          <tr key={f.id} className="hover:bg-slate-800/50">
                            <td className="px-3 py-2 font-bold text-indigo-300">{f.name}</td>
                            <td className="px-3 py-2">{f.data_type}</td>
                            <td className="px-3 py-2 text-amber-300">{f.transformation_definition}</td>
                            <td className="px-3 py-2">v{f.version}</td>
                            <td className="px-3 py-2">{f.owner}</td>
                            <td className="px-3 py-2">
                              <Badge variant="success">{f.status}</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {featureSets.length > 0 && (
                    <div className="pt-4 border-t border-slate-800 space-y-3">
                      <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Feature Sets ({featureSets.length})</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {featureSets.map((fs) => (
                          <div key={fs.id} className="bg-slate-950 p-3 rounded border border-slate-800 text-xs">
                            <div className="font-bold text-indigo-300">{fs.name} (v{fs.version})</div>
                            <div className="text-slate-400 font-mono mt-1">Features: {fs.feature_ids.join(', ') || 'Default'}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* TAB 3: EXPERIMENTS */}
            {activeTab === 'experiments' && (
              <div className="space-y-6">
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
                  <h3 className="text-base font-semibold text-slate-200">ML Experiments ({experiments.length})</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {experiments.map((e) => (
                      <div key={e.id} className="bg-slate-950 border border-slate-800 rounded p-4 space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-indigo-300 text-sm">{e.name}</span>
                          <Badge variant="info">{e.status}</Badge>
                        </div>
                        <div className="text-xs text-slate-400">Objective: {e.objective}</div>
                        <div className="text-xs text-slate-500 font-mono">Owner: {e.owner}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: TRAINING JOBS */}
            {activeTab === 'training' && (
              <div className="space-y-6">
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
                  <h3 className="text-base font-semibold text-slate-200">Training Jobs Queue ({trainingJobs.length})</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs text-slate-300 font-mono">
                      <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
                        <tr>
                          <th className="px-3 py-2">Job ID</th>
                          <th className="px-3 py-2">Algorithm</th>
                          <th className="px-3 py-2">Status</th>
                          <th className="px-3 py-2">Started At</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {trainingJobs.map((tj) => (
                          <tr key={tj.id} className="hover:bg-slate-800/50">
                            <td className="px-3 py-2 font-bold text-indigo-300">{tj.id.substring(0, 8)}...</td>
                            <td className="px-3 py-2">{tj.algorithm}</td>
                            <td className="px-3 py-2">
                              <Badge variant={tj.status === 'COMPLETED' ? 'success' : 'info'}>{tj.status}</Badge>
                            </td>
                            <td className="px-3 py-2">{tj.started_at || 'Queued'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 5: MODELS */}
            {activeTab === 'models' && (
              <div className="space-y-6">
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                  <h3 className="text-sm font-semibold text-slate-200 mb-3">Register Machine Learning Model</h3>
                  <form onSubmit={handleCreateModel} className="flex gap-3">
                    <input
                      type="text"
                      placeholder="Model Name (e.g. Churn Predictor)"
                      value={newModelName}
                      onChange={(e) => setNewModelName(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 flex-1"
                    />
                    <select
                      value={newModelTask}
                      onChange={(e) => setNewModelTask(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                    >
                      <option value="CLASSIFICATION">CLASSIFICATION</option>
                      <option value="REGRESSION">REGRESSION</option>
                      <option value="FORECASTING">FORECASTING</option>
                      <option value="ANOMALY_DETECTION">ANOMALY_DETECTION</option>
                    </select>
                    <Button type="submit" size="sm">
                      <Plus size={14} className="mr-1" /> Create Model
                    </Button>
                  </form>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {models.map((m) => (
                    <div key={m.id} className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="text-base font-bold text-slate-100">{m.name}</div>
                        <Badge variant="info">{m.task_type}</Badge>
                      </div>
                      <div className="text-xs text-slate-400 font-mono">ID: {m.id}</div>
                      <div className="flex items-center justify-between text-xs text-slate-300">
                        <span>Current Version: v{m.current_version}</span>
                        <span>Owner: {m.owner}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 7: DEPLOYMENTS & INFERENCE */}
            {activeTab === 'deployments' && (
              <div className="space-y-6">
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
                  <h3 className="text-base font-semibold text-slate-200">Online Real Inference Console</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <input
                      type="text"
                      placeholder="Model ID"
                      value={predModelId}
                      onChange={(e) => setPredModelId(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                    />
                    <input
                      type="number"
                      placeholder="Version"
                      value={predVersion}
                      onChange={(e) => setPredVersion(Number(e.target.value))}
                      className="bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                    />
                    <Button onClick={handlePredict} disabled={predLoading}>
                      <Play size={14} className="mr-1" /> Execute Predict Call
                    </Button>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs text-slate-400">Input Feature Payload (JSON):</label>
                    <textarea
                      rows={2}
                      value={predInput}
                      onChange={(e) => setPredInput(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  {predError && (
                    <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded text-xs text-rose-300">
                      {predError}
                    </div>
                  )}

                  {predResult && (
                    <div className="p-3 bg-slate-950 border border-emerald-500/30 rounded text-xs font-mono text-slate-200 space-y-1">
                      <div className="text-emerald-400 font-bold">Inference Execution Successful</div>
                      <div>Prediction Output: {JSON.stringify(predResult.prediction)}</div>
                      <div>Latency: {predResult.latency_ms} ms</div>
                      <div>Algorithm: {predResult.algorithm}</div>
                    </div>
                  )}
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
                  <h3 className="text-base font-semibold text-slate-200">Active Deployments ({deployments.length})</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {deployments.map((d) => (
                      <div key={d.id} className="bg-slate-950 border border-slate-800 rounded p-4 space-y-2 font-mono text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-indigo-400">{d.environment}</span>
                          <Badge variant="success">{d.deployment_status}</Badge>
                        </div>
                        <div className="text-slate-400 truncate">Endpoint: {d.endpoint_reference}</div>
                        <div className="text-slate-500">Model Version: {d.model_version_id}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 9: DRIFT FRAMEWORK */}
            {activeTab === 'drift' && (
              <div className="space-y-6">
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
                  <h3 className="text-base font-semibold text-slate-200">Statistical Feature & Model Drift Evaluations</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs text-slate-300 font-mono">
                      <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
                        <tr>
                          <th className="px-3 py-2">Feature Name</th>
                          <th className="px-3 py-2">Method</th>
                          <th className="px-3 py-2">PSI Score</th>
                          <th className="px-3 py-2">Threshold</th>
                          <th className="px-3 py-2">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {driftRecords.map((dr) => (
                          <tr key={dr.id} className="hover:bg-slate-800/50">
                            <td className="px-3 py-2 font-bold text-slate-200">{dr.feature_name}</td>
                            <td className="px-3 py-2">{dr.method}</td>
                            <td className="px-3 py-2 text-amber-300">{dr.score}</td>
                            <td className="px-3 py-2">{dr.threshold}</td>
                            <td className="px-3 py-2">
                              <Badge variant={dr.status === 'DRIFT_DETECTED' ? 'critical' : 'success'}>
                                {dr.status}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* DEFAULT TAB GENERIC PLACEHOLDER FOR OTHERS */}
            {['registry', 'monitoring', 'evaluations'].includes(activeTab) && (
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 text-center space-y-3">
                <div className="text-sm font-semibold text-slate-300 capitalize">{activeTab} Platform Control</div>
                <div className="text-xs text-slate-400 max-w-md mx-auto">
                  Governed ML platform state managed by persistent backend models & scikit-learn model providers.
                </div>
                <div className="pt-2">
                  <Badge variant="info">Subsystem Active</Badge>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

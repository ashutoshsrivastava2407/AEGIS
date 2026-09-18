import React, { useState } from 'react';
import { X, Server } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export interface CreateSourceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, sourceType: string, config: Record<string, any>) => Promise<void>;
}

export const CreateSourceModal: React.FC<CreateSourceModalProps> = ({
  isOpen,
  onClose,
  onSave,
}) => {
  const [name, setName] = useState('');
  const [sourceType, setSourceType] = useState<'CSV' | 'JSON' | 'POSTGRESQL' | 'REST_API'>('CSV');
  const [filePath, setFilePath] = useState('');
  const [endpointUrl, setEndpointUrl] = useState('');
  const [host, setHost] = useState('localhost');
  const [dbName, setDbName] = useState('production_db');
  const [tableName] = useState('orders');
  const [saving, setSaving] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      let config: Record<string, any> = {};
      if (sourceType === 'CSV' || sourceType === 'JSON') {
        config = { file_path: filePath || `data/fixtures/valid_orders.csv` };
      } else if (sourceType === 'POSTGRESQL') {
        config = { host, port: 5432, database: dbName, user: 'aegis_app', table_name: tableName };
      } else if (sourceType === 'REST_API') {
        config = { endpoint_url: endpointUrl || 'https://api.github.com/events', method: 'GET' };
      }

      await onSave(name, sourceType, config);
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="w-full max-w-lg bg-[#111116] border border-[rgba(255,255,255,0.12)] rounded-dialogs shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-[rgba(255,255,255,0.08)]">
          <div className="flex items-center gap-2 font-bold text-sm text-gray-100">
            <Server size={16} className="text-[#7C6FF2]" />
            <span>Register Data Source</span>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-300">
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
          <div>
            <label className="block text-gray-400 font-semibold mb-1">Source Name</label>
            <Input
              required
              placeholder="e.g. Orders Transactions Feed"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-gray-400 font-semibold mb-1">Source Connector Type</label>
            <div className="grid grid-cols-4 gap-2">
              {(['CSV', 'JSON', 'POSTGRESQL', 'REST_API'] as const).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setSourceType(type)}
                  className={`p-2.5 rounded-controls border text-center font-medium transition-all ${
                    sourceType === type
                      ? 'border-[#7C6FF2] bg-[#7C6FF2]/10 text-[#7C6FF2]'
                      : 'border-[rgba(255,255,255,0.08)] bg-[#16161C] text-gray-400 hover:text-gray-200'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {(sourceType === 'CSV' || sourceType === 'JSON') && (
            <div>
              <label className="block text-gray-400 font-semibold mb-1">File Path or Local Fixture</label>
              <Input
                placeholder="e.g. data/fixtures/valid_orders.csv"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
              />
            </div>
          )}

          {sourceType === 'POSTGRESQL' && (
            <div className="space-y-3">
              <div>
                <label className="block text-gray-400 font-semibold mb-1">Host &amp; Database</label>
                <Input placeholder="localhost" value={host} onChange={(e) => setHost(e.target.value)} />
              </div>
              <div>
                <label className="block text-gray-400 font-semibold mb-1">Database Name &amp; Table</label>
                <Input placeholder="production_db" value={dbName} onChange={(e) => setDbName(e.target.value)} />
              </div>
            </div>
          )}

          {sourceType === 'REST_API' && (
            <div>
              <label className="block text-gray-400 font-semibold mb-1">Endpoint URL</label>
              <Input
                placeholder="https://api.enterprise.com/v1/orders"
                value={endpointUrl}
                onChange={(e) => setEndpointUrl(e.target.value)}
              />
            </div>
          )}

          <div className="pt-4 border-t border-[rgba(255,255,255,0.08)] flex justify-end gap-2">
            <Button variant="ghost" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Register Source'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

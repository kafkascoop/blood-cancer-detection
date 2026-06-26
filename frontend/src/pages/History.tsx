import { useState, useEffect, useRef } from 'react';
import { Card } from 'primereact/card';
import { DataView } from 'primereact/dataview';
import { Tag } from 'primereact/tag';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { IconField } from 'primereact/iconfield';
import { InputIcon } from 'primereact/inputicon';
import { Toast } from 'primereact/toast';
import ResultCard from '../components/ResultCard';
import { getDetectionHistory } from '../utils/api';
import type { DetectionResult } from '../types';

const mockHistory: DetectionResult[] = Array.from({ length: 20 }, (_, i) => {
  const predictions: ('Normal' | 'Benign' | 'Malignant')[] = ['Normal', 'Benign', 'Malignant'];
  const names = ['John Doe', 'Jane Smith', 'Robert Brown', 'Emily Davis', 'Michael Wilson', 'Sarah Johnson', 'David Lee', 'Lisa Anderson'];
  return {
    id: `hist-${i}`,
    timestamp: new Date(Date.now() - i * 86400000 * (1 + Math.random())).toISOString(),
    type: i % 3 === 0 ? 'blood_test' : 'image',
    patientName: names[i % names.length],
    prediction: predictions[i % 3],
    confidence: 0.80 + Math.random() * 0.19,
    status: i === 0 ? 'pending' : 'completed',
  };
});

const predictionSeverity: Record<string, string> = { Normal: 'success', Benign: 'warn', Malignant: 'danger' };

export default function History() {
  const [history, setHistory] = useState<DetectionResult[]>(mockHistory);
  const [selectedResult, setSelectedResult] = useState<DetectionResult | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const toastRef = useRef<Toast>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getDetectionHistory();
        setHistory(data);
      } catch { /* mock data */ }
      finally { setLoading(false); }
    };
    fetchHistory();
  }, []);

  const filtered = history.filter((r) => r.patientName.toLowerCase().includes(searchTerm.toLowerCase()));

  const itemTemplate = (r: DetectionResult) => (
    <div
      className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200 cursor-pointer hover:border-blue-200 hover:shadow-md transition-all mb-2"
      onClick={() => setSelectedResult(r)}
    >
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shrink-0 ${
          r.prediction === 'Normal' ? 'bg-emerald-100 text-emerald-700' :
          r.prediction === 'Benign' ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'
        }`}>
          {r.patientName.charAt(0)}
        </div>
        <div className="flex flex-col gap-1">
          <span className="text-sm font-medium text-gray-800">{r.patientName}</span>
          <div className="flex items-center gap-2 flex-wrap">
            <Tag value={r.prediction} severity={predictionSeverity[r.prediction] as 'success' | 'warn' | 'danger'} rounded />
            <span className="text-xs text-gray-400">{(r.confidence * 100).toFixed(1)}% confidence</span>
            <span className="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">{r.type === 'image' ? 'Image' : 'Blood Test'}</span>
          </div>
        </div>
      </div>
      <div className="hidden sm:flex items-center gap-2 text-xs text-gray-400">
        <i className="pi pi-calendar" />
        <span className="text-gray-500">
          {new Date(r.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
        </span>
      </div>
    </div>
  );

  if (selectedResult) {
    return (
      <div className="mx-auto max-w-[1400px]">
        <Toast ref={toastRef} />
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">History</h1>
            <p className="text-sm text-gray-500 mt-1">Detailed view of detection record</p>
          </div>
        </div>
        <Button label="← Back to history" text className="mb-4" onClick={() => setSelectedResult(null)} />
        <ResultCard result={selectedResult} />
      </div>
    );
  }

  const header = (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
      <span className="text-xl font-semibold text-gray-800">Detection History</span>
      <IconField iconPosition="left">
        <InputIcon className="pi pi-search" />
        <InputText value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search by patient name..." className="pl-8" />
      </IconField>
    </div>
  );

  return (
    <div className="mx-auto max-w-[1400px]">
      <Toast ref={toastRef} />
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">History</h1>
          <p className="text-sm text-gray-500 mt-1">Complete record of all detection analyses</p>
        </div>
      </div>

      {loading ? (
        <Card className="shadow-sm">
          <div className="flex flex-col items-center py-12 text-center">
            <i className="pi pi-spin pi-spinner text-4xl text-blue-500 mb-4" />
            <h3 className="text-lg font-semibold text-gray-500">Loading history...</h3>
          </div>
        </Card>
      ) : (
        <Card className="shadow-sm">
          {header}
          <DataView value={filtered} itemTemplate={itemTemplate} layout="list" paginator rows={10} rowsPerPageOptions={[5, 10, 20]} />
          {filtered.length === 0 && (
            <div className="flex flex-col items-center py-12 text-center">
              <i className="pi pi-history text-4xl text-gray-300 mb-4" />
              <h3 className="text-lg font-semibold text-gray-500 mb-2">No history found</h3>
              <p className="text-sm text-gray-400">{searchTerm ? 'Try a different search term' : 'No detection records yet'}</p>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

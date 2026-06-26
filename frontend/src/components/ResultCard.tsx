import { Card } from 'primereact/card';
import { Tag } from 'primereact/tag';
import { ProgressBar } from 'primereact/progressbar';
import { ShieldCheck, AlertTriangle, XCircle, Clock, Microscope, Activity } from 'lucide-react';
import type { DetectionResult } from '../types';

interface ResultCardProps {
  result: DetectionResult;
  loading?: boolean;
}

const predictionSeverity = {
  Normal: 'success',
  Benign: 'warn',
  Malignant: 'danger',
} as const;

const predictionConfig = {
  Normal: {
    icon: ShieldCheck,
    color: 'emerald',
    label: 'Normal',
    description: 'No abnormal cells detected',
  },
  Benign: {
    icon: AlertTriangle,
    color: 'amber',
    label: 'Benign',
    description: 'Non-cancerous growth detected',
  },
  Malignant: {
    icon: XCircle,
    color: 'rose',
    label: 'Malignant',
    description: 'Cancerous cells detected — further investigation required',
  },
};

const statusLabels = { completed: 'Completed', pending: 'Pending', failed: 'Failed' };

export default function ResultCard({ result, loading }: ResultCardProps) {
  if (loading) {
    return (
      <Card className="border-blue-200">
        <div className="flex flex-col items-center py-8 text-center">
          <i className="pi pi-spin pi-spinner text-4xl text-blue-500 mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">Analyzing sample...</h3>
          <p className="text-sm text-gray-400">Running AI detection model</p>
        </div>
      </Card>
    );
  }

  const config = predictionConfig[result.prediction] || predictionConfig.Normal;
  const Icon = config.icon;
  const confidencePct = (result.confidence * 100).toFixed(1);

  const borderColor = {
    emerald: 'border-emerald-200',
    amber: 'border-amber-200',
    rose: 'border-rose-200',
  }[config.color];

  return (
    <Card className={`border-2 ${borderColor}`}>
      <div className="flex items-start gap-4 mb-4">
        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 ${
          config.color === 'emerald' ? 'bg-emerald-100 text-emerald-600' :
          config.color === 'amber' ? 'bg-amber-100 text-amber-600' :
          'bg-rose-100 text-rose-600'
        }`}>
          <Icon size={32} />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className={`text-xl font-bold ${
              config.color === 'emerald' ? 'text-emerald-700' :
              config.color === 'amber' ? 'text-amber-700' :
              'text-rose-700'
            }`}>
              {config.label}
            </h3>
            <Tag value={statusLabels[result.status]} severity={result.status === 'completed' ? 'success' : result.status === 'pending' ? 'warn' : 'danger'} rounded />
          </div>
          <p className="text-sm text-gray-500 mt-1">{config.description}</p>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Confidence</span>
          <span className="font-semibold">{confidencePct}%</span>
        </div>
        <ProgressBar value={parseFloat(confidencePct)} />
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="flex items-center gap-2 text-gray-600">
          <Activity size={14} />
          <span className="text-gray-400">Method:</span>
          <span className="font-medium text-gray-800 ml-auto">{result.type === 'image' ? 'Image Analysis' : 'Blood Test'}</span>
        </div>
        <div className="flex items-center gap-2 text-gray-600">
          <Microscope size={14} />
          <span className="text-gray-400">Patient:</span>
          <span className="font-medium text-gray-800 ml-auto">{result.patientName}</span>
        </div>
        <div className="flex items-center gap-2 text-gray-600 col-span-2">
          <Clock size={14} />
          <span className="text-gray-400">Date:</span>
          <span className="font-medium text-gray-800 ml-auto">
            {new Date(result.timestamp).toLocaleDateString('en-US', {
              month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit',
            })}
          </span>
        </div>
      </div>

      {result.confidence < 0.7 && (
        <div className="mt-4 px-4 py-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center gap-2 text-sm text-amber-700">
          <AlertTriangle size={16} />
          <span>Low confidence prediction — consider retesting</span>
        </div>
      )}
    </Card>
  );
}

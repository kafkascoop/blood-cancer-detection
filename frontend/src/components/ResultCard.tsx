import { Card } from 'primereact/card';
import { Tag } from 'primereact/tag';
import { ProgressBar } from 'primereact/progressbar';
import {
  ShieldCheck,
  AlertTriangle,
  XCircle,
  Clock,
  User,
  ScanLine,
} from 'lucide-react';
import type { DetectionResult } from '../types';

interface ResultCardProps {
  result: DetectionResult;
  loading?: boolean;
}

const predictionConfig = {
  Normal: {
    icon: ShieldCheck,
    color: 'emerald',
    label: 'Normal',
    description: 'No abnormal cells detected',
    gradient: 'from-emerald-500 to-emerald-600',
    lightBg: 'bg-emerald-50',
    border: 'border-emerald-200',
    ring: 'ring-emerald-500/20',
    text: 'text-emerald-700',
    dot: 'bg-emerald-500',
  },
  Benign: {
    icon: AlertTriangle,
    color: 'amber',
    label: 'Benign',
    description: 'Non-cancerous growth detected',
    gradient: 'from-amber-500 to-amber-600',
    lightBg: 'bg-amber-50',
    border: 'border-amber-200',
    ring: 'ring-amber-500/20',
    text: 'text-amber-700',
    dot: 'bg-amber-500',
  },
  Malignant: {
    icon: XCircle,
    color: 'rose',
    label: 'Malignant',
    description: 'Cancerous cells detected — further investigation required',
    gradient: 'from-rose-500 to-rose-600',
    lightBg: 'bg-rose-50',
    border: 'border-rose-200',
    ring: 'ring-rose-500/20',
    text: 'text-rose-700',
    dot: 'bg-rose-500',
  },
};

const statusLabels = {
  completed: 'Completed',
  pending: 'Pending',
  failed: 'Failed',
};

const statusSeverityMap = {
  completed: 'success' as const,
  pending: 'warn' as const,
  failed: 'danger' as const,
};

/** Circular confidence ring */
function ConfidenceRing({ value, color }: { value: number; color: string }) {
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  const strokeColor =
    color === 'emerald'
      ? '#10b981'
      : color === 'amber'
        ? '#f59e0b'
        : '#f43f5e';

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="96" height="96" className="-rotate-90">
        <circle
          cx="48"
          cy="48"
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="6"
        />
        <circle
          cx="48"
          cy="48"
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <span className={`absolute text-xl font-bold ${color === 'emerald' ? 'text-emerald-700' : color === 'amber' ? 'text-amber-700' : 'text-rose-700'}`}>
        {Math.round(value)}%
      </span>
    </div>
  );
}

/** Skeleton loader */
function ResultCardSkeleton() {
  return (
    <Card className="overflow-hidden border-gray-200 animate-pulse">
      {/* Gradient header skeleton */}
      <div className="h-36 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 rounded-t-lg -mx-0 -mt-0" />

      <div className="space-y-4 mt-6">
        {/* Two-line skeleton */}
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded-full w-3/4" />
          <div className="h-3 bg-gray-100 rounded-full w-1/2" />
        </div>

        {/* Confidence bar skeleton */}
        <div className="space-y-2">
          <div className="h-3 bg-gray-100 rounded-full w-1/3" />
          <div className="h-2 bg-gray-200 rounded-full w-full" />
        </div>

        {/* Info grid skeleton */}
        <div className="grid grid-cols-2 gap-3 pt-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gray-200 rounded" />
              <div className="h-3 bg-gray-100 rounded-full flex-1" />
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

export default function ResultCard({ result, loading }: ResultCardProps) {
  if (loading) return <ResultCardSkeleton />;

  const config = predictionConfig[result.prediction] || predictionConfig.Normal;
  const Icon = config.icon;
  const confidencePct = Number((result.confidence * 100).toFixed(1));

  return (
    <Card
      className={`
        overflow-hidden border-0 shadow-lg
        hover:shadow-xl transition-all duration-300
        ring-1 ${config.ring}
      `}
    >
      {/* ============================================================
          GRADIENT HEADER with icon, label, status
          ============================================================ */}
      <div
        className={`
          px-6 pt-5 pb-8
          bg-gradient-to-br ${config.gradient}
          relative overflow-hidden
        `}
      >
        {/* Decorative circles */}
        <div className="absolute -top-6 -right-6 w-28 h-28 rounded-full bg-white/10" />
        <div className="absolute -bottom-4 -right-2 w-20 h-20 rounded-full bg-white/5" />

        <div className="flex items-start justify-between relative z-10">
          <div className="flex items-center gap-4">
            {/* Icon */}
            <div className="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-inner">
              <Icon size={30} className="text-white" />
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white drop-shadow-sm">
                {config.label}
              </h2>
              <p className="text-sm text-white/80 mt-0.5">
                {config.description}
              </p>
            </div>
          </div>

          {/* Status badge */}
          <Tag
            value={statusLabels[result.status]}
            severity={statusSeverityMap[result.status]}
            rounded
            className="bg-white/20 text-white border-0 backdrop-blur-sm font-medium"
          />
        </div>
      </div>

      {/* ============================================================
          BODY
          ============================================================ */}
      <div className="px-6 pb-5 -mt-4">
        {/* Confidence ring card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Confidence Score
              </p>
              <p className="text-sm text-gray-500 mt-1">
                AI prediction certainty
              </p>
            </div>
            <ConfidenceRing value={confidencePct} color={config.color} />
          </div>

          {/* Confidence bar */}
          <div className="mt-4">
            <ProgressBar
              value={confidencePct}
              className="h-2 rounded-full bg-gray-100"
              pt={{
                value: {
                  style: {
                    background:
                      config.color === 'emerald'
                        ? 'linear-gradient(90deg, #34d399, #10b981)'
                        : config.color === 'amber'
                          ? 'linear-gradient(90deg, #fbbf24, #f59e0b)'
                          : 'linear-gradient(90deg, #fb7185, #f43f5e)',
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Metadata section */}
        <div className="space-y-3">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Details
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {/* Method */}
            <div className="flex items-center gap-3 px-3 py-2.5 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
                <ScanLine size={16} />
              </div>
              <div className="min-w-0">
                <p className="text-xs text-gray-400">Method</p>
                <p className="text-sm font-medium text-gray-800 truncate">
                  {result.type === 'image' ? 'Image Analysis' : 'Blood Test'}
                </p>
              </div>
            </div>

            {/* Patient */}
            <div className="flex items-center gap-3 px-3 py-2.5 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center shrink-0">
                <User size={16} />
              </div>
              <div className="min-w-0">
                <p className="text-xs text-gray-400">Patient</p>
                <p className="text-sm font-medium text-gray-800 truncate">
                  {result.patientName}
                </p>
              </div>
            </div>

            {/* Date — full width */}
            <div className="flex items-center gap-3 px-3 py-2.5 bg-gray-50 rounded-lg sm:col-span-2">
              <div className="w-8 h-8 rounded-lg bg-gray-200 text-gray-500 flex items-center justify-center shrink-0">
                <Clock size={16} />
              </div>
              <div className="min-w-0">
                <p className="text-xs text-gray-400">Date</p>
                <p className="text-sm font-medium text-gray-800">
                  {new Date(result.timestamp).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Low confidence warning */}
        {result.confidence < 0.7 && (
          <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-4 flex gap-3">
            <AlertTriangle className="text-amber-600 shrink-0 mt-0.5" size={20} />
            <div>
              <h4 className="font-semibold text-amber-800 text-sm">
                Low Confidence Prediction
              </h4>
              <p className="text-sm text-amber-700 mt-1 leading-relaxed">
                This result has a relatively low confidence score. Consider
                performing another test or consulting a healthcare professional
                for further evaluation.
              </p>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

export interface BloodTestData {
  wbc: number;
  rbc: number;
  hemoglobin: number;
  platelets: number;
  neutrophils: number;
  lymphocytes: number;
  monocytes: number;
  eosinophils: number;
  basophils: number;
  blastCells: number;
}

export interface ImageDetectionData {
  imageUrl: string;
  fileName: string;
  fileSize: number;
}

export interface DetectionResult {
  id: string;
  timestamp: string;
  type: 'image' | 'blood_test';
  patientName: string;
  prediction: 'Normal' | 'Leukemia' | 'Lymphoma' | 'Myeloma';
  confidence: number;
  status: 'completed' | 'pending' | 'failed';
  details?: BloodTestData | null;
  imageData?: ImageDetectionData | null;
  notes?: string;
}

export interface DashboardStats {
  totalTests: number;
  abnormalDetections: number;
  normalResults: number;
  pendingResults: number;
  monthlyTests: number[];
}

export type PredictionColor = 'emerald' | 'violet' | 'amber' | 'rose' | 'slate';

// ========== Activity Logs ==========

export interface ActivityLogEntry {
  id: string;
  user_id?: string | null;
  username?: string | null;
  method: string;
  endpoint: string;
  status_code: number;
  duration_ms?: number | null;
  detail?: string | null;
  created_at: string;
}

export interface ActivityLogStatsData {
  total_logs: number;
  method_counts: Record<string, number>;
  status_code_counts: Record<string, number>;
  endpoint_counts: Record<string, number>;
  monthly_logs: number[];
}

export interface ActivityLogFilters {
  method?: string;
  status_code?: number;
  endpoint?: string;
  date_from?: string;
  date_to?: string;
  user_only?: boolean;
  limit?: number;
  skip?: number;
}

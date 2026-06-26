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
  prediction: 'Normal' | 'Benign' | 'Malignant';
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

export type PredictionColor = 'emerald' | 'amber' | 'rose' | 'slate';

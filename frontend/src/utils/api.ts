import axios from 'axios';
import type { BloodTestData, DetectionResult } from '../types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
  withCredentials: true, // Important for cookie-based auth
});

// ========== Auth ==========

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

export const registerUser = async (data: RegisterData) => {
  const res = await api.post('/auth/register', data);
  return res.data;
};

export const loginUser = async (data: LoginData) => {
  const res = await api.post('/auth/login', data);
  return res.data;
};

export const logoutUser = async () => {
  const res = await api.post('/auth/logout');
  return res.data;
};

export const getMe = async () => {
  const res = await api.get('/auth/me');
  return res.data;
};

// ========== Predictions ==========

export const uploadImage = async (
  file: File,
  patientName: string
): Promise<DetectionResult> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_name', patientName);
  const { data } = await api.post('/predict/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return mapDetection(data);
};

export const predictBloodTest = async (
  testData: BloodTestData,
  patientName: string
): Promise<DetectionResult> => {
  const formData = new FormData();
  formData.append('patient_name', patientName);
  formData.append('blood_data', JSON.stringify(testData));
  const { data } = await api.post('/predict/blood-test', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return mapDetection(data);
};

// ========== Results ==========

export const getDetectionHistory = async (): Promise<DetectionResult[]> => {
  const { data } = await api.get('/results');
  return data.map(mapDetection);
};

export const getDetectionById = async (
  id: string
): Promise<DetectionResult> => {
  const { data } = await api.get(`/results/${id}`);
  return mapDetection(data);
};

export const getDashboardStats = async () => {
  const { data } = await api.get('/dashboard');
  return {
    stats: data.stats,
    recentResults: (data.recent_results || []).map(mapDetection),
  };
};

// ========== Settings ==========

export interface AppSettings {
  app_name: string;
  image_model_mode: 'auto' | 'cnn' | 'opencv';
}

export interface DlStatus {
  tensorflow_available: boolean;
  tensorflow_version: string | null;
  pytorch_available: boolean;
  pytorch_version: string | null;
  cnn_available: boolean;
}

export const getSettings = async (): Promise<AppSettings> => {
  const { data } = await api.get('/settings');
  return data;
};

export const updateSettings = async (
  settings: AppSettings
): Promise<AppSettings> => {
  const { data } = await api.put('/settings', settings);
  return data;
};

export const getDlStatus = async (): Promise<DlStatus> => {
  const { data } = await api.get('/settings/deep-learning-status');
  return data;
};

// ========== Mapping ==========

/** Convert snake_case backend response to camelCase frontend types */
function mapDetection(d: any): DetectionResult {
  return {
    id: d.id,
    timestamp: d.created_at || d.timestamp,
    type: d.type,
    patientName: d.patient_name || d.patientName,
    prediction: d.prediction,
    confidence: d.confidence,
    status: d.status || 'completed',
    details: d.blood_test_data || null,
    imageData: d.image_data || null,
    notes: d.notes || null,
  };
}

export default api;

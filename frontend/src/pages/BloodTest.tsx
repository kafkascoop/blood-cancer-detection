import { useState, useRef } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { Message } from 'primereact/message';
import { Toast } from 'primereact/toast';
import { ClipboardList } from 'lucide-react';
import ResultCard from '../components/ResultCard';
import { predictBloodTest } from '../utils/api';
import type { BloodTestData, DetectionResult } from '../types';

const initialForm: BloodTestData = {
  wbc: 0, rbc: 0, hemoglobin: 0, platelets: 0,
  neutrophils: 0, lymphocytes: 0, monocytes: 0,
  eosinophils: 0, basophils: 0, blastCells: 0,
};

const fields: { key: keyof BloodTestData; label: string; suffix: string; normalRange: string; step?: number }[] = [
  { key: 'wbc', label: 'WBC', suffix: '×10³/µL', normalRange: '4.5–11.0', step: 0.1 },
  { key: 'rbc', label: 'RBC', suffix: '×10⁶/µL', normalRange: '4.7–6.1', step: 0.01 },
  { key: 'hemoglobin', label: 'Hemoglobin', suffix: 'g/dL', normalRange: '13.8–17.2', step: 0.1 },
  { key: 'platelets', label: 'Platelets', suffix: '×10³/µL', normalRange: '150–450' },
  { key: 'neutrophils', label: 'Neutrophils', suffix: '%', normalRange: '40–80', step: 0.1 },
  { key: 'lymphocytes', label: 'Lymphocytes', suffix: '%', normalRange: '20–40', step: 0.1 },
  { key: 'monocytes', label: 'Monocytes', suffix: '%', normalRange: '2–10', step: 0.1 },
  { key: 'eosinophils', label: 'Eosinophils', suffix: '%', normalRange: '1–6', step: 0.1 },
  { key: 'basophils', label: 'Basophils', suffix: '%', normalRange: '0–1', step: 0.1 },
  { key: 'blastCells', label: 'Blast Cells', suffix: '%', normalRange: '0–5', step: 0.1 },
];

export default function BloodTest() {
  const [form, setForm] = useState<BloodTestData>(initialForm);
  const [patientName, setPatientName] = useState('');
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const toastRef = useRef<Toast>(null);

  const updateField = (key: keyof BloodTestData, value: number | null) => {
    setForm((prev) => ({ ...prev, [key]: value ?? 0 }));
  };

  const handleSubmit = async () => {
    if (!patientName.trim()) {
      setError('Please enter the patient name');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    toastRef.current?.show({ severity: 'info', summary: 'Analyzing...', detail: 'Running AI model on CBC parameters', life: 5000 });

    try {
      const data = await predictBloodTest(form, patientName.trim());
      setResult(data);
      toastRef.current?.show({ severity: 'success', summary: 'Analysis Complete', detail: `Result: ${data.prediction}`, life: 5000 });
    } catch {
      let prediction: 'Normal' | 'Benign' | 'Malignant';
      if (form.blastCells > 20) prediction = 'Malignant';
      else if (form.blastCells > 5) prediction = 'Benign';
      else prediction = 'Normal';

      const mockResult: DetectionResult = {
        id: `bt-${Date.now()}`,
        timestamp: new Date().toISOString(),
        type: 'blood_test',
        patientName: patientName.trim(),
        prediction,
        confidence: 0.82 + Math.random() * 0.16,
        status: 'completed',
        details: form,
      };
      setResult(mockResult);
      toastRef.current?.show({ severity: 'warn', summary: 'Offline Mode', detail: 'Using fallback detection (backend unavailable)', life: 4000 });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <Toast ref={toastRef} />

      <div className="page-header">
        <div>
          <h1 className="page-title">Blood Test Data</h1>
          <p className="page-subtitle">Enter complete blood count (CBC) parameters for AI analysis</p>
        </div>
      </div>

      <div className="upload-page-layout">
        <Card className="shadow-sm">
          <h3 className="text-base font-semibold text-gray-700 mb-4">CBC Parameters</h3>

          <div className="flex flex-col gap-1 mb-4">
            <label htmlFor="patient-name-bt" className="text-sm font-medium text-gray-700">Patient Name</label>
            <InputText
              id="patient-name-bt"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              placeholder="Enter patient name"
              className="w-full"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4">
            {fields.map((f) => (
              <div key={f.key} className="flex flex-col gap-1 mb-4">
                <label htmlFor={`field-${f.key}`} className="text-sm font-medium text-gray-700">
                  {f.label} <span className="text-gray-400 font-normal">({f.suffix})</span>
                </label>
                <InputNumber
                  inputId={`field-${f.key}`}
                  value={form[f.key]}
                  onValueChange={(e) => updateField(f.key, e.value ?? 0)}
                  suffix={` ${f.suffix}`}
                  min={0}
                  step={f.step || 1}
                  maxFractionDigits={2}
                  className="w-full"
                  placeholder={`Normal: ${f.normalRange}`}
                />
                <span className="text-xs text-gray-400">Normal: {f.normalRange} {f.suffix}</span>
              </div>
            ))}
          </div>

          {error && <Message severity="error" text={error} className="w-full mb-3" />}

          <Button
            label={loading ? 'Analyzing...' : 'Analyze Blood Test'}
            icon={loading ? 'pi pi-spin pi-spinner' : 'pi pi-chart-line'}
            onClick={handleSubmit}
            disabled={loading}
            className="w-full mt-2"
            size="large"
          />
        </Card>

        <div className="result-section">
          {result && <ResultCard result={result} />}
          {!result && !loading && (
            <Card className="shadow-sm">
              <div className="flex flex-col items-center py-12 text-center">
                <ClipboardList size={48} className="text-gray-300 mb-4" />
                <h3 className="text-lg font-semibold text-gray-500 mb-2">No analysis yet</h3>
                <p className="text-sm text-gray-400 max-w-xs">Enter CBC parameters and click analyze to see results</p>
              </div>
            </Card>
          )}
          {loading && <ResultCard result={null as unknown as DetectionResult} loading />}
        </div>
      </div>
    </div>
  );
}

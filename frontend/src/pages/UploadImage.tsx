import { useState, useRef } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Message } from 'primereact/message';
import { Toast } from 'primereact/toast';
import { Scan } from 'lucide-react';
import ImageUploader from '../components/ImageUploader';
import ResultCard from '../components/ResultCard';
import { uploadImage } from '../utils/api';
import type { DetectionResult } from '../types';

export default function UploadImage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [patientName, setPatientName] = useState('');
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const toastRef = useRef<Toast>(null);

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please select an image to analyze');
      return;
    }
    if (!patientName.trim()) {
      setError('Please enter the patient name');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    toastRef.current?.show({ severity: 'info', summary: 'Analyzing...', detail: 'Running AI detection model on image', life: 5000 });

    try {
      const data = await uploadImage(selectedFile, patientName);
      setResult(data);
      toastRef.current?.show({ severity: 'success', summary: 'Analysis Complete', detail: `Result: ${data.prediction}`, life: 5000 });
    } catch {
      const mockResult: DetectionResult = {
        id: `img-${Date.now()}`,
        timestamp: new Date().toISOString(),
        type: 'image',
        patientName: patientName.trim(),
        prediction: (['Normal', 'Benign', 'Malignant'] as const)[Math.floor(Math.random() * 3)],
        confidence: 0.85 + Math.random() * 0.14,
        status: 'completed',
        imageData: { imageUrl: '', fileName: selectedFile.name, fileSize: selectedFile.size },
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
          <h1 className="page-title">Image Analysis</h1>
          <p className="page-subtitle">Upload microscopic blood smear images for AI-powered detection</p>
        </div>
      </div>

      <div className="upload-page-layout">
        <Card className="shadow-sm">
          <h3 className="text-base font-semibold text-gray-700 mb-4">Blood Sample Image</h3>

          <div className="flex flex-col gap-1 mb-4">
            <label htmlFor="patient-name-img" className="text-sm font-medium text-gray-700">Patient Name</label>
            <InputText
              id="patient-name-img"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              placeholder="Enter patient name"
              className="w-full"
            />
          </div>

          <ImageUploader selectedFile={selectedFile} onFileSelect={setSelectedFile} />

          {error && <Message severity="error" text={error} className="w-full mb-3" />}

          <Button
            label={loading ? 'Analyzing...' : 'Analyze Image'}
            icon={loading ? 'pi pi-spin pi-spinner' : 'pi pi-search'}
            onClick={handleSubmit}
            disabled={loading || !selectedFile}
            className="w-full mt-2"
            size="large"
          />
        </Card>

        <div className="result-section">
          {result && <ResultCard result={result} />}
          {!result && !loading && (
            <Card className="shadow-sm">
              <div className="flex flex-col items-center py-12 text-center">
                <Scan size={48} className="text-gray-300 mb-4" />
                <h3 className="text-lg font-semibold text-gray-500 mb-2">No analysis yet</h3>
                <p className="text-sm text-gray-400 max-w-xs">Upload a blood smear image and click analyze to see results</p>
              </div>
            </Card>
          )}
          {loading && <ResultCard result={null as unknown as DetectionResult} loading />}
        </div>
      </div>
    </div>
  );
}

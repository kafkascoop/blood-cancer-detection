import { useState, useRef } from 'react';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { IconField } from 'primereact/iconfield';
import { InputIcon } from 'primereact/inputicon';
import { Toast } from 'primereact/toast';
import ResultCard from '../components/ResultCard';
import type { DetectionResult } from '../types';

const mockResults: DetectionResult[] = [
  { id: '1', timestamp: new Date().toISOString(), type: 'image', patientName: 'John Doe', prediction: 'Normal', confidence: 0.97, status: 'completed' },
  { id: '2', timestamp: new Date(Date.now() - 86400000).toISOString(), type: 'blood_test', patientName: 'Jane Smith', prediction: 'Benign', confidence: 0.84, status: 'completed' },
  { id: '3', timestamp: new Date(Date.now() - 172800000).toISOString(), type: 'image', patientName: 'Robert Brown', prediction: 'Malignant', confidence: 0.92, status: 'completed' },
  { id: '4', timestamp: new Date(Date.now() - 259200000).toISOString(), type: 'blood_test', patientName: 'Emily Davis', prediction: 'Normal', confidence: 0.95, status: 'completed' },
  { id: '5', timestamp: new Date(Date.now() - 345600000).toISOString(), type: 'image', patientName: 'Michael Wilson', prediction: 'Normal', confidence: 0.99, status: 'completed' },
  { id: '6', timestamp: new Date(Date.now() - 432000000).toISOString(), type: 'blood_test', patientName: 'Sarah Johnson', prediction: 'Malignant', confidence: 0.88, status: 'completed' },
];

const predictionSeverity: Record<string, string> = { Normal: 'success', Benign: 'warn', Malignant: 'danger' };

export default function Results() {
  const [results] = useState(mockResults);
  const [selectedResult, setSelectedResult] = useState<DetectionResult | null>(null);
  const [globalFilter, setGlobalFilter] = useState('');
  const toastRef = useRef<Toast>(null);

  const predictionBody = (row: DetectionResult) => (
    <Tag value={row.prediction} severity={predictionSeverity[row.prediction] as 'success' | 'warn' | 'danger'} rounded />
  );
  const typeBody = (row: DetectionResult) => (
    <Tag value={row.type === 'image' ? 'Image' : 'Blood Test'} severity={row.type === 'image' ? 'info' : 'warning'} rounded />
  );
  const confidenceBody = (row: DetectionResult) => (
    <span className="font-semibold text-gray-700">{(row.confidence * 100).toFixed(1)}%</span>
  );
  const dateBody = (row: DetectionResult) => (
    <span className="text-gray-500">{new Date(row.timestamp).toLocaleDateString()}</span>
  );
  const statusBody = (row: DetectionResult) => (
    <Tag
      value={row.status.charAt(0).toUpperCase() + row.status.slice(1)}
      severity={row.status === 'completed' ? 'success' : row.status === 'pending' ? 'warn' : 'danger'}
      rounded
    />
  );
  const actionBody = (row: DetectionResult) => (
    <Button
      icon="pi pi-eye"
      rounded
      text
      severity="info"
      tooltip="View Details"
      tooltipOptions={{ position: 'left' }}
      onClick={() => { setSelectedResult(row); toastRef.current?.show({ severity: 'info', summary: 'Viewing Details', detail: row.patientName, life: 2000 }); }}
    />
  );

  const header = (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
      <span className="text-xl font-semibold text-gray-800">Detection Results</span>
      <IconField iconPosition="left">
        <InputIcon className="pi pi-search" />
        <InputText value={globalFilter} onChange={(e) => setGlobalFilter(e.target.value)} placeholder="Search by patient name..." className="pl-8" />
      </IconField>
    </div>
  );

  if (selectedResult) {
    return (
      <div className="page">
        <Toast ref={toastRef} />
        <div className="page-header">
          <div>
            <h1 className="page-title">Results</h1>
            <p className="page-subtitle">Detailed view of detection result</p>
          </div>
        </div>
        <Button label="← Back to results" text className="mb-4" onClick={() => setSelectedResult(null)} />
        <ResultCard result={selectedResult} />
        {selectedResult.details && 'wbc' in selectedResult.details && (
          <Card className="shadow-sm mt-6">
            <h3 className="text-base font-semibold text-gray-700 mb-4">Blood Test Details</h3>
            <DataTable value={[selectedResult.details]} size="small">
              {Object.entries(selectedResult.details).map(([key]) => (
                <Column
                  key={key} field={key}
                  header={key.replace(/([A-Z])/g, ' $1').replace(/^./, (s) => s.toUpperCase())}
                  body={(row: Record<string, number>) => <span className="font-mono font-medium">{row[key]?.toFixed(2)}</span>}
                />
              ))}
            </DataTable>
          </Card>
        )}
      </div>
    );
  }

  return (
    <div className="page">
      <Toast ref={toastRef} />
      <div className="page-header">
        <div>
          <h1 className="page-title">Results</h1>
          <p className="page-subtitle">View and analyze detection results</p>
        </div>
      </div>

      <Card className="shadow-sm">
        <DataTable
          value={results} paginator rows={10} rowsPerPageOptions={[5, 10, 25]}
          header={header} globalFilter={globalFilter} globalFilterFields={['patientName']}
          stripedRows size="small" sortMode="multiple" className="text-sm"
        >
          <Column field="patientName" header="Patient" sortable />
          <Column header="Type" body={typeBody} sortable sortField="type" />
          <Column header="Prediction" body={predictionBody} sortable sortField="prediction" />
          <Column header="Confidence" body={confidenceBody} sortable sortField="confidence" />
          <Column header="Date" body={dateBody} sortable sortField="timestamp" />
          <Column header="Status" body={statusBody} sortable sortField="status" />
          <Column header="Actions" body={actionBody} style={{ width: '80px' }} />
        </DataTable>
      </Card>
    </div>
  );
}

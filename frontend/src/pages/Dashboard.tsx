import { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { Chart } from 'primereact/chart';
import {
  Microscope, Activity, AlertTriangle, Clock, BarChart3, Dna,
} from 'lucide-react';
import StatCard from '../components/StatCard';
import { getDashboardStats } from '../utils/api';
import type { DashboardStats, DetectionResult } from '../types';

const mockStats: DashboardStats = {
  totalTests: 147,
  abnormalDetections: 23,
  normalResults: 118,
  pendingResults: 6,
  monthlyTests: [12, 15, 18, 22, 19, 25, 28, 24, 30, 27, 32, 35],
};

const mockRecentResults: DetectionResult[] = [
  { id: '1', timestamp: new Date().toISOString(), type: 'image', patientName: 'John Doe', prediction: 'Normal', confidence: 0.97, status: 'completed' },
  { id: '2', timestamp: new Date(Date.now() - 86400000).toISOString(), type: 'blood_test', patientName: 'Jane Smith', prediction: 'Benign', confidence: 0.84, status: 'completed' },
  { id: '3', timestamp: new Date(Date.now() - 172800000).toISOString(), type: 'image', patientName: 'Robert Brown', prediction: 'Malignant', confidence: 0.92, status: 'completed' },
  { id: '4', timestamp: new Date(Date.now() - 259200000).toISOString(), type: 'blood_test', patientName: 'Emily Davis', prediction: 'Normal', confidence: 0.95, status: 'completed' },
  { id: '5', timestamp: new Date(Date.now() - 345600000).toISOString(), type: 'image', patientName: 'Michael Wilson', prediction: 'Normal', confidence: 0.99, status: 'completed' },
];

const predictionSeverity: Record<string, string> = {
  Normal: 'success',
  Benign: 'warn',
  Malignant: 'danger',
};

export default function Dashboard() {
  const [stats, setStats] = useState(mockStats);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getDashboardStats();
        setStats(data.stats);
      } catch {
        // Using mock data
      }
    };
    fetchStats();
  }, []);

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  const barChartData = {
    labels: months,
    datasets: [
      {
        label: 'Tests',
        data: stats.monthlyTests,
        backgroundColor: '#2563eb',
        borderRadius: 4,
      },
    ],
  };

  const pieChartData = {
    labels: ['Normal', 'Benign', 'Malignant'],
    datasets: [
      {
        data: [stats.normalResults, stats.abnormalDetections - 8, 8],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        hoverBackgroundColor: ['#059669', '#d97706', '#dc2626'],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 11 } },
      },
      y: {
        grid: { color: '#e2e8f0' },
        ticks: { font: { size: 11 }, stepSize: 10 },
        beginAtZero: true,
      },
    },
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: { font: { size: 12 }, padding: 16 },
      },
    },
  };

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

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Overview of all detection activities</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Live
        </div>
      </div>

      <div className="stats-grid">
        <StatCard title="Total Tests" value={stats.totalTests} icon={Microscope} color="blue" subtitle="All time" trend={{ value: 12, positive: true }} />
        <StatCard title="Normal Results" value={stats.normalResults} icon={Activity} color="emerald" subtitle={`${((stats.normalResults / (stats.totalTests || 1)) * 100).toFixed(1)}% of total`} />
        <StatCard title="Abnormal Detections" value={stats.abnormalDetections} icon={AlertTriangle} color="rose" subtitle="Requires attention" trend={{ value: 8, positive: false }} />
        <StatCard title="Pending Analysis" value={stats.pendingResults} icon={Clock} color="amber" subtitle="Awaiting results" />
      </div>

      <div className="charts-grid">
        <Card className="shadow-sm">
          <div className="flex items-center gap-2 mb-4 text-gray-700 font-semibold text-sm">
            <BarChart3 size={18} />
            <h3>Monthly Tests</h3>
          </div>
          <div className="h-72">
            <Chart type="bar" data={barChartData} options={chartOptions} />
          </div>
        </Card>

        <Card className="shadow-sm">
          <div className="flex items-center gap-2 mb-4 text-gray-700 font-semibold text-sm">
            <Dna size={18} />
            <h3>Detection Distribution</h3>
          </div>
          <div className="h-72 flex items-center justify-center">
            <Chart type="pie" data={pieChartData} options={pieOptions} />
          </div>
        </Card>
      </div>

      <Card className="shadow-sm">
        <div className="flex items-center gap-2 px-6 py-4 border-b border-gray-100 text-gray-700 font-semibold text-sm">
          <Activity size={18} />
          <h3>Recent Detections</h3>
        </div>
        <DataTable value={mockRecentResults} stripedRows size="small" className="text-sm">
          <Column field="patientName" header="Patient" sortable />
          <Column header="Type" body={typeBody} />
          <Column header="Prediction" body={predictionBody} sortable />
          <Column header="Confidence" body={confidenceBody} sortable />
          <Column header="Date" body={dateBody} sortable />
        </DataTable>
      </Card>
    </div>
  );
}

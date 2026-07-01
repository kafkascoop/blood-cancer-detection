import { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { Chart } from 'primereact/chart';
import { Button } from 'primereact/button';
import {
  Microscope, Activity, AlertTriangle, Clock, BarChart3, Dna,
  ArrowRight, RefreshCw,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatCard from '../components/StatCard';
import { getDashboardStats, getActivityLogs } from '../utils/api';
import type { DashboardStats, DetectionResult, ActivityLogEntry } from '../types';

const mockStats: DashboardStats = {
  totalTests: 147,
  abnormalDetections: 23,
  normalResults: 118,
  pendingResults: 6,
  monthlyTests: [12, 15, 18, 22, 19, 25, 28, 24, 30, 27, 32, 35],
};

const mockRecentResults: DetectionResult[] = [
  { id: '1', timestamp: new Date().toISOString(), type: 'image', patientName: 'John Doe', prediction: 'Normal', confidence: 0.97, status: 'completed' },
  { id: '2', timestamp: new Date(Date.now() - 86400000).toISOString(), type: 'blood_test', patientName: 'Jane Smith', prediction: 'Lymphoma', confidence: 0.84, status: 'completed' },
  { id: '3', timestamp: new Date(Date.now() - 172800000).toISOString(), type: 'image', patientName: 'Robert Brown', prediction: 'Leukemia', confidence: 0.92, status: 'completed' },
  { id: '4', timestamp: new Date(Date.now() - 259200000).toISOString(), type: 'blood_test', patientName: 'Emily Davis', prediction: 'Normal', confidence: 0.95, status: 'completed' },
  { id: '5', timestamp: new Date(Date.now() - 345600000).toISOString(), type: 'image', patientName: 'Michael Wilson', prediction: 'Normal', confidence: 0.99, status: 'completed' },
];

const predictionSeverity: Record<string, string> = {
  Normal: 'success',
  Leukemia: 'danger',
  Lymphoma: 'warn',
  Myeloma: 'warn',
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(mockStats);
  const [recentActivities, setRecentActivities] = useState<ActivityLogEntry[]>([]);
  const [activitiesLoading, setActivitiesLoading] = useState(true);

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

  useEffect(() => {
    const fetchActivities = async () => {
      setActivitiesLoading(true);
      try {
        const data = await getActivityLogs({ limit: 8, user_only: true });
        setRecentActivities(data);
      } catch {
        // Backend not available — show empty state
        setRecentActivities([]);
      } finally {
        setActivitiesLoading(false);
      }
    };
    fetchActivities();
    // Refresh every 30 seconds
    const interval = setInterval(fetchActivities, 30000);
    return () => clearInterval(interval);
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
    labels: ['Normal', 'Leukemia', 'Lymphoma', 'Myeloma'],
    datasets: [
      {
        data: [stats.normalResults, Math.round(stats.abnormalDetections * 0.5), Math.round(stats.abnormalDetections * 0.3), Math.round(stats.abnormalDetections * 0.2)],
        backgroundColor: ['#10b981', '#ef4444', '#8b5cf6', '#f59e0b'],
        hoverBackgroundColor: ['#059669', '#dc2626', '#7c3aed', '#d97706'],
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
    <div className="mx-auto max-w-[1400px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Overview of all detection activities</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Live
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard title="Total Tests" value={stats.totalTests} icon={Microscope} color="blue" subtitle="All time" trend={{ value: 12, positive: true }} />
        <StatCard title="Normal Results" value={stats.normalResults} icon={Activity} color="emerald" subtitle={`${((stats.normalResults / (stats.totalTests || 1)) * 100).toFixed(1)}% of total`} />
        <StatCard title="Abnormal Detections" value={stats.abnormalDetections} icon={AlertTriangle} color="rose" subtitle="Requires attention" trend={{ value: 8, positive: false }} />
        <StatCard title="Pending Analysis" value={stats.pendingResults} icon={Clock} color="amber" subtitle="Awaiting results" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
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

      {/* ========== RECENT ACTIVITY WIDGET ========== */}
      <Card className="shadow-sm mt-6">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2 text-gray-700 font-semibold text-sm">
            <RefreshCw size={16} />
            <h3>Recent Activity</h3>
          </div>
          <Button
            label="View All"
            icon={<ArrowRight size={14} />}
            text
            className="text-sm text-blue-600 hover:text-blue-700"
            onClick={() => navigate('/activity-logs')}
            pt={{ icon: { className: 'ml-1.5' } }}
          />
        </div>

        {activitiesLoading ? (
          <div className="flex items-center justify-center py-8">
            <i className="pi pi-spin pi-spinner text-2xl text-blue-400" />
          </div>
        ) : recentActivities.length === 0 ? (
          <div className="flex flex-col items-center py-8 text-center">
            <RefreshCw size={28} className="text-gray-300 mb-2" />
            <p className="text-sm text-gray-400">No recent activity</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {recentActivities.map((log) => {
              const statusSeverity: 'success' | 'warn' | 'danger' | 'info' =
                log.status_code < 300 ? 'success' :
                log.status_code < 400 ? 'info' :
                log.status_code < 500 ? 'warn' : 'danger';

              const methodColor =
                log.method === 'GET' ? 'bg-emerald-100 text-emerald-700' :
                log.method === 'POST' ? 'bg-blue-100 text-blue-700' :
                log.method === 'PUT' || log.method === 'PATCH' ? 'bg-amber-100 text-amber-700' :
                log.method === 'DELETE' ? 'bg-rose-100 text-rose-700' :
                'bg-gray-100 text-gray-600';

              return (
                <div key={log.id} className="flex items-center gap-3 px-6 py-2.5 hover:bg-gray-50/50 transition-colors">
                  {/* Method badge */}
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold w-14 justify-center shrink-0 ${methodColor}`}>
                    {log.method}
                  </span>

                  {/* Endpoint */}
                  <span className="font-mono text-xs text-gray-700 flex-1 truncate">
                    {log.endpoint}
                  </span>

                  {/* Status code */}
                  <Tag value={log.status_code} severity={statusSeverity} rounded className="text-[11px]" />

                  {/* Duration */}
                  <span className={`font-mono text-[11px] w-12 text-right shrink-0 ${
                    (log.duration_ms ?? 0) < 200 ? 'text-emerald-600' :
                    (log.duration_ms ?? 0) < 500 ? 'text-amber-600' : 'text-rose-600'
                  }`}>
                    {log.duration_ms ?? '-'}ms
                  </span>

                  {/* Timestamp */}
                  <span className="text-[11px] text-gray-400 w-28 text-right shrink-0 hidden sm:block">
                    {new Date(log.created_at).toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit',
                    })}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}

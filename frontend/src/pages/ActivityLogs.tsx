import { useState, useEffect, useRef } from 'react';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Toast } from 'primereact/toast';
import { IconField } from 'primereact/iconfield';
import { InputIcon } from 'primereact/inputicon';
import { Calendar } from 'primereact/calendar';
import { Toolbar } from 'primereact/toolbar';
import { Activity, Filter, RefreshCw } from 'lucide-react';
import { getActivityLogs, getActivityStats } from '../utils/api';
import type { ActivityLogEntry, ActivityLogStatsData } from '../types';

const methodOptions = [
  { label: 'All Methods', value: null },
  { label: 'GET', value: 'GET' },
  { label: 'POST', value: 'POST' },
  { label: 'PUT', value: 'PUT' },
  { label: 'PATCH', value: 'PATCH' },
  { label: 'DELETE', value: 'DELETE' },
];

const statusOptions = [
  { label: 'All Status', value: null },
  { label: '2xx Success', value: 200 },
  { label: '4xx Client Error', value: 400 },
  { label: '5xx Server Error', value: 500 },
];

const methodSeverity: Record<string, 'success' | 'info' | 'warn' | 'danger' | 'contrast'> = {
  GET: 'success',
  POST: 'info',
  PUT: 'warn',
  PATCH: 'warn',
  DELETE: 'danger',
};

function getMethodSeverity(method: string) {
  return methodSeverity[method] || 'contrast';
}

export default function ActivityLogs() {
  const [logs, setLogs] = useState<ActivityLogEntry[]>([]);
  const [stats, setStats] = useState<ActivityLogStatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [totalRecords, setTotalRecords] = useState(0);
  const [first, setFirst] = useState(0);
  const [rows, setRows] = useState(50);

  // Filters
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<number | null>(null);
  const [searchEndpoint, setSearchEndpoint] = useState('');
  const [dateRange, setDateRange] = useState<Date[] | null>(null);

  const toastRef = useRef<Toast>(null);

  const fetchLogs = async (skip = 0) => {
    setLoading(true);
    try {
      const params: Record<string, any> = {
        limit: rows,
        skip,
        user_only: true,
      };
      if (selectedMethod) params.method = selectedMethod;
      if (selectedStatus) params.status_code = selectedStatus;
      if (searchEndpoint.trim()) params.endpoint = searchEndpoint.trim();
      if (dateRange?.[0]) params.date_from = dateRange[0].toISOString();
      if (dateRange?.[1]) params.date_to = dateRange[1].toISOString();

      const data = await getActivityLogs(params);
      setLogs(data);
      setTotalRecords(data.length < rows ? skip + data.length : skip + rows + 1);
    } catch {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load activity logs',
        life: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await getActivityStats();
      setStats(data);
    } catch {
      // Stats are non-critical
    }
  };

  useEffect(() => {
    fetchLogs(0);
    fetchStats();
  }, []);

  const onPage = (event: any) => {
    setFirst(event.first);
    setRows(event.rows);
    fetchLogs(event.first);
  };

  const applyFilters = () => {
    setFirst(0);
    fetchLogs(0);
  };

  const clearFilters = () => {
    setSelectedMethod(null);
    setSelectedStatus(null);
    setSearchEndpoint('');
    setDateRange(null);
    setFirst(0);
    fetchLogs(0);
  };

  // Template functions for columns
  const methodBody = (row: ActivityLogEntry) => (
    <Tag value={row.method} severity={getMethodSeverity(row.method)} rounded />
  );

  const statusBody = (row: ActivityLogEntry) => {
    const code = row.status_code;
    const severity: 'success' | 'warn' | 'danger' | 'info' =
      code < 300 ? 'success' : code < 400 ? 'info' : code < 500 ? 'warn' : 'danger';
    return <Tag value={code} severity={severity} rounded />;
  };

  const endpointBody = (row: ActivityLogEntry) => (
    <span className="font-mono text-sm text-gray-700">{row.endpoint}</span>
  );

  const durationBody = (row: ActivityLogEntry) => {
    const ms = row.duration_ms ?? 0;
    const color = ms < 200 ? 'text-emerald-600' : ms < 500 ? 'text-amber-600' : 'text-rose-600';
    return <span className={`font-mono text-sm ${color}`}>{ms}ms</span>;
  };

  const userBody = (row: ActivityLogEntry) => (
    <span className="text-sm text-gray-600">{row.username || '-'}</span>
  );

  const dateBody = (row: ActivityLogEntry) => (
    <span className="text-sm text-gray-500">
      {new Date(row.created_at).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })}
    </span>
  );

  const detailBody = (row: ActivityLogEntry) => {
    if (!row.detail) return <span className="text-gray-400">—</span>;
    return (
      <span className="text-xs text-amber-700 max-w-[200px] truncate block" title={row.detail}>
        {row.detail}
      </span>
    );
  };

  const header = (
    <div className="flex flex-col gap-4">
      {/* Top row: title + refresh */}
      <div className="flex items-center justify-between">
        <span className="text-xl font-semibold text-gray-800">Activity Logs</span>
        <div className="flex items-center gap-2">
          {(selectedMethod || selectedStatus || searchEndpoint || dateRange) && (
            <Button
              label="Clear Filters"
              icon="pi pi-filter-slash"
              text
              severity="secondary"
              onClick={clearFilters}
              className="text-sm"
            />
          )}
          <Button
            label="Refresh"
            icon={<RefreshCw size={16} />}
            text
            onClick={() => fetchLogs(first)}
            loading={loading}
            className="text-sm"
          />
        </div>
      </div>

      {/* Filter row */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5">
          <Filter size={15} className="text-gray-400" />
          <span className="text-xs font-medium text-gray-500 uppercase">Filters</span>
        </div>

        <Dropdown
          value={selectedMethod}
          options={methodOptions}
          onChange={(e) => setSelectedMethod(e.value)}
          placeholder="Method"
          className="w-32"
          showClear={selectedMethod !== null}
        />

        <Dropdown
          value={selectedStatus}
          options={statusOptions}
          onChange={(e) => setSelectedStatus(e.value)}
          placeholder="Status"
          className="w-36"
          showClear={selectedStatus !== null}
        />

        <IconField iconPosition="left">
          <InputIcon className="pi pi-search" />
          <InputText
            value={searchEndpoint}
            onChange={(e) => setSearchEndpoint(e.target.value)}
            placeholder="Search endpoint..."
            className="w-48 text-sm"
          />
        </IconField>

        <Calendar
          value={dateRange}
          onChange={(e) => setDateRange(e.value as Date[])}
          selectionMode="range"
          placeholder="Date range"
          dateFormat="mm/dd/yy"
          readOnlyInput
          className="w-52"
          showButtonBar
        />

        <Button
          label="Apply"
          icon="pi pi-check"
          onClick={applyFilters}
          className="text-sm"
        />
      </div>

      {/* Stats chips */}
      {stats && (
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-gray-500">Total: <strong className="text-gray-700">{stats.total_logs}</strong></span>
          {Object.entries(stats.method_counts).map(([method, count]) => (
            <Tag
              key={method}
              value={`${method}: ${count}`}
              severity={getMethodSeverity(method)}
              rounded
              className="text-[11px]"
            />
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="mx-auto">
      <Toast ref={toastRef} position="top-right" />

      <div className="flex items-center gap-2 mb-6">
        <div className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center">
          <Activity size={22} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Activity Logs</h1>
          <p className="text-sm text-gray-500 mt-1">
            Track all API activity across the system
          </p>
        </div>
      </div>

      <Card className="shadow-sm border border-gray-200">
        <DataTable
          value={logs}
          loading={loading}
          header={header}
          paginator
          first={first}
          rows={rows}
          onPage={onPage}
          rowsPerPageOptions={[25, 50, 100]}
          stripedRows
          size="small"
          sortMode="multiple"
          className="text-sm"
          emptyMessage="No activity logs found"
        >
          <Column header="Method" body={methodBody} sortable sortField="method" style={{ width: '100px' }} />
          <Column header="Status" body={statusBody} sortable sortField="status_code" style={{ width: '90px' }} />
          <Column header="Endpoint" body={endpointBody} sortable sortField="endpoint" />
          <Column header="Duration" body={durationBody} sortable sortField="duration_ms" style={{ width: '100px' }} />
          <Column header="User" body={userBody} sortable sortField="username" style={{ width: '120px' }} />
          <Column header="Date" body={dateBody} sortable sortField="created_at" style={{ width: '180px' }} />
          <Column header="Detail" body={detailBody} style={{ width: '150px' }} />
        </DataTable>
      </Card>
    </div>
  );
}

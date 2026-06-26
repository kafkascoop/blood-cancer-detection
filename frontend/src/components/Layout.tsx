import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Menubar } from 'primereact/menubar';
import { PanelMenu } from 'primereact/panelmenu';
import { Button } from 'primereact/button';
import type { MenuItem } from 'primereact/menuitem';
import { Microscope, Menu, X } from 'lucide-react';

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  const navItems: MenuItem[] = [
    {
      label: 'Dashboard',
      icon: 'pi pi-home',
      command: () => navigate('/'),
      className: location.pathname === '/' ? 'sidebar-link--active' : '',
    },
    {
      label: 'Upload Image',
      icon: 'pi pi-upload',
      command: () => navigate('/upload-image'),
      className: location.pathname === '/upload-image' ? 'sidebar-link--active' : '',
    },
    {
      label: 'Blood Test Data',
      icon: 'pi pi-pencil',
      command: () => navigate('/blood-test'),
      className: location.pathname === '/blood-test' ? 'sidebar-link--active' : '',
    },
    {
      label: 'Results',
      icon: 'pi pi-chart-bar',
      command: () => navigate('/results'),
      className: location.pathname === '/results' ? 'sidebar-link--active' : '',
    },
    {
      label: 'History',
      icon: 'pi pi-history',
      command: () => navigate('/history'),
      className: location.pathname === '/history' ? 'sidebar-link--active' : '',
    },
  ];

  const start = (
    <div className="flex items-center gap-3">
      <Microscope className="text-blue-600" size={28} />
      <div className="flex flex-col">
        <span className="text-lg font-bold text-gray-800 leading-tight">HematoScan</span>
        <span className="text-xs text-gray-400 leading-tight">Blood Cancer Detection</span>
      </div>
    </div>
  );

  const end = (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium">
      <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
      <span>AI Ready</span>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Menubar start={start} end={end} className="rounded-none border-0 border-b border-gray-200 h-16 px-4" />

      <div className="flex h-[calc(100vh-64px)]">
        {/* Mobile sidebar toggle */}
        <button
          className="md:hidden fixed bottom-4 right-4 z-50 w-12 h-12 bg-blue-600 text-white rounded-full shadow-lg flex items-center justify-center"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div className="md:hidden fixed inset-0 bg-black/30 z-30" onClick={() => setSidebarOpen(false)} />
        )}

        {/* Sidebar */}
        <aside
          className={`
            w-60 bg-white border-r border-gray-200 flex flex-col shrink-0 transition-all duration-300 z-40
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
            md:translate-x-0 md:relative md:z-0
            ${sidebarOpen ? 'fixed inset-y-0 left-0 md:static' : 'hidden md:flex'}
          `}
        >
          <div className="p-3 flex-1">
            <PanelMenu model={navItems} className="border-0 w-full" />
          </div>
          <div className="p-4 border-t border-gray-100 text-xs text-gray-400 flex items-center gap-2">
            <i className="pi pi-file" />
            <span>v1.0.0</span>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

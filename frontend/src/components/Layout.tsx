import { useState, useRef } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Avatar } from 'primereact/avatar';
import { Menu } from 'primereact/menu';
import { Toast } from 'primereact/toast';
import type { MenuItem } from 'primereact/menuitem';
import {
  Microscope, LayoutDashboard, Upload, ClipboardList, BarChart3, History, Settings,
  Menu as MenuIcon, X, ChevronLeft, ChevronRight, FileText,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import type { RefObject } from 'react';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/upload-image', label: 'Upload Image', icon: Upload },
  { to: '/blood-test', label: 'Blood Test Data', icon: ClipboardList },
  { to: '/results', label: 'Results', icon: BarChart3 },
  { to: '/history', label: 'History', icon: History },
  { to: '/settings', label: 'Settings', icon: Settings },
] as const;

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const toastRef = useRef<Toast>(null);
  const menuRef = useRef<Menu>(null);

  const userMenuItems: MenuItem[] = [
    {
      label: user?.full_name || user?.username,
      items: [
        {
          label: 'Sign Out',
          icon: 'pi pi-sign-out',
          command: async () => {
            await logout();
            toastRef.current?.show({ severity: 'info', summary: 'Signed out', life: 2000 });
            navigate('/login');
          },
        },
      ],
    },
  ];

  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <Toast ref={toastRef} position="top-right" />

      {/* ========== TOP NAVBAR ========== */}
      <header className="sticky top-0 z-50 h-16 bg-white border-b border-gray-200 px-4 flex items-center justify-between">
        {/* Left: hamburger + brand */}
        <div className="flex items-center gap-3">
          <button
            className="md:hidden w-9 h-9 rounded-lg flex items-center justify-center text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open sidebar"
          >
            <MenuIcon size={20} />
          </button>
          <button
            className="hidden md:flex w-9 h-9 rounded-lg items-center justify-center text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center">
              <Microscope size={20} className="text-white" />
            </div>
            <div className="flex-col leading-tight hidden sm:flex">
              <span className="text-base font-bold text-gray-800">HematoScan</span>
              <span className="text-[11px] text-gray-400">Blood Cancer Detection</span>
            </div>
          </div>
        </div>

        {/* Right: status + user */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>AI Ready</span>
          </div>
          <Avatar
            label={user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
            shape="circle"
            className="cursor-pointer bg-blue-600 text-white font-bold hover:bg-blue-700 transition-colors"
            style={{ width: 34, height: 34 }}
            onClick={(e) => menuRef.current?.toggle(e)}
          />
          <Menu model={userMenuItems} popup ref={menuRef} />
        </div>
      </header>

      {/* ========== SIDEBAR + MAIN CONTENT ========== */}
      <div className="flex h-[calc(100vh-64px)] relative">
        {/* Mobile backdrop */}
        {sidebarOpen && (
          <div
            className="md:hidden fixed inset-0 bg-black/40 z-30 animate-[fadeIn_0.2s_ease-out]"
            onClick={closeSidebar}
          />
        )}

        {/* Sidebar */}
        <aside
          className={`
            bg-white border-r border-gray-200 flex flex-col shrink-0 z-40
            transition-all duration-300 ease-in-out
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
            ${sidebarCollapsed ? 'w-16' : 'w-60'}
            fixed inset-y-0 left-0 md:relative md:inset-y-auto md:translate-x-0
            ${sidebarOpen ? '' : 'md:translate-x-0'}
          `}
        >
          {/* Mobile close button */}
          <div className={`flex items-center h-16 border-b border-gray-100 px-3 ${sidebarCollapsed ? 'justify-center' : 'justify-between'}`}>
            {!sidebarCollapsed && (
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Navigation</span>
            )}
            <button
              className="md:hidden w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
              onClick={closeSidebar}
              aria-label="Close sidebar"
            >
              <X size={18} />
            </button>
          </div>

          {/* Nav links */}
          <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const isActive = location.pathname === item.to;
              const Icon = item.icon;
              return (
                <button
                  key={item.to}
                  onClick={() => {
                    navigate(item.to);
                    closeSidebar();
                  }}
                  className={`
                    w-full flex items-center gap-3 rounded-xl transition-all duration-200
                    ${sidebarCollapsed ? 'justify-center h-11 w-11 mx-auto' : 'px-3 py-2.5'}
                    ${isActive
                      ? 'bg-blue-50 text-blue-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                    }
                  `}
                  title={sidebarCollapsed ? item.label : undefined}
                >
                  <Icon size={20} className="shrink-0" />
                  {!sidebarCollapsed && (
                    <span className="text-sm truncate">{item.label}</span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Footer */}
          <div className={`p-3 border-t border-gray-100 text-xs text-gray-400 flex items-center gap-2 ${sidebarCollapsed ? 'justify-center' : ''}`}>
            <FileText size={sidebarCollapsed ? 16 : 14} className="shrink-0" />
            {!sidebarCollapsed && <span>v1.0.0</span>}
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet context={{ toastRef } satisfies { toastRef: RefObject<Toast | null> }} />
        </main>
      </div>
    </div>
  );
}

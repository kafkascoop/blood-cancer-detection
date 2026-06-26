import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Upload,
  FileText,
  ClipboardList,
  Activity,
  History,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { to: '/upload-image', icon: Upload, label: 'Upload Image' },
  { to: '/blood-test', icon: ClipboardList, label: 'Blood Test Data' },
  { to: '/results', icon: Activity, label: 'Results' },
  { to: '/history', icon: History, label: 'History' },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {open && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${open ? 'sidebar--open' : ''}`}>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'sidebar-link--active' : ''}`
              }
              onClick={onClose}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <FileText size={16} />
          <span>v1.0.0</span>
        </div>
      </aside>
    </>
  );
}

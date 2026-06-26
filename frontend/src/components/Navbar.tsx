import { Menu, X, Microscope } from 'lucide-react';

interface NavbarProps {
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export default function Navbar({ sidebarOpen, onToggleSidebar }: NavbarProps) {
  return (
    <header className="navbar">
      <button
        className="sidebar-toggle"
        onClick={onToggleSidebar}
        aria-label={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
      >
        {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
      </button>

      <div className="navbar-brand">
        <Microscope size={28} className="navbar-icon" />
        <div className="navbar-title">
          <span className="navbar-title-main">HematoScan</span>
          <span className="navbar-title-sub">Blood Cancer Detection</span>
        </div>
      </div>

      <div className="navbar-right">
        <div className="navbar-status">
          <span className="status-dot" />
          <span className="status-text">AI Ready</span>
        </div>
      </div>
    </header>
  );
}

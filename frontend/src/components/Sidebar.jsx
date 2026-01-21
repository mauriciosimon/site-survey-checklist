import { useState, Children } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Target,
  DollarSign,
  CheckSquare,
  Building2,
  Users,
  FolderKanban,
  ClipboardList,
  Plus,
  ChevronRight,
  ChevronDown,
  Menu,
  TrendingUp,
  UserCircle,
  Briefcase,
  FileText
} from 'lucide-react';

// Folder component with expand/collapse
function Folder({ title, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const location = useLocation();

  // Check if any child route is active
  const childArray = Children.toArray(children);
  const hasActiveChild = childArray.some(child =>
    child.props?.to && (
      location.pathname === child.props.to ||
      location.pathname.startsWith(child.props.to + '/')
    )
  );

  return (
    <div className="sidebar-folder">
      <button
        className={`folder-header ${hasActiveChild ? 'has-active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="folder-title">{title}</span>
        <span className="folder-arrow">
          {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </span>
      </button>
      {isOpen && (
        <div className="folder-content">
          {children}
        </div>
      )}
    </div>
  );
}

// Navigation item component
function NavItem({ to, icon: Icon, label, badge }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
    >
      <span className="nav-icon">
        <Icon size={18} strokeWidth={1.75} />
      </span>
      <span className="nav-label">{label}</span>
      {badge && <span className="nav-badge">{badge}</span>}
    </NavLink>
  );
}

export default function Sidebar({ collapsed = false, onToggle }) {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Workspace Header */}
      <div className="sidebar-header">
        <div className="workspace-icon">S</div>
        <span className="workspace-name">Satoris</span>
        <button className="sidebar-toggle" onClick={onToggle}>
          <Menu size={18} />
        </button>
      </div>

      <div className="sidebar-content">
        {/* Dashboard - Top level */}
        <NavItem to="/" icon={LayoutDashboard} label="Dashboard" />

        {/* Sales Folder */}
        <Folder title="SALES" defaultOpen={true}>
          <NavItem to="/leads" icon={Target} label="Leads" />
          <NavItem to="/deals" icon={DollarSign} label="Deals" />
          <NavItem to="/tasks" icon={CheckSquare} label="Tasks" />
        </Folder>

        {/* Clients Folder */}
        <Folder title="CLIENTS" defaultOpen={true}>
          <NavItem to="/accounts" icon={Building2} label="Accounts" />
          <NavItem to="/contacts" icon={Users} label="Contacts" />
        </Folder>

        {/* Projects Folder */}
        <Folder title="PROJECTS" defaultOpen={false}>
          <NavItem to="/projects" icon={FolderKanban} label="Projects Overview" />
        </Folder>

        {/* Site Checklists Folder */}
        <Folder title="SITE SURVEYS" defaultOpen={true}>
          <NavItem to="/checklists" icon={ClipboardList} label="Surveys" />
          <NavItem to="/new" icon={Plus} label="New Survey" />
        </Folder>
      </div>

      {/* Sidebar footer */}
      <div className="sidebar-footer">
        <div className="sidebar-version">v2.0</div>
      </div>
    </aside>
  );
}

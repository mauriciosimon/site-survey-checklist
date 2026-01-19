import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';

// Folder component with expand/collapse
function Folder({ title, icon, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const location = useLocation();

  // Check if any child route is active
  const hasActiveChild = children?.some(child =>
    location.pathname === child.props.to ||
    location.pathname.startsWith(child.props.to + '/')
  );

  return (
    <div className="sidebar-folder">
      <button
        className={`folder-header ${hasActiveChild ? 'has-active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="folder-icon">{isOpen ? '📂' : '📁'}</span>
        <span className="folder-title">{title}</span>
        <span className={`folder-arrow ${isOpen ? 'open' : ''}`}>›</span>
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
function NavItem({ to, icon, label, badge }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
    >
      <span className="nav-icon">{icon}</span>
      <span className="nav-label">{label}</span>
      {badge && <span className="nav-badge">{badge}</span>}
    </NavLink>
  );
}

export default function Sidebar({ collapsed = false }) {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-content">
        {/* Dashboard - Top level */}
        <NavItem to="/" icon="🏠" label="Dashboard" />

        {/* Sales Folder */}
        <Folder title="Sales" icon="📊" defaultOpen={true}>
          <NavItem to="/leads" icon="🎯" label="Leads" />
          <NavItem to="/deals" icon="💰" label="Deals" />
          <NavItem to="/tasks" icon="✓" label="Tasks" />
        </Folder>

        {/* Clients Folder */}
        <Folder title="Clients" icon="👥" defaultOpen={true}>
          <NavItem to="/accounts" icon="🏢" label="Accounts" />
          <NavItem to="/contacts" icon="👤" label="Contacts" />
        </Folder>

        {/* Projects Folder */}
        <Folder title="Projects" icon="📋" defaultOpen={false}>
          <NavItem to="/projects" icon="📊" label="Projects Overview" />
        </Folder>

        {/* Site Checklists Folder - Our value add */}
        <Folder title="Site Checklists" icon="📝" defaultOpen={true}>
          <NavItem to="/checklists" icon="📋" label="Surveys" />
          <NavItem to="/new" icon="➕" label="New Survey" />
        </Folder>
      </div>

      {/* Sidebar footer */}
      <div className="sidebar-footer">
        <div className="sidebar-version">
          Site Checklist v2.0
        </div>
      </div>
    </aside>
  );
}

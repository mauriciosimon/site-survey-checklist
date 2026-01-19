// Placeholder component for pages under development
export default function PlaceholderPage({ title, icon, description }) {
  return (
    <div className="placeholder-page">
      <div className="placeholder-content">
        <span className="placeholder-icon">{icon}</span>
        <h2>{title}</h2>
        <p>{description || 'This page is coming soon.'}</p>
        <div className="placeholder-features">
          <h4>Planned Features:</h4>
          <ul>
            <li>Table view with sorting and filtering</li>
            <li>Kanban board view</li>
            <li>Quick search</li>
            <li>Create and edit records</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

// Specific placeholder pages
export function TasksPage() {
  return (
    <PlaceholderPage
      title="Tasks"
      icon="✓"
      description="Manage your sales tasks and activities."
    />
  );
}

export function ContactsPage() {
  return (
    <PlaceholderPage
      title="Contacts"
      icon="👤"
      description="Manage your business contacts and relationships."
    />
  );
}

export function ProjectsPage() {
  return (
    <PlaceholderPage
      title="Projects Overview"
      icon="📊"
      description="Track project status and progress."
    />
  );
}

export function DashboardPage() {
  return (
    <div className="dashboard-page">
      <h2>Welcome to Site Checklist</h2>
      <p className="dashboard-subtitle">Your construction site survey management system</p>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-icon">📋</div>
          <h3>Site Surveys</h3>
          <p>Create and manage site visit checklists</p>
          <a href="/checklists" className="card-link">View Surveys →</a>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">💰</div>
          <h3>Deals</h3>
          <p>Track opportunities through the pipeline</p>
          <a href="/deals" className="card-link">View Deals →</a>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">🎯</div>
          <h3>Leads</h3>
          <p>Manage incoming leads and prospects</p>
          <a href="/leads" className="card-link">View Leads →</a>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">👥</div>
          <h3>Contacts</h3>
          <p>Your network of business contacts</p>
          <a href="/contacts" className="card-link">View Contacts →</a>
        </div>
      </div>
    </div>
  );
}

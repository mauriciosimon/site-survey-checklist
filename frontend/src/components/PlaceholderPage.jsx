import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Target,
  DollarSign,
  Building2,
  Users,
  CheckSquare,
  ClipboardList,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  FolderKanban
} from 'lucide-react';
import { leadApi, dealApi, accountApi, contactApi, taskApi, checklistApi } from '../api';

// Placeholder component for pages under development
export default function PlaceholderPage({ title, icon: Icon, description }) {
  return (
    <div className="placeholder-page">
      <div className="placeholder-content">
        <span className="placeholder-icon">
          {Icon && <Icon size={48} strokeWidth={1.5} />}
        </span>
        <h2>{title}</h2>
        <p>{description || 'This page is coming soon.'}</p>
      </div>
    </div>
  );
}

// Specific placeholder pages
export function ProjectsPage() {
  return (
    <PlaceholderPage
      title="Projects Overview"
      icon={FolderKanban}
      description="Track project status and progress."
    />
  );
}

// Dashboard with real metrics
export function DashboardPage() {
  const [metrics, setMetrics] = useState({
    leads: { count: 0, loading: true },
    deals: { count: 0, value: 0, loading: true },
    accounts: { count: 0, loading: true },
    contacts: { count: 0, loading: true },
    tasks: { pending: 0, done: 0, loading: true },
    surveys: { count: 0, loading: true }
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // Fetch all data in parallel
        const [leads, deals, accounts, contacts, tasks, surveys] = await Promise.all([
          leadApi.getAll({ limit: 1000 }).catch(() => ({ data: [] })),
          dealApi.getAll({ limit: 1000 }).catch(() => ({ data: [] })),
          accountApi.getAll({ limit: 1000 }).catch(() => ({ data: [] })),
          contactApi.getAll({ limit: 1000 }).catch(() => ({ data: [] })),
          taskApi.getAll({ limit: 1000 }).catch(() => ({ data: [] })),
          checklistApi.getAll({ limit: 1000 }).catch(() => ({ data: [] }))
        ]);

        // Calculate deal pipeline value
        const pipelineValue = deals.data.reduce((sum, deal) => {
          const value = parseFloat(deal.value) || 0;
          return sum + value;
        }, 0);

        // Count tasks by status
        const pendingTasks = tasks.data.filter(t => t.status !== 'Done').length;
        const doneTasks = tasks.data.filter(t => t.status === 'Done').length;

        setMetrics({
          leads: { count: leads.data.length, loading: false },
          deals: { count: deals.data.length, value: pipelineValue, loading: false },
          accounts: { count: accounts.data.length, loading: false },
          contacts: { count: contacts.data.length, loading: false },
          tasks: { pending: pendingTasks, done: doneTasks, loading: false },
          surveys: { count: surveys.data.length, loading: false }
        });
      } catch (error) {
        console.error('Failed to fetch dashboard metrics:', error);
      }
    };

    fetchMetrics();
  }, []);

  const formatCurrency = (value) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Overview of your business metrics</p>
      </div>

      <div className="metrics-grid">
        {/* Leads Card */}
        <Link to="/leads" className="metric-card">
          <div className="metric-icon leads">
            <Target size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Active Leads</span>
            <span className="metric-value">
              {metrics.leads.loading ? '...' : metrics.leads.count}
            </span>
          </div>
          <ArrowRight size={16} className="metric-arrow" />
        </Link>

        {/* Deals Card */}
        <Link to="/deals" className="metric-card">
          <div className="metric-icon deals">
            <DollarSign size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Pipeline Value</span>
            <span className="metric-value">
              {metrics.deals.loading ? '...' : formatCurrency(metrics.deals.value)}
            </span>
            <span className="metric-subtext">
              {metrics.deals.count} deals
            </span>
          </div>
          <ArrowRight size={16} className="metric-arrow" />
        </Link>

        {/* Accounts Card */}
        <Link to="/accounts" className="metric-card">
          <div className="metric-icon accounts">
            <Building2 size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Accounts</span>
            <span className="metric-value">
              {metrics.accounts.loading ? '...' : metrics.accounts.count}
            </span>
          </div>
          <ArrowRight size={16} className="metric-arrow" />
        </Link>

        {/* Contacts Card */}
        <Link to="/contacts" className="metric-card">
          <div className="metric-icon contacts">
            <Users size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Contacts</span>
            <span className="metric-value">
              {metrics.contacts.loading ? '...' : metrics.contacts.count}
            </span>
          </div>
          <ArrowRight size={16} className="metric-arrow" />
        </Link>

        {/* Tasks Card */}
        <Link to="/tasks" className="metric-card">
          <div className="metric-icon tasks">
            <CheckSquare size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Open Tasks</span>
            <span className="metric-value">
              {metrics.tasks.loading ? '...' : metrics.tasks.pending}
            </span>
            <span className="metric-subtext">
              {metrics.tasks.done} completed
            </span>
          </div>
          <ArrowRight size={16} className="metric-arrow" />
        </Link>

        {/* Surveys Card */}
        <Link to="/checklists" className="metric-card">
          <div className="metric-icon surveys">
            <ClipboardList size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Site Surveys</span>
            <span className="metric-value">
              {metrics.surveys.loading ? '...' : metrics.surveys.count}
            </span>
          </div>
          <ArrowRight size={16} className="metric-arrow" />
        </Link>
      </div>
    </div>
  );
}

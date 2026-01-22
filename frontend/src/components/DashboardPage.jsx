import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Target,
  DollarSign,
  Building2,
  Users,
  CheckSquare,
  TrendingUp,
  ArrowRight,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  Calendar,
  Award,
  AlertCircle
} from 'lucide-react';
import { useWorkspace } from '../WorkspaceContext';
import { leadApi, dealApi, accountApi, contactApi, taskApi, opportunityApi } from '../api';

export default function DashboardPage() {
  const { currentWorkspace } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    pipeline: { total: 0, won: 0, wonCount: 0, lost: 0, lostCount: 0 },
    leads: { total: 0, new: 0, qualified: 0, working: 0 },
    deals: { total: 0, byStage: {} },
    tasks: { total: 0, pending: 0, done: 0 },
    accounts: { total: 0, byLabel: {} },
    contacts: { total: 0 },
    opportunities: { total: 0, byGrade: {}, totalValue: 0 }
  });

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const workspaceId = currentWorkspace?.id;

        const [dealsRes, leadsRes, accountsRes, contactsRes, tasksRes, oppsRes] = await Promise.all([
          dealApi.getAll({ workspace_id: workspaceId, limit: 2000 }).catch(() => ({ data: [] })),
          leadApi.getAll({ workspace_id: workspaceId, limit: 2000 }).catch(() => ({ data: [] })),
          accountApi.getAll({ workspace_id: workspaceId, limit: 2000 }).catch(() => ({ data: [] })),
          contactApi.getAll({ workspace_id: workspaceId, limit: 2000 }).catch(() => ({ data: [] })),
          taskApi.getAll({ workspace_id: workspaceId, limit: 2000 }).catch(() => ({ data: [] })),
          opportunityApi.getAll({ workspace_id: workspaceId, limit: 2000 }).catch(() => ({ data: [] }))
        ]);

        const deals = dealsRes.data || [];
        const leads = leadsRes.data || [];
        const accounts = accountsRes.data || [];
        const contacts = contactsRes.data || [];
        const tasks = tasksRes.data || [];
        const opportunities = oppsRes.data || [];

        // Calculate pipeline metrics
        const totalPipeline = deals.reduce((sum, d) => sum + (parseFloat(d.value) || 0), 0);
        const wonDeals = deals.filter(d => ['Closed won', 'Won', 'Completed'].includes(d.status));
        const wonValue = wonDeals.reduce((sum, d) => sum + (parseFloat(d.value) || 0), 0);
        const lostDeals = deals.filter(d => d.status === 'Lost');
        const lostValue = lostDeals.reduce((sum, d) => sum + (parseFloat(d.value) || 0), 0);

        // Deals by stage
        const dealsByStage = {};
        deals.forEach(d => {
          const stage = d.status || 'Unknown';
          if (!dealsByStage[stage]) {
            dealsByStage[stage] = { count: 0, value: 0 };
          }
          dealsByStage[stage].count++;
          dealsByStage[stage].value += parseFloat(d.value) || 0;
        });

        // Lead status counts
        const leadNew = leads.filter(l => l.status === 'New' || l.status === 'New Lead').length;
        const leadQualified = leads.filter(l => l.status === 'Qualified').length;
        const leadWorking = leads.filter(l => l.status === 'Working on it').length;

        // Tasks
        const tasksDone = tasks.filter(t => t.status === 'Done').length;
        const tasksPending = tasks.length - tasksDone;

        // Accounts by label
        const accountsByLabel = {};
        accounts.forEach(a => {
          const label = a.label || 'Other';
          accountsByLabel[label] = (accountsByLabel[label] || 0) + 1;
        });

        // Opportunities by grade
        const oppsByGrade = {};
        let oppsTotalValue = 0;
        opportunities.forEach(o => {
          const grade = o.grade || 'Ungraded';
          if (!oppsByGrade[grade]) {
            oppsByGrade[grade] = { count: 0, value: 0 };
          }
          oppsByGrade[grade].count++;
          oppsByGrade[grade].value += parseFloat(o.sale_price) || 0;
          oppsTotalValue += parseFloat(o.sale_price) || 0;
        });

        setMetrics({
          pipeline: {
            total: totalPipeline,
            won: wonValue,
            wonCount: wonDeals.length,
            lost: lostValue,
            lostCount: lostDeals.length
          },
          leads: {
            total: leads.length,
            new: leadNew,
            qualified: leadQualified,
            working: leadWorking
          },
          deals: {
            total: deals.length,
            byStage: dealsByStage
          },
          tasks: {
            total: tasks.length,
            pending: tasksPending,
            done: tasksDone
          },
          accounts: {
            total: accounts.length,
            byLabel: accountsByLabel
          },
          contacts: {
            total: contacts.length
          },
          opportunities: {
            total: opportunities.length,
            byGrade: oppsByGrade,
            totalValue: oppsTotalValue
          }
        });
      } catch (error) {
        console.error('Dashboard error:', error);
      }
      setLoading(false);
    };

    fetchData();
  }, [currentWorkspace]);

  const formatCurrency = (value) => {
    if (value >= 1000000) return `£${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `£${(value / 1000).toFixed(0)}K`;
    return `£${value.toFixed(0)}`;
  };

  // Calculate win rate
  const totalClosed = metrics.pipeline.wonCount + metrics.pipeline.lostCount;
  const winRate = totalClosed > 0 ? Math.round((metrics.pipeline.wonCount / totalClosed) * 100) : 0;

  // Get top account labels
  const topLabels = Object.entries(metrics.accounts.byLabel)
    .filter(([label]) => label !== 'Other' && label !== 'None')
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);
  const maxLabelCount = topLabels.length > 0 ? topLabels[0][1] : 1;

  // Deal stages for funnel
  const stageOrder = ['New deal', 'Prospect', 'Preparing proposal', 'Proposal sent', 'Closed won', 'Lost', 'Completed'];
  const stageColors = {
    'New deal': '#579bfc',
    'Prospect': '#0086c0',
    'Preparing proposal': '#fdab3d',
    'Proposal sent': '#9cd326',
    'Closed won': '#00c875',
    'Lost': '#df2f4a',
    'Completed': '#c4c4c4'
  };

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Executive Dashboard</h1>
          <p className="dashboard-subtitle">
            {currentWorkspace?.name || 'All Workspaces'} Overview
          </p>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="kpi-grid">
        <div className="kpi-card primary">
          <div className="kpi-icon">
            <DollarSign size={24} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Total Pipeline</span>
            <span className="kpi-value">{formatCurrency(metrics.pipeline.total)}</span>
            <span className="kpi-detail">{metrics.deals.total} deals</span>
          </div>
        </div>

        <div className="kpi-card success">
          <div className="kpi-icon">
            <Award size={24} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Won Revenue</span>
            <span className="kpi-value">{formatCurrency(metrics.pipeline.won)}</span>
            <span className="kpi-detail">{metrics.pipeline.wonCount} deals closed</span>
          </div>
        </div>

        <div className="kpi-card info">
          <div className="kpi-icon">
            <TrendingUp size={24} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Win Rate</span>
            <span className="kpi-value">{winRate}%</span>
            <span className="kpi-detail">{totalClosed} deals closed</span>
          </div>
        </div>

        <div className="kpi-card warning">
          <div className="kpi-icon">
            <Target size={24} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Active Leads</span>
            <span className="kpi-value">{metrics.leads.total}</span>
            <span className="kpi-detail">{metrics.leads.qualified} qualified</span>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="dashboard-charts">
        {/* Pipeline by Stage */}
        <div className="chart-card">
          <h3>Pipeline by Stage</h3>
          <div className="pipeline-chart">
            {stageOrder.map(stage => {
              const data = metrics.deals.byStage[stage];
              if (!data || data.count === 0) return null;
              const percentage = metrics.pipeline.total > 0
                ? (data.value / metrics.pipeline.total) * 100
                : 0;
              return (
                <div key={stage} className="pipeline-bar-row">
                  <span className="pipeline-label">{stage}</span>
                  <div className="pipeline-bar-container">
                    <div
                      className="pipeline-bar"
                      style={{
                        width: `${Math.max(percentage, 5)}%`,
                        backgroundColor: stageColors[stage] || '#c4c4c4'
                      }}
                    />
                  </div>
                  <span className="pipeline-value">{formatCurrency(data.value)}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Tasks Overview */}
        <div className="chart-card">
          <h3>Tasks Overview</h3>
          <div className="tasks-chart">
            <div className="tasks-donut">
              <svg viewBox="0 0 100 100">
                {metrics.tasks.total > 0 && (
                  <>
                    <circle
                      cx="50" cy="50" r="40"
                      fill="none"
                      stroke="#e6e9ef"
                      strokeWidth="12"
                    />
                    <circle
                      cx="50" cy="50" r="40"
                      fill="none"
                      stroke="#00c875"
                      strokeWidth="12"
                      strokeDasharray={`${(metrics.tasks.done / metrics.tasks.total) * 251.2} 251.2`}
                      strokeLinecap="round"
                      transform="rotate(-90 50 50)"
                    />
                  </>
                )}
              </svg>
              <div className="tasks-donut-center">
                <span className="tasks-donut-value">{metrics.tasks.done}</span>
                <span className="tasks-donut-label">Done</span>
              </div>
            </div>
            <div className="tasks-legend">
              <div className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: '#00c875' }} />
                <span>Completed: {metrics.tasks.done}</span>
              </div>
              <div className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: '#fdab3d' }} />
                <span>Pending: {metrics.tasks.pending}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Second Row */}
      <div className="dashboard-charts">
        {/* Lead Status */}
        <div className="chart-card">
          <h3>Lead Pipeline</h3>
          <div className="lead-funnel">
            <div className="funnel-stage">
              <div className="funnel-bar" style={{ width: '100%', backgroundColor: '#ff6d3b' }}>
                <span>New Leads</span>
                <span>{metrics.leads.new}</span>
              </div>
            </div>
            <div className="funnel-stage">
              <div className="funnel-bar" style={{ width: '80%', backgroundColor: '#fdab3d' }}>
                <span>Working On</span>
                <span>{metrics.leads.working}</span>
              </div>
            </div>
            <div className="funnel-stage">
              <div className="funnel-bar" style={{ width: '60%', backgroundColor: '#00c875' }}>
                <span>Qualified</span>
                <span>{metrics.leads.qualified}</span>
              </div>
            </div>
          </div>
          <div className="chart-footer">
            <Link to="/leads" className="chart-link">
              View all leads <ArrowRight size={14} />
            </Link>
          </div>
        </div>

        {/* Account Types */}
        <div className="chart-card">
          <h3>Accounts by Type</h3>
          <div className="accounts-chart">
            {topLabels.map(([label, count]) => (
              <div key={label} className="account-bar-row">
                <span className="account-label">{label}</span>
                <div className="account-bar-container">
                  <div
                    className="account-bar"
                    style={{ width: `${(count / maxLabelCount) * 100}%` }}
                  />
                </div>
                <span className="account-count">{count}</span>
              </div>
            ))}
          </div>
          <div className="chart-footer">
            <Link to="/accounts" className="chart-link">
              View all {metrics.accounts.total} accounts <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Stats Row */}
      <div className="quick-stats">
        <Link to="/contacts" className="quick-stat">
          <Users size={20} />
          <span className="quick-stat-value">{metrics.contacts.total}</span>
          <span className="quick-stat-label">Contacts</span>
        </Link>
        <Link to="/accounts" className="quick-stat">
          <Building2 size={20} />
          <span className="quick-stat-value">{metrics.accounts.total}</span>
          <span className="quick-stat-label">Accounts</span>
        </Link>
        <Link to="/tasks" className="quick-stat">
          <CheckSquare size={20} />
          <span className="quick-stat-value">{metrics.tasks.pending}</span>
          <span className="quick-stat-label">Open Tasks</span>
        </Link>
        {currentWorkspace?.id === 2 && (
          <Link to="/opportunities" className="quick-stat">
            <TrendingUp size={20} />
            <span className="quick-stat-value">{metrics.opportunities.total}</span>
            <span className="quick-stat-label">Opportunities</span>
          </Link>
        )}
      </div>
    </div>
  );
}

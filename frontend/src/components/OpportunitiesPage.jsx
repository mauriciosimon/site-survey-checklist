/**
 * OpportunitiesPage Component
 * Displays opportunities in Table view with Grade field filtering
 * For Business Technology Group workspace
 */

import { useState, useEffect, useCallback } from 'react';
import { opportunityApi } from '../api';
import { useWorkspace } from '../WorkspaceContext';
import TableView from './ui/TableView';

// ============================================
// CONSTANTS
// ============================================

const STAGE_OPTIONS = [
  { value: '', label: 'All Stages' },
  { value: 'Leads', label: 'Leads' },
  { value: 'Estimating', label: 'Estimating' },
  { value: 'Submitted', label: 'Submitted' },
  { value: 'Submitted Revisions', label: 'Submitted Revisions' },
  { value: 'Small works', label: 'Small Works' },
  { value: 'Won', label: 'Won' },
  { value: 'Signed - Small works', label: 'Signed - Small Works' },
  { value: 'Lost', label: 'Lost' },
  { value: 'Declined', label: 'Declined' },
];

const GRADE_OPTIONS = [
  { value: '', label: 'All Grades' },
  { value: 'Grade 1', label: 'Grade 1 (Hot)' },
  { value: 'Grade 2', label: 'Grade 2 (Warm)' },
  { value: 'Grade 3', label: 'Grade 3 (Cold)' },
];

// Table columns configuration
const TABLE_COLUMNS = [
  { key: 'name', label: 'Name', type: 'text', width: 250, sortable: true },
  { key: 'stage', label: 'Stage', type: 'status', statusType: 'opportunity_stage', width: 140, sortable: true },
  { key: 'grade', label: 'Grade', type: 'status', statusType: 'opportunity_grade', width: 100, sortable: true },
  { key: 'company_name', label: 'Company', type: 'text', width: 150, sortable: true },
  { key: 'contact_name', label: 'Contact', type: 'text', width: 140, sortable: true },
  { key: 'sale_price', label: 'Sale Price', type: 'currency', width: 120, sortable: true },
  { key: 'next_interaction', label: 'Next Action', type: 'date', width: 120, sortable: true },
  { key: 'owner_name', label: 'Estimator', type: 'person', width: 140, sortable: true },
];

// ============================================
// OPPORTUNITY FORM MODAL COMPONENT
// ============================================

function OpportunityFormModal({ opportunity, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    stage: 'Leads',
    grade: '',
    contact_name: '',
    company_name: '',
    email: '',
    phone: '',
    sale_price: '',
    close_probability: '',
    owner_name: '',
    survey_required: false,
    quote_template: '',
    next_interaction: '',
    return_date: '',
    quote_sent_date: '',
    decision_date: '',
    close_date: '',
    location_address: '',
    link: '',
    ...opportunity,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      // Clean up empty values
      const cleanData = {};
      Object.entries(formData).forEach(([key, val]) => {
        if (val !== '' && val !== null) {
          if (key === 'sale_price' && val) {
            cleanData[key] = parseFloat(val);
          } else if (key === 'close_probability' && val) {
            cleanData[key] = parseInt(val, 10);
          } else {
            cleanData[key] = val;
          }
        }
      });

      if (opportunity?.id) {
        await opportunityApi.update(opportunity.id, cleanData);
      } else {
        await opportunityApi.create(cleanData);
      }
      onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save opportunity');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content task-form-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{opportunity?.id ? 'Edit Opportunity' : 'New Opportunity'}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="form-error">{error}</div>}

          <div className="form-grid">
            <div className="form-group full-width">
              <label htmlFor="name">Opportunity Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Enter opportunity name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="stage">Stage</label>
              <select id="stage" name="stage" value={formData.stage} onChange={handleChange}>
                {STAGE_OPTIONS.slice(1).map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="grade">Grade</label>
              <select id="grade" name="grade" value={formData.grade || ''} onChange={handleChange}>
                {GRADE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="company_name">Company</label>
              <input
                type="text"
                id="company_name"
                name="company_name"
                value={formData.company_name || ''}
                onChange={handleChange}
                placeholder="Company name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact_name">Contact</label>
              <input
                type="text"
                id="contact_name"
                name="contact_name"
                value={formData.contact_name || ''}
                onChange={handleChange}
                placeholder="Contact name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email || ''}
                onChange={handleChange}
                placeholder="Email address"
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input
                type="text"
                id="phone"
                name="phone"
                value={formData.phone || ''}
                onChange={handleChange}
                placeholder="Phone number"
              />
            </div>

            <div className="form-group">
              <label htmlFor="sale_price">Sale Price (GBP)</label>
              <input
                type="number"
                id="sale_price"
                name="sale_price"
                value={formData.sale_price || ''}
                onChange={handleChange}
                placeholder="0.00"
                step="0.01"
              />
            </div>

            <div className="form-group">
              <label htmlFor="close_probability">Close Probability (%)</label>
              <input
                type="number"
                id="close_probability"
                name="close_probability"
                value={formData.close_probability || ''}
                onChange={handleChange}
                placeholder="0-100"
                min="0"
                max="100"
              />
            </div>

            <div className="form-group">
              <label htmlFor="owner_name">Estimator</label>
              <input
                type="text"
                id="owner_name"
                name="owner_name"
                value={formData.owner_name || ''}
                onChange={handleChange}
                placeholder="Estimator name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="next_interaction">Next Interaction</label>
              <input
                type="date"
                id="next_interaction"
                name="next_interaction"
                value={formData.next_interaction || ''}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="decision_date">Decision Date</label>
              <input
                type="date"
                id="decision_date"
                name="decision_date"
                value={formData.decision_date || ''}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="close_date">Close Date</label>
              <input
                type="date"
                id="close_date"
                name="close_date"
                value={formData.close_date || ''}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="survey_required"
                  checked={formData.survey_required || false}
                  onChange={handleChange}
                />
                Survey Required
              </label>
            </div>

            <div className="form-group full-width">
              <label htmlFor="location_address">Location</label>
              <input
                type="text"
                id="location_address"
                name="location_address"
                value={formData.location_address || ''}
                onChange={handleChange}
                placeholder="Address"
              />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : (opportunity?.id ? 'Update Opportunity' : 'Create Opportunity')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================
// OPPORTUNITIES PAGE COMPONENT
// ============================================

export default function OpportunitiesPage() {
  // Workspace context
  const { currentWorkspace } = useWorkspace();

  // Data state
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [filters, setFilters] = useState({
    stage: '',
    grade: '',
    search: '',
  });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);

  // Fetch opportunities
  const fetchOpportunities = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await opportunityApi.getAll({
        ...filters,
        workspace_id: currentWorkspace?.id,
      });
      setOpportunities(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load opportunities');
    } finally {
      setLoading(false);
    }
  }, [filters, currentWorkspace]);

  useEffect(() => {
    if (currentWorkspace) {
      fetchOpportunities();
    }
  }, [fetchOpportunities, currentWorkspace]);

  // Handle filter change
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  // Handle search
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setFilters((prev) => ({ ...prev, search: value }));
  };

  // Handle row click
  const handleOpportunityClick = (opp) => {
    setSelectedOpportunity(opp);
    setShowModal(true);
  };

  // Handle new opportunity button
  const handleNewOpportunity = () => {
    setSelectedOpportunity(null);
    setShowModal(true);
  };

  // Handle modal save
  const handleModalSave = () => {
    setShowModal(false);
    setSelectedOpportunity(null);
    fetchOpportunities();
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowModal(false);
    setSelectedOpportunity(null);
  };

  // Count opportunities by stage
  const leadsCount = opportunities.filter(o => o.stage === 'Leads').length;
  const estimatingCount = opportunities.filter(o => o.stage === 'Estimating').length;
  const wonCount = opportunities.filter(o => o.stage === 'Won').length;

  return (
    <div className="page-container opportunities-page">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-title-section">
          <h1>Opportunities</h1>
          <span className="record-count">{opportunities.length} opportunities</span>
          <span className="task-stats">
            <span className="stat-item stat-todo">{leadsCount} leads</span>
            <span className="stat-item stat-progress">{estimatingCount} estimating</span>
            <span className="stat-item stat-done">{wonCount} won</span>
          </span>
        </div>

        <div className="page-actions">
          <button className="btn btn-primary" onClick={handleNewOpportunity}>
            + New Opportunity
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="page-toolbar">
        {/* Filters */}
        <div className="filters">
          <select
            name="stage"
            value={filters.stage}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {STAGE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <select
            name="grade"
            value={filters.grade}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {GRADE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search opportunities..."
            value={filters.search}
            onChange={handleSearchChange}
            className="search-input"
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-banner">
          {error}
          <button onClick={fetchOpportunities}>Retry</button>
        </div>
      )}

      {/* Content */}
      <div className="page-content">
        <TableView
          columns={TABLE_COLUMNS}
          data={opportunities}
          onRowClick={handleOpportunityClick}
          loading={loading}
          emptyMessage="No opportunities found. Create your first opportunity!"
        />
      </div>

      {/* Opportunity Form Modal */}
      {showModal && (
        <OpportunityFormModal
          opportunity={selectedOpportunity}
          onClose={handleModalClose}
          onSave={handleModalSave}
        />
      )}
    </div>
  );
}

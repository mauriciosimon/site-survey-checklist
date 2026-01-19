/**
 * DealsPage Component
 * Displays deals in Kanban or Table view with filtering
 */

import { useState, useEffect, useCallback } from 'react';
import { dealApi } from '../api';
import KanbanBoard, { DEAL_STAGES } from './ui/KanbanBoard';
import TableView from './ui/TableView';
import StatusBadge from './ui/StatusBadge';

// ============================================
// CONSTANTS
// ============================================

const STAGE_OPTIONS = [
  { value: '', label: 'All Stages' },
  { value: 'Prospects', label: 'Prospects' },
  { value: 'Preparing proposal', label: 'Preparing proposal' },
  { value: 'Proposal sent', label: 'Proposal sent' },
  { value: 'Closed Won', label: 'Closed Won' },
  { value: 'Lost', label: 'Lost' },
  { value: 'Completed', label: 'Completed' },
];

const GRADE_OPTIONS = [
  { value: '', label: 'All Grades' },
  { value: 'Grade 1', label: 'Grade 1 (Hot)' },
  { value: 'Grade 2', label: 'Grade 2 (Warm)' },
  { value: 'Grade 3', label: 'Grade 3 (Cold)' },
];

const DEAL_TYPE_OPTIONS = [
  { value: '', label: 'All Types' },
  { value: 'Monthly', label: 'Monthly' },
  { value: 'Project', label: 'Project' },
];

// Table columns configuration
const TABLE_COLUMNS = [
  { key: 'name', label: 'Name', type: 'text', width: 200, sortable: true },
  { key: 'stage', label: 'Stage', type: 'status', statusType: 'deal_stage', width: 150, sortable: true },
  { key: 'grade', label: 'Grade', type: 'status', statusType: 'grade', width: 100, sortable: true },
  { key: 'value', label: 'Value', type: 'currency', currency: '£', width: 120, sortable: true },
  { key: 'company_name', label: 'Company', type: 'text', width: 160, sortable: true },
  { key: 'contact_name', label: 'Contact', type: 'text', width: 140, sortable: true },
  { key: 'close_date', label: 'Close Date', type: 'date', width: 120, sortable: true },
  { key: 'deal_type', label: 'Type', type: 'text', width: 100, sortable: true },
];

// ============================================
// DEAL FORM MODAL COMPONENT
// ============================================

function DealFormModal({ deal, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    stage: 'Prospects',
    status: 'New deal',
    grade: '',
    value: '',
    deal_type: '',
    deal_length: '',
    company_name: '',
    contact_name: '',
    email: '',
    phone: '',
    next_interaction: '',
    proposal_sent_date: '',
    close_date: '',
    ...deal,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      // Clean up empty values and convert value to number
      const cleanData = {};
      Object.entries(formData).forEach(([key, val]) => {
        if (val !== '' && val !== null) {
          if (key === 'value' && val) {
            cleanData[key] = parseFloat(val);
          } else if (key === 'deal_length' && val) {
            cleanData[key] = parseInt(val, 10);
          } else {
            cleanData[key] = val;
          }
        }
      });

      if (deal?.id) {
        await dealApi.update(deal.id, cleanData);
      } else {
        await dealApi.create(cleanData);
      }
      onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save deal');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content deal-form-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{deal?.id ? 'Edit Deal' : 'New Deal'}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="form-error">{error}</div>}

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="name">Deal Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Project or deal name"
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
              <label htmlFor="deal_type">Deal Type</label>
              <select id="deal_type" name="deal_type" value={formData.deal_type || ''} onChange={handleChange}>
                {DEAL_TYPE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="value">Value (GBP)</label>
              <input
                type="number"
                id="value"
                name="value"
                value={formData.value || ''}
                onChange={handleChange}
                placeholder="0.00"
                step="0.01"
                min="0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="deal_length">Deal Length (months)</label>
              <input
                type="number"
                id="deal_length"
                name="deal_length"
                value={formData.deal_length || ''}
                onChange={handleChange}
                placeholder="12"
                min="1"
              />
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
              <label htmlFor="contact_name">Contact Name</label>
              <input
                type="text"
                id="contact_name"
                name="contact_name"
                value={formData.contact_name || ''}
                onChange={handleChange}
                placeholder="Contact person"
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
                placeholder="email@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone || ''}
                onChange={handleChange}
                placeholder="+44 123 456 7890"
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
              <label htmlFor="close_date">Close Date</label>
              <input
                type="date"
                id="close_date"
                name="close_date"
                value={formData.close_date || ''}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : (deal?.id ? 'Update Deal' : 'Create Deal')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================
// DEALS PAGE COMPONENT
// ============================================

export default function DealsPage() {
  // View state
  const [viewMode, setViewMode] = useState('kanban'); // 'kanban' or 'table'

  // Data state
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [filters, setFilters] = useState({
    stage: '',
    grade: '',
    deal_type: '',
    search: '',
  });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedDeal, setSelectedDeal] = useState(null);

  // Fetch deals
  const fetchDeals = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await dealApi.getAll(filters);
      setDeals(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load deals');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchDeals();
  }, [fetchDeals]);

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

  // Handle Kanban stage change (drag & drop)
  const handleStageChange = async (itemId, newStageId, newStageLabel) => {
    try {
      // Map stage ID to stage value
      const stageIdToValue = {
        'prospects': 'Prospects',
        'preparing_proposal': 'Preparing proposal',
        'proposal_sent': 'Proposal sent',
        'closed_won': 'Closed Won',
        'lost': 'Lost',
        'completed': 'Completed',
      };

      const newStage = stageIdToValue[newStageId] || newStageLabel;

      // Optimistic update
      setDeals((prev) =>
        prev.map((deal) =>
          deal.id === itemId ? { ...deal, stage: newStage } : deal
        )
      );

      // API update
      await dealApi.update(itemId, { stage: newStage });
    } catch (err) {
      // Revert on error
      fetchDeals();
      console.error('Failed to update deal stage:', err);
    }
  };

  // Handle row/card click
  const handleDealClick = (deal) => {
    setSelectedDeal(deal);
    setShowModal(true);
  };

  // Handle new deal button
  const handleNewDeal = () => {
    setSelectedDeal(null);
    setShowModal(true);
  };

  // Handle modal save
  const handleModalSave = () => {
    setShowModal(false);
    setSelectedDeal(null);
    fetchDeals();
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowModal(false);
    setSelectedDeal(null);
  };

  // Calculate total pipeline value
  const totalValue = deals.reduce((sum, deal) => sum + (parseFloat(deal.value) || 0), 0);

  return (
    <div className="page-container deals-page">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-title-section">
          <h1>Deals</h1>
          <span className="record-count">{deals.length} deals</span>
          <span className="pipeline-value">Pipeline: £{totalValue.toLocaleString('en-GB', { minimumFractionDigits: 2 })}</span>
        </div>

        <div className="page-actions">
          <button className="btn btn-primary" onClick={handleNewDeal}>
            + New Deal
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="page-toolbar">
        {/* View Toggle */}
        <div className="view-toggle">
          <button
            className={`view-btn ${viewMode === 'kanban' ? 'active' : ''}`}
            onClick={() => setViewMode('kanban')}
            title="Kanban View"
          >
            <span className="view-icon">|||</span>
            Kanban
          </button>
          <button
            className={`view-btn ${viewMode === 'table' ? 'active' : ''}`}
            onClick={() => setViewMode('table')}
            title="Table View"
          >
            <span className="view-icon">=</span>
            Table
          </button>
        </div>

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

          <select
            name="deal_type"
            value={filters.deal_type}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {DEAL_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search deals..."
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
          <button onClick={fetchDeals}>Retry</button>
        </div>
      )}

      {/* Content */}
      <div className="page-content">
        {viewMode === 'kanban' ? (
          <KanbanBoard
            stages={DEAL_STAGES}
            items={deals}
            stageField="stage"
            onItemMove={handleStageChange}
            onItemClick={handleDealClick}
            cardFields={['company_name', 'contact_name', 'value', 'grade']}
            loading={loading}
          />
        ) : (
          <TableView
            columns={TABLE_COLUMNS}
            data={deals}
            onRowClick={handleDealClick}
            loading={loading}
            emptyMessage="No deals found. Create your first deal!"
          />
        )}
      </div>

      {/* Deal Form Modal */}
      {showModal && (
        <DealFormModal
          deal={selectedDeal}
          onClose={handleModalClose}
          onSave={handleModalSave}
        />
      )}
    </div>
  );
}

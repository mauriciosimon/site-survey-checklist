/**
 * LeadsPage Component
 * Displays leads in Kanban or Table view with filtering
 */

import { useState, useEffect, useCallback } from 'react';
import { leadApi } from '../api';
import { useWorkspace } from '../WorkspaceContext';
import KanbanBoard, { LEAD_STAGES } from './ui/KanbanBoard';
import TableView from './ui/TableView';
import StatusBadge from './ui/StatusBadge';

// ============================================
// CONSTANTS
// ============================================

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'New Lead', label: 'New Lead' },
  { value: 'Working on it', label: 'Working on it' },
  { value: 'Prospect', label: 'Prospect' },
  { value: 'Unqualified', label: 'Unqualified' },
];

const PRIORITY_OPTIONS = [
  { value: '', label: 'All Priorities' },
  { value: 'Critical', label: 'Critical' },
  { value: 'High', label: 'High' },
  { value: 'Medium', label: 'Medium' },
  { value: 'Low', label: 'Low' },
];

const SOURCE_OPTIONS = [
  { value: '', label: 'All Sources' },
  { value: 'Networking', label: 'Networking' },
  { value: 'Linkedin', label: 'LinkedIn' },
  { value: 'Existing contact', label: 'Existing Contact' },
  { value: 'WOM', label: 'Word of Mouth' },
  { value: 'Fractional Dubai', label: 'Fractional Dubai' },
];

// Table columns configuration
const TABLE_COLUMNS = [
  { key: 'name', label: 'Name', type: 'text', width: 200, sortable: true },
  { key: 'status', label: 'Status', type: 'status', statusType: 'lead_status', width: 140, sortable: true },
  { key: 'priority', label: 'Priority', type: 'status', statusType: 'priority', width: 100, sortable: true },
  { key: 'source', label: 'Source', type: 'text', width: 130, sortable: true },
  { key: 'contact_name', label: 'Contact', type: 'text', width: 150, sortable: true },
  { key: 'email', label: 'Email', type: 'email', width: 200, sortable: true },
  { key: 'phone', label: 'Phone', type: 'phone', width: 130, sortable: false },
  { key: 'next_interaction_date', label: 'Next Interaction', type: 'date', width: 140, sortable: true },
];

// ============================================
// LEAD FORM MODAL COMPONENT
// ============================================

function LeadFormModal({ lead, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    status: 'New Lead',
    priority: '',
    source: '',
    contact_name: '',
    job_title: '',
    email: '',
    phone: '',
    next_interaction_date: '',
    notes: '',
    ...lead,
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
      // Clean up empty values
      const cleanData = Object.fromEntries(
        Object.entries(formData).filter(([_, v]) => v !== '' && v !== null)
      );

      if (lead?.id) {
        await leadApi.update(lead.id, cleanData);
      } else {
        await leadApi.create(cleanData);
      }
      onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save lead');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content lead-form-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{lead?.id ? 'Edit Lead' : 'New Lead'}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="form-error">{error}</div>}

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="name">Lead Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Company or lead name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="status">Status</label>
              <select id="status" name="status" value={formData.status} onChange={handleChange}>
                {STATUS_OPTIONS.slice(1).map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="priority">Priority</label>
              <select id="priority" name="priority" value={formData.priority || ''} onChange={handleChange}>
                {PRIORITY_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="source">Source</label>
              <select id="source" name="source" value={formData.source || ''} onChange={handleChange}>
                {SOURCE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="contact_name">Contact Name</label>
              <input
                type="text"
                id="contact_name"
                name="contact_name"
                value={formData.contact_name || ''}
                onChange={handleChange}
                placeholder="Person's name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="job_title">Job Title</label>
              <input
                type="text"
                id="job_title"
                name="job_title"
                value={formData.job_title || ''}
                onChange={handleChange}
                placeholder="e.g., Project Manager"
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
              <label htmlFor="next_interaction_date">Next Interaction</label>
              <input
                type="date"
                id="next_interaction_date"
                name="next_interaction_date"
                value={formData.next_interaction_date || ''}
                onChange={handleChange}
              />
            </div>

            <div className="form-group full-width">
              <label htmlFor="notes">Notes</label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes || ''}
                onChange={handleChange}
                rows={3}
                placeholder="Additional notes about this lead..."
              />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : (lead?.id ? 'Update Lead' : 'Create Lead')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================
// LEADS PAGE COMPONENT
// ============================================

export default function LeadsPage() {
  // Workspace context
  const { currentWorkspace } = useWorkspace();

  // View state
  const [viewMode, setViewMode] = useState('kanban'); // 'kanban' or 'table'

  // Data state
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    source: '',
    search: '',
  });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);

  // Fetch leads
  const fetchLeads = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await leadApi.getAll({
        ...filters,
        workspace_id: currentWorkspace?.id,
      });
      setLeads(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load leads');
    } finally {
      setLoading(false);
    }
  }, [filters, currentWorkspace]);

  useEffect(() => {
    if (currentWorkspace) {
      fetchLeads();
    }
  }, [fetchLeads, currentWorkspace]);

  // Handle filter change
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  // Handle search with debounce
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setFilters((prev) => ({ ...prev, search: value }));
  };

  // Handle Kanban stage change (drag & drop)
  const handleStageChange = async (itemId, newStageId, newStageLabel) => {
    try {
      // Map stage ID to status value
      const stageToStatus = {
        'new_leads': 'New Lead',
        'working_on_it': 'Working on it',
        'prospect': 'Prospect',
        'unqualified': 'Unqualified',
      };

      const newStatus = stageToStatus[newStageId] || newStageLabel;

      // Optimistic update
      setLeads((prev) =>
        prev.map((lead) =>
          lead.id === itemId ? { ...lead, status: newStatus } : lead
        )
      );

      // API update
      await leadApi.update(itemId, { status: newStatus });
    } catch (err) {
      // Revert on error
      fetchLeads();
      console.error('Failed to update lead status:', err);
    }
  };

  // Handle row/card click
  const handleLeadClick = (lead) => {
    setSelectedLead(lead);
    setShowModal(true);
  };

  // Handle new lead button
  const handleNewLead = () => {
    setSelectedLead(null);
    setShowModal(true);
  };

  // Handle modal save
  const handleModalSave = () => {
    setShowModal(false);
    setSelectedLead(null);
    fetchLeads();
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowModal(false);
    setSelectedLead(null);
  };

  return (
    <div className="page-container leads-page">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-title-section">
          <h1>Leads</h1>
          <span className="record-count">{leads.length} leads</span>
        </div>

        <div className="page-actions">
          <button className="btn btn-primary" onClick={handleNewLead}>
            + New Lead
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
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <select
            name="priority"
            value={filters.priority}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {PRIORITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <select
            name="source"
            value={filters.source}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {SOURCE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search leads..."
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
          <button onClick={fetchLeads}>Retry</button>
        </div>
      )}

      {/* Content */}
      <div className="page-content">
        {viewMode === 'kanban' ? (
          <KanbanBoard
            stages={LEAD_STAGES}
            items={leads}
            stageField="status"
            onItemMove={handleStageChange}
            onItemClick={handleLeadClick}
            cardFields={['contact_name', 'priority', 'next_interaction_date']}
            loading={loading}
          />
        ) : (
          <TableView
            columns={TABLE_COLUMNS}
            data={leads}
            onRowClick={handleLeadClick}
            loading={loading}
            emptyMessage="No leads found. Create your first lead!"
          />
        )}
      </div>

      {/* Lead Form Modal */}
      {showModal && (
        <LeadFormModal
          lead={selectedLead}
          onClose={handleModalClose}
          onSave={handleModalSave}
        />
      )}
    </div>
  );
}

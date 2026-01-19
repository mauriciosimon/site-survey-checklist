/**
 * AccountsPage Component
 * Displays accounts in Table view with filtering
 */

import { useState, useEffect, useCallback } from 'react';
import { accountApi } from '../api';
import TableView from './ui/TableView';
import StatusBadge from './ui/StatusBadge';

// ============================================
// CONSTANTS
// ============================================

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'Active', label: 'Active' },
  { value: 'Inactive', label: 'Inactive' },
  { value: 'Qualified', label: 'Qualified' },
  { value: 'Prospect', label: 'Prospect' },
];

const LABEL_OPTIONS = [
  { value: '', label: 'All Labels' },
  { value: 'Contractor', label: 'Contractor' },
  { value: 'Main Contractor', label: 'Main Contractor' },
  { value: 'Property Developer', label: 'Property Developer' },
  { value: 'Construction and Engineering', label: 'Construction & Engineering' },
  { value: 'Real Estate and Property', label: 'Real Estate & Property' },
  { value: 'Interior Design and Furnishings', label: 'Interior Design' },
  { value: 'Food and Hospitality', label: 'Food & Hospitality' },
  { value: 'Consulting and Financial Services', label: 'Consulting & Financial' },
];

const INDUSTRY_OPTIONS = [
  { value: '', label: 'All Industries' },
  { value: 'Construction', label: 'Construction' },
  { value: 'Real Estate', label: 'Real Estate' },
  { value: 'Architecture', label: 'Architecture' },
  { value: 'Interior Design', label: 'Interior Design' },
  { value: 'Engineering', label: 'Engineering' },
  { value: 'Hospitality', label: 'Hospitality' },
  { value: 'Financial Services', label: 'Financial Services' },
];

const EMPLOYEE_COUNT_OPTIONS = [
  { value: '', label: 'Any Size' },
  { value: '1-10', label: '1-10' },
  { value: '11-50', label: '11-50' },
  { value: '51-100', label: '51-100' },
  { value: '101-250', label: '101-250' },
  { value: '251-500', label: '251-500' },
  { value: '501-1000', label: '501-1000' },
  { value: '1001+', label: '1001+' },
];

// Table columns configuration
const TABLE_COLUMNS = [
  { key: 'name', label: 'Account Name', type: 'text', width: 220, sortable: true },
  { key: 'status', label: 'Status', type: 'status', statusType: 'status', width: 120, sortable: true },
  { key: 'label', label: 'Label', type: 'status', statusType: 'status', width: 160, sortable: true },
  { key: 'industry', label: 'Industry', type: 'text', width: 150, sortable: true },
  {
    key: 'website',
    label: 'Website',
    type: 'text',
    width: 180,
    sortable: false,
    render: (value) => value ? (
      <a
        href={value.startsWith('http') ? value : `https://${value}`}
        target="_blank"
        rel="noopener noreferrer"
        className="table-cell-link"
        onClick={(e) => e.stopPropagation()}
      >
        {value.replace(/^https?:\/\//, '')}
      </a>
    ) : <span className="table-cell-empty">-</span>
  },
  { key: 'employee_count', label: 'Employees', type: 'text', width: 100, sortable: true },
  { key: 'owner_name', label: 'Owner', type: 'person', width: 140, sortable: true },
];

// ============================================
// ACCOUNT FORM MODAL COMPONENT
// ============================================

function AccountFormModal({ account, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    status: 'Prospect',
    label: '',
    industry: '',
    employee_count: '',
    account_type: '',
    website: '',
    company_profile_url: '',
    address: '',
    owner_name: '',
    owner_job_title: '',
    notes: '',
    ...account,
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

      if (account?.id) {
        await accountApi.update(account.id, cleanData);
      } else {
        await accountApi.create(cleanData);
      }
      onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save account');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content account-form-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{account?.id ? 'Edit Account' : 'New Account'}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="form-error">{error}</div>}

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="name">Account Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Company name"
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
              <label htmlFor="label">Label</label>
              <select id="label" name="label" value={formData.label || ''} onChange={handleChange}>
                {LABEL_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="industry">Industry</label>
              <input
                type="text"
                id="industry"
                name="industry"
                value={formData.industry || ''}
                onChange={handleChange}
                placeholder="e.g., Construction, Real Estate"
              />
            </div>

            <div className="form-group">
              <label htmlFor="employee_count">Employee Count</label>
              <select id="employee_count" name="employee_count" value={formData.employee_count || ''} onChange={handleChange}>
                {EMPLOYEE_COUNT_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="account_type">Account Type</label>
              <input
                type="text"
                id="account_type"
                name="account_type"
                value={formData.account_type || ''}
                onChange={handleChange}
                placeholder="e.g., Enterprise, SMB"
              />
            </div>

            <div className="form-group">
              <label htmlFor="website">Website</label>
              <input
                type="text"
                id="website"
                name="website"
                value={formData.website || ''}
                onChange={handleChange}
                placeholder="www.example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="company_profile_url">Company Profile URL</label>
              <input
                type="url"
                id="company_profile_url"
                name="company_profile_url"
                value={formData.company_profile_url || ''}
                onChange={handleChange}
                placeholder="LinkedIn or other profile URL"
              />
            </div>

            <div className="form-group full-width">
              <label htmlFor="address">Address</label>
              <input
                type="text"
                id="address"
                name="address"
                value={formData.address || ''}
                onChange={handleChange}
                placeholder="Full business address"
              />
            </div>

            <div className="form-group">
              <label htmlFor="owner_name">Owner Name</label>
              <input
                type="text"
                id="owner_name"
                name="owner_name"
                value={formData.owner_name || ''}
                onChange={handleChange}
                placeholder="Account owner"
              />
            </div>

            <div className="form-group">
              <label htmlFor="owner_job_title">Owner Job Title</label>
              <input
                type="text"
                id="owner_job_title"
                name="owner_job_title"
                value={formData.owner_job_title || ''}
                onChange={handleChange}
                placeholder="e.g., Sales Manager"
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
                placeholder="Additional notes about this account..."
              />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : (account?.id ? 'Update Account' : 'Create Account')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================
// ACCOUNTS PAGE COMPONENT
// ============================================

export default function AccountsPage() {
  // Data state
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [filters, setFilters] = useState({
    status: '',
    label: '',
    industry: '',
    search: '',
  });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);

  // Fetch accounts
  const fetchAccounts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await accountApi.getAll(filters);
      setAccounts(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load accounts');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

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
  const handleAccountClick = (account) => {
    setSelectedAccount(account);
    setShowModal(true);
  };

  // Handle new account button
  const handleNewAccount = () => {
    setSelectedAccount(null);
    setShowModal(true);
  };

  // Handle modal save
  const handleModalSave = () => {
    setShowModal(false);
    setSelectedAccount(null);
    fetchAccounts();
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowModal(false);
    setSelectedAccount(null);
  };

  return (
    <div className="page-container accounts-page">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-title-section">
          <h1>Accounts</h1>
          <span className="record-count">{accounts.length} accounts</span>
        </div>

        <div className="page-actions">
          <button className="btn btn-primary" onClick={handleNewAccount}>
            + New Account
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="page-toolbar">
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
            name="label"
            value={filters.label}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {LABEL_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <select
            name="industry"
            value={filters.industry}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {INDUSTRY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search accounts..."
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
          <button onClick={fetchAccounts}>Retry</button>
        </div>
      )}

      {/* Content */}
      <div className="page-content">
        <TableView
          columns={TABLE_COLUMNS}
          data={accounts}
          onRowClick={handleAccountClick}
          loading={loading}
          emptyMessage="No accounts found. Create your first account!"
        />
      </div>

      {/* Account Form Modal */}
      {showModal && (
        <AccountFormModal
          account={selectedAccount}
          onClose={handleModalClose}
          onSave={handleModalSave}
        />
      )}
    </div>
  );
}

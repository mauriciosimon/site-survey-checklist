/**
 * ContactsPage Component
 * Displays contacts in Table view with filtering
 */

import { useState, useEffect, useCallback } from 'react';
import { contactApi, accountApi } from '../api';
import TableView from './ui/TableView';

// ============================================
// CONSTANTS
// ============================================

const CONTACT_TYPE_OPTIONS = [
  { value: '', label: 'All Types' },
  { value: 'Client', label: 'Client' },
  { value: 'Past client', label: 'Past Client' },
  { value: 'Potential Lead', label: 'Potential Lead' },
  { value: 'In progress', label: 'In Progress' },
  { value: 'Architecture', label: 'Architecture' },
  { value: 'Interior design', label: 'Interior Design' },
  { value: 'Design & Build', label: 'Design & Build' },
  { value: 'Fit-Out Contractor', label: 'Fit-Out Contractor' },
  { value: 'Smart Building Solutions', label: 'Smart Building' },
  { value: 'Main contractor', label: 'Main Contractor' },
  { value: 'Joinery', label: 'Joinery' },
  { value: 'Partner', label: 'Partner' },
  { value: 'MEP Contractors', label: 'MEP Contractors' },
];

const ICP_FIT_OPTIONS = [
  { value: '', label: 'All ICP Fit' },
  { value: 'Yes', label: 'Yes' },
  { value: 'Maybe', label: 'Maybe' },
  { value: 'No', label: 'No' },
];

const OUTREACH_STAGE_OPTIONS = [
  { value: '', label: 'All Stages' },
  { value: 'Not touched', label: 'Not Touched' },
  { value: 'Profile viewed', label: 'Profile Viewed' },
  { value: 'Engaged (Like/comment)', label: 'Engaged' },
  { value: 'Connection sent', label: 'Connection Sent' },
  { value: 'Connected', label: 'Connected' },
  { value: 'DM Sent', label: 'DM Sent' },
  { value: 'Conversation live', label: 'Conversation Live' },
  { value: 'Qualified', label: 'Qualified' },
  { value: 'Parked/not ICP', label: 'Parked/Not ICP' },
];

const TITLE_ROLE_OPTIONS = [
  { value: '', label: 'Select Role' },
  { value: 'CEO', label: 'CEO' },
  { value: 'COO', label: 'COO' },
  { value: 'CIO', label: 'CIO' },
  { value: 'BDM', label: 'BDM' },
  { value: 'PM', label: 'PM' },
  { value: 'Co-founder', label: 'Co-founder' },
  { value: 'Director', label: 'Director' },
  { value: 'Manager', label: 'Manager' },
];

const TIER_OPTIONS = [
  { value: '', label: 'Select Tier' },
  { value: 'Tier 1', label: 'Tier 1' },
  { value: 'Tier 2', label: 'Tier 2' },
  { value: 'Tier 3', label: 'Tier 3' },
];

const SOURCE_OPTIONS = [
  { value: '', label: 'Select Source' },
  { value: 'LinkedIn', label: 'LinkedIn' },
  { value: 'Referral', label: 'Referral' },
  { value: 'Website', label: 'Website' },
  { value: 'Event', label: 'Event' },
  { value: 'Cold Outreach', label: 'Cold Outreach' },
  { value: 'Other', label: 'Other' },
];

// Table columns configuration
const TABLE_COLUMNS = [
  { key: 'name', label: 'Name', type: 'text', width: 180, sortable: true },
  { key: 'company', label: 'Company', type: 'text', width: 160, sortable: true },
  { key: 'contact_type', label: 'Type', type: 'status', statusType: 'contact_type', width: 140, sortable: true },
  { key: 'job_title', label: 'Job Title', type: 'text', width: 150, sortable: true },
  {
    key: 'email',
    label: 'Email',
    type: 'text',
    width: 200,
    sortable: false,
    render: (value) => value ? (
      <a
        href={`mailto:${value}`}
        className="table-cell-link"
        onClick={(e) => e.stopPropagation()}
      >
        {value}
      </a>
    ) : <span className="table-cell-empty">-</span>
  },
  {
    key: 'phone',
    label: 'Phone',
    type: 'text',
    width: 130,
    sortable: false,
    render: (value) => value ? (
      <a
        href={`tel:${value}`}
        className="table-cell-link"
        onClick={(e) => e.stopPropagation()}
      >
        {value}
      </a>
    ) : <span className="table-cell-empty">-</span>
  },
  { key: 'icp_fit', label: 'ICP Fit', type: 'status', statusType: 'icp_fit', width: 100, sortable: true },
  { key: 'outreach_stage', label: 'Outreach Stage', type: 'status', statusType: 'outreach_stage', width: 150, sortable: true },
  {
    key: 'linkedin_url',
    label: 'LinkedIn',
    type: 'text',
    width: 100,
    sortable: false,
    render: (value) => value ? (
      <a
        href={value.startsWith('http') ? value : `https://${value}`}
        target="_blank"
        rel="noopener noreferrer"
        className="table-cell-link"
        onClick={(e) => e.stopPropagation()}
      >
        View
      </a>
    ) : <span className="table-cell-empty">-</span>
  },
];

// ============================================
// CONTACT FORM MODAL COMPONENT
// ============================================

function ContactFormModal({ contact, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    contact_type: '',
    job_title: '',
    title_role: '',
    tier: '',
    email: '',
    phone: '',
    linkedin_url: '',
    icp_fit: '',
    outreach_stage: 'Not touched',
    source: '',
    account_id: '',
    about: '',
    description: '',
    ...contact,
  });
  const [accounts, setAccounts] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // Fetch accounts for dropdown
  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const response = await accountApi.getAll({ limit: 100 });
        setAccounts(response.data);
      } catch (err) {
        console.error('Failed to fetch accounts:', err);
      }
    };
    fetchAccounts();
  }, []);

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
      const cleanData = {};
      Object.entries(formData).forEach(([key, val]) => {
        if (val !== '' && val !== null) {
          if (key === 'account_id' && val) {
            cleanData[key] = parseInt(val, 10);
          } else {
            cleanData[key] = val;
          }
        }
      });

      if (contact?.id) {
        await contactApi.update(contact.id, cleanData);
      } else {
        await contactApi.create(cleanData);
      }
      onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save contact');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content contact-form-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{contact?.id ? 'Edit Contact' : 'New Contact'}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="form-error">{error}</div>}

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="name">Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Contact name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="company">Company</label>
              <input
                type="text"
                id="company"
                name="company"
                value={formData.company || ''}
                onChange={handleChange}
                placeholder="Company name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact_type">Type</label>
              <select id="contact_type" name="contact_type" value={formData.contact_type || ''} onChange={handleChange}>
                {CONTACT_TYPE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="job_title">Job Title</label>
              <input
                type="text"
                id="job_title"
                name="job_title"
                value={formData.job_title || ''}
                onChange={handleChange}
                placeholder="e.g., Sales Director"
              />
            </div>

            <div className="form-group">
              <label htmlFor="title_role">Role</label>
              <select id="title_role" name="title_role" value={formData.title_role || ''} onChange={handleChange}>
                {TITLE_ROLE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="tier">Tier</label>
              <select id="tier" name="tier" value={formData.tier || ''} onChange={handleChange}>
                {TIER_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
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
              <label htmlFor="linkedin_url">LinkedIn URL</label>
              <input
                type="url"
                id="linkedin_url"
                name="linkedin_url"
                value={formData.linkedin_url || ''}
                onChange={handleChange}
                placeholder="https://linkedin.com/in/..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="icp_fit">ICP Fit</label>
              <select id="icp_fit" name="icp_fit" value={formData.icp_fit || ''} onChange={handleChange}>
                {ICP_FIT_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="outreach_stage">Outreach Stage</label>
              <select id="outreach_stage" name="outreach_stage" value={formData.outreach_stage || ''} onChange={handleChange}>
                {OUTREACH_STAGE_OPTIONS.map((opt) => (
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
              <label htmlFor="account_id">Account</label>
              <select id="account_id" name="account_id" value={formData.account_id || ''} onChange={handleChange}>
                <option value="">No linked account</option>
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>{acc.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group full-width">
              <label htmlFor="about">Notes</label>
              <textarea
                id="about"
                name="about"
                value={formData.about || ''}
                onChange={handleChange}
                rows={3}
                placeholder="Additional notes about this contact..."
              />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : (contact?.id ? 'Update Contact' : 'Create Contact')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================
// CONTACTS PAGE COMPONENT
// ============================================

export default function ContactsPage() {
  // Data state
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [filters, setFilters] = useState({
    contact_type: '',
    icp_fit: '',
    outreach_stage: '',
    search: '',
  });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedContact, setSelectedContact] = useState(null);

  // Fetch contacts
  const fetchContacts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await contactApi.getAll(filters);
      setContacts(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load contacts');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchContacts();
  }, [fetchContacts]);

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
  const handleContactClick = (contact) => {
    setSelectedContact(contact);
    setShowModal(true);
  };

  // Handle new contact button
  const handleNewContact = () => {
    setSelectedContact(null);
    setShowModal(true);
  };

  // Handle modal save
  const handleModalSave = () => {
    setShowModal(false);
    setSelectedContact(null);
    fetchContacts();
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowModal(false);
    setSelectedContact(null);
  };

  return (
    <div className="page-container contacts-page">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-title-section">
          <h1>Contacts</h1>
          <span className="record-count">{contacts.length} contacts</span>
        </div>

        <div className="page-actions">
          <button className="btn btn-primary" onClick={handleNewContact}>
            + New Contact
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="page-toolbar">
        {/* Filters */}
        <div className="filters">
          <select
            name="contact_type"
            value={filters.contact_type}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {CONTACT_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <select
            name="icp_fit"
            value={filters.icp_fit}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {ICP_FIT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <select
            name="outreach_stage"
            value={filters.outreach_stage}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {OUTREACH_STAGE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search contacts..."
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
          <button onClick={fetchContacts}>Retry</button>
        </div>
      )}

      {/* Content */}
      <div className="page-content">
        <TableView
          columns={TABLE_COLUMNS}
          data={contacts}
          onRowClick={handleContactClick}
          loading={loading}
          emptyMessage="No contacts found. Create your first contact!"
        />
      </div>

      {/* Contact Form Modal */}
      {showModal && (
        <ContactFormModal
          contact={selectedContact}
          onClose={handleModalClose}
          onSave={handleModalSave}
        />
      )}
    </div>
  );
}

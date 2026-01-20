/**
 * TasksPage Component
 * Displays tasks in Table view with filtering
 */

import { useState, useEffect, useCallback } from 'react';
import { taskApi, dealApi, leadApi, accountApi, contactApi } from '../api';
import TableView from './ui/TableView';

// ============================================
// CONSTANTS
// ============================================

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'To do', label: 'To Do' },
  { value: 'Working on it', label: 'Working on it' },
  { value: 'Done', label: 'Done' },
  { value: 'Stuck', label: 'Stuck' },
  { value: 'On hold', label: 'On Hold' },
  { value: 'Need info', label: 'Need Info' },
  { value: 'Waiting for review', label: 'Waiting for Review' },
];

const PRIORITY_OPTIONS = [
  { value: '', label: 'All Priorities' },
  { value: 'Critical', label: 'Critical' },
  { value: 'High', label: 'High' },
  { value: 'Medium', label: 'Medium' },
  { value: 'Low', label: 'Low' },
];

const TASK_TYPE_OPTIONS = [
  { value: '', label: 'All Types' },
  { value: 'Finance', label: 'Finance' },
  { value: 'Birocratic', label: 'Birocratic' },
  { value: 'Marketing', label: 'Marketing' },
  { value: 'Other', label: 'Other' },
];

// Table columns configuration
const TABLE_COLUMNS = [
  { key: 'name', label: 'Name', type: 'text', width: 250, sortable: true },
  { key: 'status', label: 'Status', type: 'status', statusType: 'task_status', width: 140, sortable: true },
  { key: 'priority', label: 'Priority', type: 'status', statusType: 'priority', width: 100, sortable: true },
  { key: 'task_type', label: 'Type', type: 'text', width: 100, sortable: true },
  { key: 'due_date', label: 'Due Date', type: 'date', width: 120, sortable: true },
  { key: 'related_to', label: 'Related To', type: 'text', width: 150, sortable: true },
  { key: 'owner_name', label: 'Owner', type: 'person', width: 140, sortable: true },
];

// ============================================
// TASK FORM MODAL COMPONENT
// ============================================

function TaskFormModal({ task, onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    status: 'To do',
    priority: 'Medium',
    task_type: '',
    due_date: '',
    close_date: '',
    related_to: '',
    deal_id: '',
    lead_id: '',
    account_id: '',
    contact_id: '',
    notes: '',
    owner_name: '',
    ...task,
  });
  const [deals, setDeals] = useState([]);
  const [leads, setLeads] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // Fetch related entities for dropdowns
  useEffect(() => {
    const fetchRelatedEntities = async () => {
      try {
        const [dealsRes, leadsRes, accountsRes, contactsRes] = await Promise.all([
          dealApi.getAll({ limit: 100 }),
          leadApi.getAll({ limit: 100 }),
          accountApi.getAll({ limit: 100 }),
          contactApi.getAll({ limit: 100 }),
        ]);
        setDeals(dealsRes.data);
        setLeads(leadsRes.data);
        setAccounts(accountsRes.data);
        setContacts(contactsRes.data);
      } catch (err) {
        console.error('Failed to fetch related entities:', err);
      }
    };
    fetchRelatedEntities();
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
      // Clean up empty values and convert IDs
      const cleanData = {};
      Object.entries(formData).forEach(([key, val]) => {
        if (val !== '' && val !== null) {
          if (['deal_id', 'lead_id', 'account_id', 'contact_id'].includes(key) && val) {
            cleanData[key] = parseInt(val, 10);
          } else {
            cleanData[key] = val;
          }
        }
      });

      if (task?.id) {
        await taskApi.update(task.id, cleanData);
      } else {
        await taskApi.create(cleanData);
      }
      onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save task');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content task-form-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{task?.id ? 'Edit Task' : 'New Task'}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="form-error">{error}</div>}

          <div className="form-grid">
            <div className="form-group full-width">
              <label htmlFor="name">Task Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="What needs to be done?"
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
              <select id="priority" name="priority" value={formData.priority} onChange={handleChange}>
                {PRIORITY_OPTIONS.slice(1).map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="task_type">Type</label>
              <select id="task_type" name="task_type" value={formData.task_type || ''} onChange={handleChange}>
                {TASK_TYPE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="due_date">Due Date</label>
              <input
                type="date"
                id="due_date"
                name="due_date"
                value={formData.due_date || ''}
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
              <label htmlFor="owner_name">Owner</label>
              <input
                type="text"
                id="owner_name"
                name="owner_name"
                value={formData.owner_name || ''}
                onChange={handleChange}
                placeholder="Task owner"
              />
            </div>

            <div className="form-group">
              <label htmlFor="related_to">Related To</label>
              <input
                type="text"
                id="related_to"
                name="related_to"
                value={formData.related_to || ''}
                onChange={handleChange}
                placeholder="e.g., Project name, Event"
              />
            </div>

            <div className="form-group">
              <label htmlFor="deal_id">Link to Deal</label>
              <select id="deal_id" name="deal_id" value={formData.deal_id || ''} onChange={handleChange}>
                <option value="">No linked deal</option>
                {deals.map((deal) => (
                  <option key={deal.id} value={deal.id}>{deal.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="lead_id">Link to Lead</label>
              <select id="lead_id" name="lead_id" value={formData.lead_id || ''} onChange={handleChange}>
                <option value="">No linked lead</option>
                {leads.map((lead) => (
                  <option key={lead.id} value={lead.id}>{lead.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="account_id">Link to Account</label>
              <select id="account_id" name="account_id" value={formData.account_id || ''} onChange={handleChange}>
                <option value="">No linked account</option>
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>{acc.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="contact_id">Link to Contact</label>
              <select id="contact_id" name="contact_id" value={formData.contact_id || ''} onChange={handleChange}>
                <option value="">No linked contact</option>
                {contacts.map((contact) => (
                  <option key={contact.id} value={contact.id}>{contact.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group full-width">
              <label htmlFor="notes">Notes</label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes || ''}
                onChange={handleChange}
                rows={3}
                placeholder="Additional notes about this task..."
              />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : (task?.id ? 'Update Task' : 'Create Task')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================
// TASKS PAGE COMPONENT
// ============================================

export default function TasksPage() {
  // Data state
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    task_type: '',
    search: '',
  });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await taskApi.getAll(filters);
      setTasks(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

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
  const handleTaskClick = (task) => {
    setSelectedTask(task);
    setShowModal(true);
  };

  // Handle new task button
  const handleNewTask = () => {
    setSelectedTask(null);
    setShowModal(true);
  };

  // Handle modal save
  const handleModalSave = () => {
    setShowModal(false);
    setSelectedTask(null);
    fetchTasks();
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowModal(false);
    setSelectedTask(null);
  };

  // Count tasks by status
  const todoCount = tasks.filter(t => t.status === 'To do').length;
  const inProgressCount = tasks.filter(t => t.status === 'Working on it').length;
  const doneCount = tasks.filter(t => t.status === 'Done').length;

  return (
    <div className="page-container tasks-page">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-title-section">
          <h1>Tasks</h1>
          <span className="record-count">{tasks.length} tasks</span>
          <span className="task-stats">
            <span className="stat-item stat-todo">{todoCount} to do</span>
            <span className="stat-item stat-progress">{inProgressCount} in progress</span>
            <span className="stat-item stat-done">{doneCount} done</span>
          </span>
        </div>

        <div className="page-actions">
          <button className="btn btn-primary" onClick={handleNewTask}>
            + New Task
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
            name="task_type"
            value={filters.task_type}
            onChange={handleFilterChange}
            className="filter-select"
          >
            {TASK_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search tasks..."
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
          <button onClick={fetchTasks}>Retry</button>
        </div>
      )}

      {/* Content */}
      <div className="page-content">
        <TableView
          columns={TABLE_COLUMNS}
          data={tasks}
          onRowClick={handleTaskClick}
          loading={loading}
          emptyMessage="No tasks found. Create your first task!"
        />
      </div>

      {/* Task Form Modal */}
      {showModal && (
        <TaskFormModal
          task={selectedTask}
          onClose={handleModalClose}
          onSave={handleModalSave}
        />
      )}
    </div>
  );
}

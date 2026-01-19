/**
 * TableView Component
 * Displays board data in a sortable, resizable table format
 * Matches Monday.com/Satoris table styling
 */

import { useState, useRef, useCallback } from 'react';
import StatusBadge from './StatusBadge';

// ============================================
// COLUMN RENDERERS
// ============================================

/**
 * Format date for display
 */
function formatDate(dateStr) {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  } catch {
    return dateStr;
  }
}

/**
 * Format currency for display
 */
function formatCurrency(value, currency = '£') {
  if (value === null || value === undefined || value === '') return '-';
  const num = parseFloat(value);
  if (isNaN(num)) return value;
  return `${currency}${num.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/**
 * Render cell content based on column type
 */
function CellRenderer({ column, value, row }) {
  const { type, statusType, currency } = column;

  switch (type) {
    case 'status':
      return value ? (
        <StatusBadge
          label={value}
          type={statusType || 'status'}
          size="sm"
        />
      ) : (
        <span className="table-cell-empty">-</span>
      );

    case 'date':
      return <span className="table-cell-date">{formatDate(value)}</span>;

    case 'currency':
      return <span className="table-cell-currency">{formatCurrency(value, currency)}</span>;

    case 'email':
      return value ? (
        <a
          href={`mailto:${value}`}
          className="table-cell-link"
          onClick={(e) => e.stopPropagation()}
        >
          {value}
        </a>
      ) : (
        <span className="table-cell-empty">-</span>
      );

    case 'phone':
      return value ? (
        <a
          href={`tel:${value}`}
          className="table-cell-link"
          onClick={(e) => e.stopPropagation()}
        >
          {value}
        </a>
      ) : (
        <span className="table-cell-empty">-</span>
      );

    case 'person':
      return value ? (
        <div className="table-cell-person">
          <div className="person-avatar">
            {value.charAt(0).toUpperCase()}
          </div>
          <span className="person-name">{value}</span>
        </div>
      ) : (
        <span className="table-cell-empty">-</span>
      );

    case 'badge':
      return value ? (
        <span className={`table-badge ${column.badgeClass || ''}`}>
          {value}
        </span>
      ) : (
        <span className="table-cell-empty">-</span>
      );

    case 'text':
    default:
      return value !== null && value !== undefined && value !== '' ? (
        <span className="table-cell-text">{value}</span>
      ) : (
        <span className="table-cell-empty">-</span>
      );
  }
}

// ============================================
// COLUMN RESIZE HOOK
// ============================================

function useColumnResize(initialWidths) {
  const [columnWidths, setColumnWidths] = useState(initialWidths);
  const resizeRef = useRef(null);

  const startResize = useCallback((columnKey, startX, startWidth) => {
    resizeRef.current = { columnKey, startX, startWidth };

    const handleMouseMove = (e) => {
      if (!resizeRef.current) return;
      const diff = e.clientX - resizeRef.current.startX;
      const newWidth = Math.max(80, resizeRef.current.startWidth + diff);
      setColumnWidths((prev) => ({
        ...prev,
        [resizeRef.current.columnKey]: newWidth
      }));
    };

    const handleMouseUp = () => {
      resizeRef.current = null;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }, []);

  return { columnWidths, setColumnWidths, startResize };
}

// ============================================
// TABLE VIEW COMPONENT
// ============================================

/**
 * TableView Component
 *
 * @param {Object} props
 * @param {Array} props.columns - Column configuration array
 * @param {Array} props.data - Data array to display
 * @param {Function} props.onRowClick - Callback when row is clicked (receives row data)
 * @param {string} props.rowKey - Key field for unique row identification (default: 'id')
 * @param {boolean} props.loading - Show loading state
 * @param {string} props.emptyMessage - Message when no data
 * @param {boolean} props.stickyHeader - Keep header sticky on scroll
 * @param {string} props.className - Additional CSS class
 *
 * Column config:
 * {
 *   key: 'field_name',      // Data field key
 *   label: 'Column Title',  // Header text
 *   type: 'text',           // text|status|date|currency|email|phone|person|badge
 *   width: 150,             // Initial width in pixels
 *   sortable: true,         // Enable sorting
 *   statusType: 'status',   // For status type: status|grade|priority|deal_stage|lead_status
 *   currency: '£',          // For currency type
 *   render: (value, row) => JSX  // Custom render function
 * }
 */
export default function TableView({
  columns = [],
  data = [],
  onRowClick,
  rowKey = 'id',
  loading = false,
  emptyMessage = 'No data to display',
  stickyHeader = true,
  className = ''
}) {
  // Sort state
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // Column widths
  const initialWidths = columns.reduce((acc, col) => {
    acc[col.key] = col.width || 150;
    return acc;
  }, {});
  const { columnWidths, startResize } = useColumnResize(initialWidths);

  // Handle sort
  const handleSort = (column) => {
    if (!column.sortable) return;

    setSortConfig((prev) => {
      if (prev.key === column.key) {
        // Toggle direction or reset
        if (prev.direction === 'asc') {
          return { key: column.key, direction: 'desc' };
        } else {
          return { key: null, direction: 'asc' };
        }
      }
      return { key: column.key, direction: 'asc' };
    });
  };

  // Sort data
  const sortedData = [...data].sort((a, b) => {
    if (!sortConfig.key) return 0;

    const aVal = a[sortConfig.key];
    const bVal = b[sortConfig.key];

    // Handle nulls
    if (aVal === null || aVal === undefined) return 1;
    if (bVal === null || bVal === undefined) return -1;

    // Compare
    let comparison = 0;
    if (typeof aVal === 'string') {
      comparison = aVal.localeCompare(bVal);
    } else if (typeof aVal === 'number') {
      comparison = aVal - bVal;
    } else if (aVal instanceof Date || !isNaN(Date.parse(aVal))) {
      comparison = new Date(aVal) - new Date(bVal);
    } else {
      comparison = String(aVal).localeCompare(String(bVal));
    }

    return sortConfig.direction === 'asc' ? comparison : -comparison;
  });

  // Handle resize start
  const handleResizeStart = (e, columnKey) => {
    e.preventDefault();
    e.stopPropagation();
    const startX = e.clientX;
    const startWidth = columnWidths[columnKey] || 150;
    startResize(columnKey, startX, startWidth);
  };

  // Loading state
  if (loading) {
    return (
      <div className={`table-view-container ${className}`}>
        <div className="table-loading">
          <div className="loading-spinner" />
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  // Empty state
  if (data.length === 0) {
    return (
      <div className={`table-view-container ${className}`}>
        <div className="table-empty">
          <span className="empty-icon">-</span>
          <span>{emptyMessage}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`table-view-container ${className}`}>
      <div className="table-view-wrapper">
        <table className={`table-view ${stickyHeader ? 'sticky-header' : ''}`}>
          <thead>
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  style={{ width: columnWidths[column.key] || column.width || 150 }}
                  className={`
                    ${column.sortable ? 'sortable' : ''}
                    ${sortConfig.key === column.key ? `sorted-${sortConfig.direction}` : ''}
                  `}
                  onClick={() => handleSort(column)}
                >
                  <div className="th-content">
                    <span className="th-label">{column.label}</span>
                    {column.sortable && (
                      <span className="sort-indicator">
                        {sortConfig.key === column.key
                          ? sortConfig.direction === 'asc'
                            ? '\u25B2'
                            : '\u25BC'
                          : '\u25B2'}
                      </span>
                    )}
                  </div>
                  <div
                    className="resize-handle"
                    onMouseDown={(e) => handleResizeStart(e, column.key)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, rowIndex) => (
              <tr
                key={row[rowKey] || rowIndex}
                className={onRowClick ? 'clickable' : ''}
                onClick={() => onRowClick && onRowClick(row)}
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    style={{ width: columnWidths[column.key] || column.width || 150 }}
                  >
                    {column.render ? (
                      column.render(row[column.key], row)
                    ) : (
                      <CellRenderer
                        column={column}
                        value={row[column.key]}
                        row={row}
                      />
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============================================
// EXPORTS
// ============================================

export { CellRenderer, formatDate, formatCurrency };

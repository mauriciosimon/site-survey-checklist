/**
 * KanbanBoard Component
 * Displays items in a kanban/pipeline view with drag-and-drop
 * Matches Monday.com/Satoris kanban styling
 */

import { useState, useRef } from 'react';
import StatusBadge, { getGradeColor } from './StatusBadge';
import { formatCurrency } from './TableView';

// ============================================
// KANBAN CARD COMPONENT
// ============================================

/**
 * KanbanCard - Individual card in the kanban board
 */
function KanbanCard({
  item,
  stageColor,
  onDragStart,
  onDragEnd,
  onClick,
  isDragging,
  cardFields
}) {
  const handleDragStart = (e) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', JSON.stringify({ id: item.id }));
    onDragStart && onDragStart(item);
  };

  const handleDragEnd = (e) => {
    onDragEnd && onDragEnd();
  };

  // Default fields to display
  const fields = cardFields || ['company_name', 'contact_name', 'value', 'grade'];

  return (
    <div
      className={`kanban-card ${isDragging ? 'dragging' : ''}`}
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onClick={() => onClick && onClick(item)}
      style={{ '--card-accent': stageColor }}
    >
      {/* Card accent border */}
      <div className="card-accent" style={{ backgroundColor: stageColor }} />

      {/* Card content */}
      <div className="card-content">
        {/* Title/Name */}
        <div className="card-title">{item.name || 'Untitled'}</div>

        {/* Company */}
        {fields.includes('company_name') && item.company_name && (
          <div className="card-company">{item.company_name}</div>
        )}

        {/* Contact */}
        {fields.includes('contact_name') && item.contact_name && (
          <div className="card-contact">
            <span className="contact-avatar">
              {item.contact_name.charAt(0).toUpperCase()}
            </span>
            <span className="contact-name">{item.contact_name}</span>
          </div>
        )}

        {/* Footer with value and grade */}
        <div className="card-footer">
          {/* Value */}
          {fields.includes('value') && item.value !== undefined && item.value !== null && (
            <span className="card-value">{formatCurrency(item.value)}</span>
          )}

          {/* Grade badge */}
          {fields.includes('grade') && item.grade && (
            <StatusBadge
              label={item.grade}
              type="grade"
              size="sm"
            />
          )}
        </div>

        {/* Custom fields */}
        {item.customFields && (
          <div className="card-custom-fields">
            {Object.entries(item.customFields).map(([key, value]) => (
              <div key={key} className="custom-field">
                <span className="field-label">{key}:</span>
                <span className="field-value">{value}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================
// KANBAN COLUMN COMPONENT
// ============================================

/**
 * KanbanColumn - A single column/stage in the kanban board
 */
function KanbanColumn({
  stage,
  items,
  onDragOver,
  onDrop,
  onDragEnter,
  onDragLeave,
  isDropTarget,
  onItemClick,
  onItemDragStart,
  onItemDragEnd,
  draggingItem,
  cardFields
}) {
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    onDragOver && onDragOver(stage.id);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const data = e.dataTransfer.getData('text/plain');
    try {
      const { id } = JSON.parse(data);
      onDrop && onDrop(id, stage.id);
    } catch (err) {
      console.error('Drop error:', err);
    }
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    onDragEnter && onDragEnter(stage.id);
  };

  const handleDragLeave = (e) => {
    // Only trigger if leaving the column, not entering a child
    if (e.currentTarget === e.target) {
      onDragLeave && onDragLeave(stage.id);
    }
  };

  return (
    <div
      className={`kanban-column ${isDropTarget ? 'drop-target' : ''}`}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
    >
      {/* Column header */}
      <div className="column-header" style={{ '--header-color': stage.color }}>
        <div className="header-color-bar" style={{ backgroundColor: stage.color }} />
        <div className="header-content">
          <span className="header-label">{stage.label}</span>
          <span className="header-count">{items.length}</span>
        </div>
      </div>

      {/* Column body with cards */}
      <div className="column-body">
        {items.map((item) => (
          <KanbanCard
            key={item.id}
            item={item}
            stageColor={stage.color}
            onClick={onItemClick}
            onDragStart={onItemDragStart}
            onDragEnd={onItemDragEnd}
            isDragging={draggingItem?.id === item.id}
            cardFields={cardFields}
          />
        ))}

        {/* Empty state */}
        {items.length === 0 && (
          <div className="column-empty">
            <span>No items</span>
          </div>
        )}

        {/* Drop placeholder */}
        {isDropTarget && draggingItem && (
          <div className="drop-placeholder">
            <span>Drop here</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================
// KANBAN BOARD COMPONENT
// ============================================

/**
 * KanbanBoard Component
 *
 * @param {Object} props
 * @param {Array} props.stages - Stage/column configuration
 * @param {Array} props.items - Items to display (must have id and stage field)
 * @param {string} props.stageField - Field name for stage (default: 'stage')
 * @param {Function} props.onItemMove - Callback when item is moved (itemId, newStage)
 * @param {Function} props.onItemClick - Callback when item is clicked
 * @param {Array} props.cardFields - Fields to show on cards (default: ['company_name', 'contact_name', 'value', 'grade'])
 * @param {boolean} props.loading - Show loading state
 * @param {string} props.className - Additional CSS class
 *
 * Stage config:
 * {
 *   id: 'stage_id',       // Unique stage identifier
 *   label: 'Stage Name',  // Display label
 *   color: '#hexcolor'    // Stage color
 * }
 *
 * Item requirements:
 * - Must have 'id' field
 * - Must have stage field (default: 'stage') matching stage.id
 * - Optional: name, company_name, contact_name, value, grade
 */
export default function KanbanBoard({
  stages = [],
  items = [],
  stageField = 'stage',
  onItemMove,
  onItemClick,
  cardFields,
  loading = false,
  className = ''
}) {
  // Drag state
  const [draggingItem, setDraggingItem] = useState(null);
  const [dropTarget, setDropTarget] = useState(null);

  // Group items by stage
  const itemsByStage = stages.reduce((acc, stage) => {
    acc[stage.id] = items.filter((item) => {
      const itemStage = item[stageField];
      // Handle case-insensitive matching and variations
      if (!itemStage) return stage.id === 'unassigned';
      const normalizedItemStage = itemStage.toLowerCase().replace(/\s+/g, '_');
      const normalizedStageId = stage.id.toLowerCase().replace(/\s+/g, '_');
      return normalizedItemStage === normalizedStageId ||
             itemStage.toLowerCase() === stage.label.toLowerCase();
    });
    return acc;
  }, {});

  // Handle drag start
  const handleItemDragStart = (item) => {
    setDraggingItem(item);
  };

  // Handle drag end
  const handleItemDragEnd = () => {
    setDraggingItem(null);
    setDropTarget(null);
  };

  // Handle drop
  const handleDrop = (itemId, newStageId) => {
    const item = items.find((i) => i.id === itemId);
    if (!item) return;

    const currentStage = item[stageField];
    const targetStage = stages.find((s) => s.id === newStageId);

    // Check if actually moving to different stage
    if (currentStage?.toLowerCase() !== targetStage?.label?.toLowerCase() &&
        currentStage?.toLowerCase().replace(/\s+/g, '_') !== newStageId) {
      onItemMove && onItemMove(itemId, newStageId, targetStage?.label);
    }

    setDraggingItem(null);
    setDropTarget(null);
  };

  // Handle drag enter
  const handleDragEnter = (stageId) => {
    if (draggingItem) {
      setDropTarget(stageId);
    }
  };

  // Handle drag leave
  const handleDragLeave = (stageId) => {
    if (dropTarget === stageId) {
      setDropTarget(null);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className={`kanban-board-container ${className}`}>
        <div className="kanban-loading">
          <div className="loading-spinner" />
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`kanban-board-container ${className}`}>
      <div className="kanban-board">
        {stages.map((stage) => (
          <KanbanColumn
            key={stage.id}
            stage={stage}
            items={itemsByStage[stage.id] || []}
            onItemClick={onItemClick}
            onItemDragStart={handleItemDragStart}
            onItemDragEnd={handleItemDragEnd}
            onDrop={handleDrop}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            isDropTarget={dropTarget === stage.id}
            draggingItem={draggingItem}
            cardFields={cardFields}
          />
        ))}
      </div>
    </div>
  );
}

// ============================================
// DEFAULT STAGE CONFIGURATIONS
// ============================================

/**
 * Default deal stages matching Satoris Monday.com
 */
export const DEAL_STAGES = [
  { id: 'leads', label: 'Leads', color: '#ff6d3b' },
  { id: 'estimating', label: 'Estimating', color: '#fdab3d' },
  { id: 'submitted', label: 'Submitted', color: '#9cd326' },
  { id: 'won', label: 'Won', color: '#00c875' },
  { id: 'lost', label: 'Lost', color: '#df2f4a' },
  { id: 'declined', label: 'Declined', color: '#c4c4c4' },
];

/**
 * Alternative deal stages (prospects flow)
 */
export const DEAL_STAGES_ALT = [
  { id: 'prospects', label: 'Prospects', color: '#0086c0' },
  { id: 'preparing_proposal', label: 'Preparing Proposal', color: '#fdab3d' },
  { id: 'proposal_sent', label: 'Proposal Sent', color: '#9cd326' },
  { id: 'closed_won', label: 'Closed Won', color: '#00c875' },
  { id: 'lost', label: 'Lost', color: '#df2f4a' },
];

/**
 * Lead stages matching Satoris Monday.com
 */
export const LEAD_STAGES = [
  { id: 'new_leads', label: 'New Leads', color: '#ff6d3b' },
  { id: 'working_on_it', label: 'Working on it', color: '#fdab3d' },
  { id: 'prospect', label: 'Prospect', color: '#0086c0' },
  { id: 'unqualified', label: 'Unqualified', color: '#df2f4a' },
];

// ============================================
// EXPORTS
// ============================================

export { KanbanCard, KanbanColumn };

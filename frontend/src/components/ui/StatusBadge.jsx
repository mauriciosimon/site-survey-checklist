/**
 * StatusBadge Component
 * Renders colored pill/badge matching Monday.com/Satoris color scheme
 */

// ============================================
// COLOR MAPPINGS FROM SATORIS MONDAY.COM
// ============================================

// General status colors
const STATUS_COLORS = {
  // Success states - Green (#00c875)
  'won': '#00c875',
  'active': '#00c875',
  'done': '#00c875',
  'closed won': '#00c875',
  'approved': '#00c875',

  // Completed - Dark Green (#037f4c)
  'completed': '#037f4c',

  // Failure states - Red (#df2f4a)
  'lost': '#df2f4a',
  'unqualified': '#df2f4a',
  'churned': '#df2f4a',
  'rejected': '#df2f4a',
  'cancelled': '#df2f4a',

  // Working/In Progress - Orange (#fdab3d)
  'working on it': '#fdab3d',
  'in progress': '#fdab3d',
  'preparing proposal': '#fdab3d',

  // New/To Do - Dark Orange (#ff6d3b)
  'new': '#ff6d3b',
  'to do': '#ff6d3b',
  'new leads': '#ff6d3b',

  // Proposal Sent - Lime Green (#9cd326)
  'proposal sent': '#9cd326',
  'submitted': '#9cd326',

  // Pending - Yellow (#ffcb00)
  'pending': '#ffcb00',
  'waiting': '#ffcb00',
  'on review': '#ffcb00',

  // Prospect - Blue (#0086c0)
  'prospect': '#0086c0',
  'prospects': '#0086c0',
  'lead': '#0086c0',

  // Follow up - Purple (#a25ddc)
  'follow up': '#a25ddc',
  'needs follow up': '#a25ddc',

  // On Hold/Inactive - Gray (#c4c4c4)
  'on hold': '#c4c4c4',
  'inactive': '#c4c4c4',
  'paused': '#c4c4c4',
};

// Grade/Temperature colors (for pipeline prioritization)
const GRADE_COLORS = {
  'grade 1': '#ffadad',  // Hot - Pink
  'grade 2': '#fdab3d',  // Warm - Orange
  'grade 3': '#9cd326',  // Cold - Green
  'hot': '#ffadad',
  'warm': '#fdab3d',
  'cold': '#9cd326',
};

// Priority level colors
const PRIORITY_COLORS = {
  'critical': '#df2f4a',  // Red
  'high': '#fdab3d',      // Orange
  'medium': '#ffcb00',    // Yellow
  'low': '#0086c0',       // Blue
};

// Deal stage colors
const DEAL_STAGE_COLORS = {
  'leads': '#ff6d3b',           // Dark Orange
  'prospects': '#0086c0',       // Blue
  'estimating': '#fdab3d',      // Orange
  'preparing proposal': '#fdab3d', // Orange
  'submitted': '#9cd326',       // Lime Green
  'proposal sent': '#9cd326',   // Lime Green
  'won': '#00c875',             // Green
  'closed won': '#00c875',      // Green
  'lost': '#df2f4a',            // Red
  'declined': '#c4c4c4',        // Gray
  'completed': '#037f4c',       // Dark Green
};

// Lead status colors
const LEAD_STATUS_COLORS = {
  'new leads': '#ff6d3b',       // Dark Orange
  'working on it': '#fdab3d',   // Orange
  'prospect': '#0086c0',        // Blue
  'unqualified': '#df2f4a',     // Red
};

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get color for a status value
 * @param {string} type - Status type: 'status', 'grade', 'priority', 'deal_stage', 'lead_status'
 * @param {string} value - The status value
 * @returns {string} Hex color code
 */
export function getStatusColor(type, value) {
  if (!value) return '#c4c4c4';

  const normalizedValue = value.toLowerCase().trim();

  switch (type) {
    case 'grade':
      return GRADE_COLORS[normalizedValue] || '#c4c4c4';
    case 'priority':
      return PRIORITY_COLORS[normalizedValue] || '#c4c4c4';
    case 'deal_stage':
      return DEAL_STAGE_COLORS[normalizedValue] || STATUS_COLORS[normalizedValue] || '#c4c4c4';
    case 'lead_status':
      return LEAD_STATUS_COLORS[normalizedValue] || STATUS_COLORS[normalizedValue] || '#c4c4c4';
    case 'status':
    default:
      return STATUS_COLORS[normalizedValue] || '#c4c4c4';
  }
}

/**
 * Get color for a grade value (Grade 1, Grade 2, Grade 3 or Hot, Warm, Cold)
 * @param {string} grade - Grade value
 * @returns {string} Hex color code
 */
export function getGradeColor(grade) {
  if (!grade) return '#c4c4c4';
  return GRADE_COLORS[grade.toLowerCase().trim()] || '#c4c4c4';
}

/**
 * Get contrasting text color (white or black) based on background
 * @param {string} hexColor - Background hex color
 * @returns {string} 'white' or 'black'
 */
function getContrastColor(hexColor) {
  // Remove # if present
  const hex = hexColor.replace('#', '');

  // Convert to RGB
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);

  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  return luminance > 0.5 ? '#333333' : '#ffffff';
}

// ============================================
// STATUS BADGE COMPONENT
// ============================================

/**
 * StatusBadge Component
 *
 * Usage:
 * // With explicit color
 * <StatusBadge label="Won" color="#00c875" />
 *
 * // With auto-color based on type
 * <StatusBadge label="Won" type="status" />
 * <StatusBadge label="Grade 1" type="grade" />
 * <StatusBadge label="High" type="priority" />
 * <StatusBadge label="Prospects" type="deal_stage" />
 *
 * // With size
 * <StatusBadge label="Active" type="status" size="sm" />
 * <StatusBadge label="Active" type="status" size="md" />
 * <StatusBadge label="Active" type="status" size="lg" />
 */
export default function StatusBadge({
  label,
  color,
  type = 'status',
  size = 'md',
  className = ''
}) {
  if (!label) return null;

  // Get color: use explicit color or auto-detect from type
  const bgColor = color || getStatusColor(type, label);
  const textColor = getContrastColor(bgColor);

  const sizeClasses = {
    sm: 'status-badge-sm',
    md: 'status-badge-md',
    lg: 'status-badge-lg',
  };

  return (
    <span
      className={`status-badge ${sizeClasses[size] || 'status-badge-md'} ${className}`}
      style={{
        backgroundColor: bgColor,
        color: textColor,
      }}
    >
      {label}
    </span>
  );
}

// ============================================
// EXPORTS
// ============================================

// Export color maps for external use
export const colorMaps = {
  STATUS_COLORS,
  GRADE_COLORS,
  PRIORITY_COLORS,
  DEAL_STAGE_COLORS,
  LEAD_STATUS_COLORS,
};

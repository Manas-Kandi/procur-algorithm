ProcureAI Design System
Version 1.0 | Last Updated: 2025-01-20

Philosophy & Principles
Design Values

Clarity over cleverness: Every element should have obvious purpose
Data density without clutter: Show maximum information with minimum chrome
Trust through transparency: Make system state and AI reasoning visible
Speed as a feature: Optimize for task completion velocity

Visual Language

Sharp, not soft: Straight edges, minimal rounding (2px max for interactive elements)
Depth through hierarchy, not shadows: Use color, weight, and spacing for depth
Whitespace is structural: Padding creates rhythm and scanability
Typography does the heavy lifting: Font weight and size establish importance


Foundation
Color System
Base Palette
--color-background-primary: #FAFAFA    // Main canvas
--color-background-secondary: #F4F4F5  // Cards, panels
--color-background-tertiary: #E4E4E7   // Disabled, inactive states

--color-surface-raised: #FFFFFF        // Elevated cards
--color-surface-sunken: #FAFAFA        // Input fields, wells

--color-border-subtle: #E4E4E7         // Default borders (barely visible)
--color-border-medium: #D4D4D8         // Hover states
--color-border-strong: #A1A1AA         // Focus, active states
Text Hierarchy
--color-text-primary: #18181B          // Headings, key data
--color-text-secondary: #52525B        // Body text, labels
--color-text-tertiary: #A1A1AA         // Metadata, timestamps
--color-text-disabled: #D4D4D8         // Disabled text
--color-text-inverse: #FAFAFA          // Text on dark backgrounds
Semantic Colors
--color-brand-primary: #2563EB         // Primary actions, links
--color-brand-hover: #1D4ED8           // Hover state
--color-brand-active: #1E40AF          // Active/pressed state

--color-success: #16A34A               // Approvals, wins, completions
--color-success-bg: #F0FDF4            // Success background tint

--color-warning: #EA580C               // Alerts, expiring, at-risk
--color-warning-bg: #FFF7ED            // Warning background tint

--color-danger: #DC2626                // Rejections, violations, errors
--color-danger-bg: #FEF2F2             // Danger background tint

--color-info: #0891B2                  // Informational, neutral updates
--color-info-bg: #ECFEFF               // Info background tint
AI/Agent Colors (distinct from user actions)
--color-ai-primary: #7C3AED            // AI actions, suggestions
--color-ai-bg: #F5F3FF                 // AI reasoning boxes
--color-ai-accent: #A78BFA             // AI activity indicators
Data Visualization (for charts, graphs)
--color-viz-1: #2563EB                 // Primary series
--color-viz-2: #16A34A                 // Secondary series
--color-viz-3: #EA580C                 // Tertiary series
--color-viz-4: #7C3AED                 // Quaternary series
--color-viz-5: #0891B2                 // Quinary series
--color-viz-6: #DC2626                 // Senary series
Typography
Font Stack
css--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             'Roboto', 'Helvetica Neue', Arial, sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code', 
             'Roboto Mono', Consolas, monospace;
Type Scale
--text-xs:   0.75rem   // 12px - Metadata, table headers
--text-sm:   0.875rem  // 14px - Body text, labels
--text-base: 1rem      // 16px - Default paragraph
--text-lg:   1.125rem  // 18px - Subheadings
--text-xl:   1.25rem   // 20px - Card titles
--text-2xl:  1.5rem    // 24px - Section headings
--text-3xl:  1.875rem  // 30px - Page titles
--text-4xl:  2.25rem   // 36px - Dashboard metrics
Font Weights
--font-normal:   400   // Body text
--font-medium:   500   // Subtle emphasis, labels
--font-semibold: 600   // Headings, key data
--font-bold:     700   // Metrics, critical information
Line Heights
--leading-tight:  1.25  // Large headings, metrics
--leading-snug:   1.375 // Subheadings
--leading-normal: 1.5   // Body text
--leading-relaxed: 1.625 // Long-form content
Spacing System
Base Unit: 4px (0.25rem)
--space-0:   0px      // 0
--space-1:   4px      // 0.25rem
--space-2:   8px      // 0.5rem
--space-3:   12px     // 0.75rem
--space-4:   16px     // 1rem      ← Default element padding
--space-5:   20px     // 1.25rem
--space-6:   24px     // 1.5rem    ← Card padding
--space-8:   32px     // 2rem      ← Section spacing
--space-10:  40px     // 2.5rem
--space-12:  48px     // 3rem      ← Large section breaks
--space-16:  64px     // 4rem
--space-20:  80px     // 5rem
--space-24:  96px     // 6rem
Application Rules:

Inline spacing (between related elements): 8-12px
Block spacing (between unrelated elements): 16-24px
Section spacing (between major sections): 32-48px
Element padding: Minimum 16px, standard 24px
Page margins: 32px minimum on desktop, 16px on mobile

Elevation & Shadows
Minimal shadow approach - use sparingly, only for true elevation:
css--shadow-none: none;

--shadow-subtle: 0 1px 2px rgba(0, 0, 0, 0.04);
/* Use for: Slightly raised cards on white background */

--shadow-low: 0 1px 3px rgba(0, 0, 0, 0.06), 
              0 1px 2px rgba(0, 0, 0, 0.04);
/* Use for: Elevated cards, dropdown triggers */

--shadow-medium: 0 4px 6px rgba(0, 0, 0, 0.05), 
                 0 2px 4px rgba(0, 0, 0, 0.04);
/* Use for: Modals, popovers, floating panels */

--shadow-high: 0 10px 15px rgba(0, 0, 0, 0.08), 
               0 4px 6px rgba(0, 0, 0, 0.04);
/* Use for: Critical alerts, command palettes */
Border-first elevation: Prefer border: 1px solid var(--color-border-subtle) over shadows for most cards.
Border Radius
Minimal rounding - sharp edges with subtle softening:
--radius-none: 0px         // Tables, strict layouts
--radius-sm:   2px         // Buttons, inputs, tags
--radius-md:   4px         // Cards, panels (rare)
--radius-lg:   6px         // Modals (rare)
--radius-full: 9999px      // Avatar badges, status dots only
Default: --radius-sm (2px) for interactive elements. Use --radius-none (0px) for data tables and strict layouts.

Components
Buttons
Variants
css/* Primary Button - main actions */
.button-primary {
  background: var(--color-brand-primary);
  color: var(--color-text-inverse);
  border: none;
  padding: 10px 20px;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 150ms ease;
}
.button-primary:hover {
  background: var(--color-brand-hover);
}
.button-primary:active {
  background: var(--color-brand-active);
}

/* Secondary Button - alternative actions */
.button-secondary {
  background: var(--color-surface-raised);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-medium);
  padding: 10px 20px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  border-radius: var(--radius-sm);
  cursor: pointer;
}
.button-secondary:hover {
  border-color: var(--color-border-strong);
  background: var(--color-background-secondary);
}

/* Ghost Button - tertiary actions */
.button-ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border: none;
  padding: 10px 20px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  border-radius: var(--radius-sm);
  cursor: pointer;
}
.button-ghost:hover {
  background: var(--color-background-secondary);
  color: var(--color-text-primary);
}

/* Danger Button - destructive actions */
.button-danger {
  background: var(--color-danger);
  color: var(--color-text-inverse);
  border: none;
  padding: 10px 20px;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  border-radius: var(--radius-sm);
}
Sizes

Small: padding: 6px 12px; font-size: var(--text-xs);
Medium (default): padding: 10px 20px; font-size: var(--text-sm);
Large: padding: 12px 24px; font-size: var(--text-base);

Icon Buttons: Square aspect ratio, center icon, size 36x36px (medium).
Loading State: Replace text with spinner (same color), disable pointer events.
Disabled State: opacity: 0.5; cursor: not-allowed; pointer-events: none;
Input Fields
Text Input
css.input {
  background: var(--color-surface-sunken);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  width: 100%;
  transition: border-color 150ms ease;
}
.input:hover {
  border-color: var(--color-border-medium);
}
.input:focus {
  outline: none;
  border-color: var(--color-brand-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
.input::placeholder {
  color: var(--color-text-tertiary);
}
Input Label
css.input-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
}
Input Helper Text
css.input-helper {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--space-1);
}
Input Error State
css.input-error {
  border-color: var(--color-danger);
}
.input-error:focus {
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}
.input-error-message {
  font-size: var(--text-xs);
  color: var(--color-danger);
  margin-top: var(--space-1);
}
Search Input: Add icon prefix (magnifying glass), padding-left: 36px to accommodate icon.
Dropdowns
Select Component
css.select {
  background: var(--color-surface-sunken);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  padding: 10px 36px 10px 12px; /* Extra right padding for chevron */
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  appearance: none; /* Hide native arrow */
  background-image: url('data:image/svg+xml;utf8,<svg>...</svg>'); /* Custom chevron */
  background-position: right 12px center;
  background-repeat: no-repeat;
}
Dropdown Menu (for custom dropdowns):
css.dropdown-menu {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-medium);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-medium);
  padding: var(--space-1) 0;
  min-width: 200px;
  max-height: 320px;
  overflow-y: auto;
}

.dropdown-item {
  padding: 8px 12px;
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background 100ms ease;
}
.dropdown-item:hover {
  background: var(--color-background-secondary);
}
.dropdown-item-active {
  background: var(--color-brand-primary);
  color: var(--color-text-inverse);
}
Multi-select: Show selected items as removable tags below the input.
Cards
Standard Card
css.card {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  padding: var(--space-6);
}

.card-hover {
  transition: border-color 150ms ease;
  cursor: pointer;
}
.card-hover:hover {
  border-color: var(--color-border-medium);
}
Card Header
css.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border-subtle);
}

.card-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}
Card with Status Banner (for negotiations, deals):
css.card-status-banner {
  height: 4px;
  border-top-left-radius: var(--radius-sm);
  border-top-right-radius: var(--radius-sm);
  background: var(--color-success); /* or warning/danger based on state */
}
Metric Card (for dashboard):
css.metric-card {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  padding: var(--space-6);
}

.metric-value {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  line-height: var(--leading-tight);
}

.metric-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  margin-top: var(--space-2);
}

.metric-change {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-top: var(--space-2);
}
.metric-change-positive {
  color: var(--color-success);
}
.metric-change-negative {
  color: var(--color-danger);
}
Tables
Table Structure
css.table-container {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-none); /* Sharp edges for data */
  overflow: hidden;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.table-header {
  background: var(--color-background-secondary);
  border-bottom: 1px solid var(--color-border-medium);
}

.table-header-cell {
  padding: 12px 16px;
  text-align: left;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table-row {
  border-bottom: 1px solid var(--color-border-subtle);
  transition: background 100ms ease;
}
.table-row:hover {
  background: var(--color-background-secondary);
}

.table-cell {
  padding: 16px;
  color: var(--color-text-primary);
  vertical-align: middle;
}

.table-cell-numeric {
  text-align: right;
  font-variant-numeric: tabular-nums; /* Align numbers properly */
}
Sortable Column Headers: Add chevron icon (up/down) on hover, highlight active sort column.
Row Actions: Show action buttons (edit, delete, etc.) on row hover, aligned right.
Empty State: Center message with icon, suggestion for action.
Badges & Tags
Status Badge
css.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-success {
  background: var(--color-success-bg);
  color: var(--color-success);
}
.badge-warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}
.badge-danger {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}
.badge-info {
  background: var(--color-info-bg);
  color: var(--color-info);
}
.badge-neutral {
  background: var(--color-background-tertiary);
  color: var(--color-text-secondary);
}
Tag (removable):
css.tag {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 6px 10px;
  background: var(--color-background-secondary);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

.tag-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: var(--radius-full);
  background: transparent;
  cursor: pointer;
  transition: background 100ms ease;
}
.tag-remove:hover {
  background: var(--color-border-medium);
}
Modals & Dialogs
Modal Overlay
css.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 200ms ease;
}

.modal {
  background: var(--color-surface-raised);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-high);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  animation: scaleIn 200ms ease;
}

.modal-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border-subtle);
}

.modal-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--space-6);
}

.modal-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--color-border-subtle);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}
Confirmation Dialog (for destructive actions):

Title clearly states action
Body explains consequences
Danger button for confirm, secondary for cancel
Optional: Require typing confirmation text for critical actions

Alerts & Notifications
Alert Banner (inline, contextual):
css.alert {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 1px solid;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}

.alert-success {
  background: var(--color-success-bg);
  border-color: var(--color-success);
  color: var(--color-success);
}
.alert-warning {
  background: var(--color-warning-bg);
  border-color: var(--color-warning);
  color: var(--color-warning);
}
.alert-danger {
  background: var(--color-danger-bg);
  border-color: var(--color-danger);
  color: var(--color-danger);
}
.alert-info {
  background: var(--color-info-bg);
  border-color: var(--color-info);
  color: var(--color-info);
}
Toast Notification (floating, temporary):
css.toast {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  min-width: 320px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-medium);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-medium);
  padding: var(--space-4);
  animation: slideInRight 300ms ease;
  z-index: 2000;
}
Duration: Success/Info = 4s, Warning = 6s, Error = 8s (or until dismissed).
Progress Indicators
Progress Bar
css.progress-bar-container {
  width: 100%;
  height: 8px;
  background: var(--color-background-tertiary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--color-brand-primary);
  transition: width 300ms ease;
}
Spinner (loading indicator):
css.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border-subtle);
  border-top-color: var(--color-brand-primary);
  border-radius: var(--radius-full);
  animation: spin 600ms linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
Skeleton Loader (for content loading):
css.skeleton {
  background: var(--color-background-tertiary);
  border-radius: var(--radius-sm);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
Navigation
Top Navigation Bar
css.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 var(--space-6);
  background: var(--color-surface-raised);
  border-bottom: 1px solid var(--color-border-subtle);
}

.navbar-brand {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
}

.navbar-nav {
  display: flex;
  gap: var(--space-6);
}

.navbar-item {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  transition: all 150ms ease;
}
.navbar-item:hover {
  color: var(--color-text-primary);
  background: var(--color-background-secondary);
}
.navbar-item-active {
  color: var(--color-brand-primary);
  background: var(--color-brand-primary);
  background: rgba(37, 99, 235, 0.1);
}
Sidebar Navigation
css.sidebar {
  width: 240px;
  height: 100vh;
  background: var(--color-surface-raised);
  border-right: 1px solid var(--color-border-subtle);
  padding: var(--space-6);
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: var(--space-6);
}

.sidebar-label {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 10px 12px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  transition: all 150ms ease;
  cursor: pointer;
}
.sidebar-item:hover {
  color: var(--color-text-primary);
  background: var(--color-background-secondary);
}
.sidebar-item-active {
  color: var(--color-brand-primary);
  background: rgba(37, 99, 235, 0.1);
}
Breadcrumbs
css.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-4);
}

.breadcrumb-separator {
  color: var(--color-text-tertiary);
}

.breadcrumb-link {
  color: var(--color-text-secondary);
  transition: color 150ms ease;
}
.breadcrumb-link:hover {
  color: var(--color-brand-primary);
}

.breadcrumb-current {
  color: var(--color-text-primary);
  font-weight: var(--font-medium);
}
Tabs
css.tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border-subtle);
  margin-bottom: var(--space-6);
}

.tab {
  padding: 12px 20px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 150ms ease;
}
.tab:hover {
  color: var(--color-text-primary);
}
.tab-active {
  color: var(--color-brand-primary);
  border-bottom-color: var(--color-brand-primary);
}
Forms
Form Group (label + input + helper):
css.form-group {
  margin-bottom: var(--space-6);
}
Form Row (multiple inputs side-by-side):
css.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
}
Checkbox & Radio
css.checkbox-wrapper,
.radio-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.checkbox,
.radio {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border-medium);
  border-radius: var(--radius-sm); /* checkbox */
  /* border-radius: var(--radius-full); for radio */
  appearance: none;
  cursor: pointer;
  transition: all 150ms ease;
}

.checkbox:checked,
.radio:checked {
  background: var(--color-brand-primary);
  border-color: var(--color-brand-primary);
  /* Add checkmark icon via background-image */
}

.checkbox-label,
.radio-label {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  cursor: pointer;
}
Toggle Switch
css.toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--color-border-strong);
  border-radius: 24px;
  transition: background 200ms ease;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 2px;
  bottom: 2px;
  background: white;
  border-radius: 50%;
  transition: transform 200ms ease;
}

.toggle-input:checked + .toggle-slider {
  background: var(--color-brand-primary);
}

.toggle-input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

Iconography
Icon System
Icon Library: Use Lucide Icons or Heroicons for consistency.
Icon Sizes
--icon-xs:  14px  // Inline with small text
--icon-sm:  16px  // Default inline icon
--icon-md:  20px  // Button icons, navigation
--icon-lg:  24px  // Section headers
--icon-xl:  32px  // Empty states, illustrations
Icon Colors: Icons inherit text color by default. Use semantic colors for status icons:

Success: --color-success
Warning: --color-warning
Danger: --color-danger
Info: --color-info
AI actions: --color-ai-primary

Icon Stroke Width: Use 2px stroke weight for consistency with sharp edge aesthetic.
Common Icons & Usage
Check circle      → Approvals, success states
X circle          → Rejections, errors
Alert triangle    → Warnings, caution
Info circle       → Information, help text
Sparkles          → AI-generated content, suggestions
Zap               → Quick actions, automations
Clock             → Time-related, pending states
Users             → Team, stakeholders
Building          → Vendors, companies
Dollar sign       → Pricing, budget
File text         → Documents, contracts
Trending up/down  → Metrics, changes
Filter            → Filtering controls
Search            → Search functionality
Settings          → Configuration, preferences
Bell              → Notifications
ChevronDown       → Dropdowns, expandable sections
External link     → Links to external resources

Dashboard Elements
Metric Cards
Structure
html<div class="metric-card">
  <div class="metric-value">$2.4M</div>
  <div class="metric-label">Active Pipeline</div>
  <div class="metric-change metric-change-positive">
    ↑ 12% from last month
  </div>
</div>
Layout Pattern: 4-column grid on desktop, 2-column on tablet, 1-column on mobile.
Status Timeline
css.timeline {
  position: relative;
  padding-left: var(--space-8);
}

.timeline-item {
  position: relative;
  padding-bottom: var(--space-6);
}

.timeline-item:before {
  content: '';
  position: absolute;
  left: -24px;
  top: 0;
  width: 2px;
  height: 100%;
  background: var(--color-border-subtle);
}

.timeline-dot {
  position: absolute;
  left: -30px;
  top: 2px;
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  border: 2px solid var(--color-brand-primary);
  background: white;
}

.timeline-content {
  font-size: var(--text-sm);
}

.timeline-timestamp {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--space-1);
}
Comparison Table
css.comparison-table {
  display: grid;
  grid-template-columns: 200px repeat(3, 1fr);
  gap: 1px;
  background: var(--color-border-subtle);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.comparison-header,
.comparison-cell {
  background: white;
  padding: var(--space-4);
}

.comparison-header {
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
  background: var(--color-background-secondary);
}

.comparison-row-label {
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

.comparison-cell-highlight {
  background: var(--color-success-bg);
  color: var(--color-success);
  font-weight: var(--font-semibold);
}
Activity Feed
css.activity-feed {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.activity-item {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
}

.activity-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  background: var(--color-background-secondary);
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.activity-description {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.activity-timestamp {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--space-2);
}
Kanban Board
css.kanban-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-4);
  overflow-x: auto;
}

.kanban-column {
  background: var(--color-background-secondary);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  min-height: 400px;
}

.kanban-column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.kanban-column-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.kanban-column-count {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  background: var(--color-surface-raised);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.kanban-card {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  padding: var(--space-3);
  margin-bottom: var(--space-3);
  cursor: pointer;
  transition: border-color 150ms ease;
}
.kanban-card:hover {
  border-color: var(--color-border-medium);
}

AI-Specific Components
AI Reasoning Box
css.ai-reasoning {
  background: var(--color-ai-bg);
  border-left: 3px solid var(--color-ai-primary);
  padding: var(--space-4);
  border-radius: var(--radius-sm);
  margin: var(--space-4) 0;
}

.ai-reasoning-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.ai-reasoning-icon {
  color: var(--color-ai-primary);
}

.ai-reasoning-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-ai-primary);
}

.ai-reasoning-content {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
}
Negotiation Transcript
css.negotiation-transcript {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.negotiation-round {
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.negotiation-round-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--color-background-secondary);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
}

.negotiation-round-content {
  padding: var(--space-4);
}

.negotiation-message {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.negotiation-message:last-child {
  margin-bottom: 0;
}

.negotiation-message-buyer {
  flex-direction: row-reverse;
}

.negotiation-message-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--color-brand-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.negotiation-message-seller .negotiation-message-avatar {
  background: var(--color-border-strong);
}

.negotiation-message-content {
  flex: 1;
  background: var(--color-background-secondary);
  padding: var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}
AI Activity Indicator
css.ai-activity {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 6px 12px;
  background: var(--color-ai-bg);
  border: 1px solid var(--color-ai-primary);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--color-ai-primary);
}

.ai-activity-pulse {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--color-ai-primary);
  animation: pulse 2s ease-in-out infinite;
}

Data Visualization
Chart Container
css.chart-container {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  padding: var(--space-6);
}

.chart-header {
  margin-bottom: var(--space-6);
}

.chart-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.chart-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
Chart Legend
css.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-top: var(--space-4);
}

.chart-legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
}

.chart-legend-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-sm);
}
Sparkline
css.sparkline {
  height: 32px;
  width: 100px;
}
/* Use inline SVG or canvas for rendering */
Progress Ring
css.progress-ring {
  position: relative;
  width: 120px;
  height: 120px;
}

.progress-ring-value {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
}
/* Use SVG circle with stroke-dasharray for ring */

Responsive Design
Breakpoints
css--breakpoint-sm:  640px   /* Mobile landscape */
--breakpoint-md:  768px   /* Tablet */
--breakpoint-lg:  1024px  /* Desktop */
--breakpoint-xl:  1280px  /* Large desktop */
--breakpoint-2xl: 1536px  /* Extra large */
Mobile-First Approach
Start with mobile layout, progressively enhance for larger screens:
css/* Mobile first */
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}

/* Tablet and up */
@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
Touch Targets
Minimum touch target size: 44x44px for mobile (iOS HIG standard).
For desktop: 36x36px minimum.
Mobile Navigation
Convert sidebar to bottom tab bar on mobile:
css@media (max-width: 767px) {
  .sidebar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: auto;
    flex-direction: row;
    border-right: none;
    border-top: 1px solid var(--color-border-subtle);
    padding: var(--space-2);
  }
}

Accessibility
Focus States
Always visible focus indicators:
css*:focus {
  outline: 2px solid var(--color-brand-primary);
  outline-offset: 2px;
}

/* For elements with background, use inset ring */
.button:focus,
.input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
}
Skip Links
css.skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  padding: var(--space-3);
  background: var(--color-brand-primary);
  color: white;
  text-decoration: none;
  z-index: 9999;
}

.skip-link:focus {
  left: 0;
}
ARIA Labels

Add aria-label to icon-only buttons
Use aria-describedby for form field hints
Add aria-live="polite" to toast notifications
Use role="status" for loading states
Add aria-expanded to collapsible sections

Color Contrast
Minimum ratios (WCAG AA):

Normal text: 4.5:1
Large text (18px+): 3:1
UI components: 3:1

Test all color combinations with contrast checker.
Reduced Motion
css@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

Animation
Timing Functions
css--ease-in:     cubic-bezier(0.4, 0, 1, 1);
--ease-out:    cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
Duration Scale
--duration-fast:   150ms  /* Hover states, toggles */
--duration-base:   200ms  /* Default transitions */
--duration-medium: 300ms  /* Modals, dropdowns */
--duration-slow:   500ms  /* Complex animations */
Common Animations
css@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
Animation Guidelines:

Avoid animations >500ms
Use opacity + transform (GPU-accelerated)
Never animate: width, height, top, left (causes reflow)
Provide reduced motion alternatives


Layout Patterns
Page Container
css.page-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6);
}

@media (max-width: 767px) {
  .page-container {
    padding: var(--space-4);
  }
}
Two-Column Layout
css.two-column-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: var(--space-6);
  min-height: 100vh;
}

@media (max-width: 1023px) {
  .two-column-layout {
    grid-template-columns: 1fr;
  }
}
Dashboard Grid
css.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-6);
}
Split View
css.split-view {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 1px;
  background: var(--color-border-subtle);
  height: calc(100vh - 64px);
}

.split-view-sidebar,
.split-view-main {
  background: white;
  overflow-y: auto;
}

Data States
Empty State
css.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
}

.empty-state-icon {
  width: 64px;
  height: 64px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-4);
}

.empty-state-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.empty-state-description {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  max-width: 400px;
  margin-bottom: var(--space-6);
}
Error State
css.error-state {
  background: var(--color-danger-bg);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-sm);
  padding: var(--space-6);
  text-align: center;
}

.error-state-icon {
  color: var(--color-danger);
  margin-bottom: var(--space-3);
}

.error-state-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-danger);
  margin-bottom: var(--space-2);
}
Loading State
css.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
}

.loading-spinner {
  margin-bottom: var(--space-4);
}

.loading-text {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

Implementation Guidelines
CSS Architecture
Use BEM naming for clarity:
.block {}
.block__element {}
.block--modifier {}
Example:
css.card {}
.card__header {}
.card__title {}
.card--highlighted {}
CSS Custom Properties Usage
Define at :root, override in contexts:
css:root {
  --card-padding: var(--space-6);
}

.card--compact {
  --card-padding: var(--space-4);
}

.card {
  padding: var(--card-padding);
}
Component Composition
Build complex components from primitives:
html<!-- Good: Composed from design system -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Negotiation Status</h3>
    <span class="badge badge-success">Active</span>
  </div>
  <div class="card-body">
    ...
  </div>
</div>

<!-- Bad: One-off custom styling -->
<div style="background: #fff; padding: 20px; border: 1px solid #ccc;">
  ...
</div>
Dark Mode Preparation
Structure tokens for future dark mode:
css:root {
  --color-bg-primary: #FAFAFA;
  --color-surface: #FFFFFF;
}

[data-theme="dark"] {
  --color-bg-primary: #18181B;
  --color-surface: #27272A;
}

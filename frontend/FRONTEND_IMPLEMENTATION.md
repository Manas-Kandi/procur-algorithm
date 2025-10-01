# ProcurAI Frontend Implementation

## Overview
Comprehensive React + TypeScript frontend implementing the dual-sided marketplace UX architecture for ProcurAI's AI-powered procurement platform.

## Technology Stack
- **Framework**: React 18 + TypeScript
- **Routing**: React Router v6
- **State Management**: Zustand (auth) + TanStack Query (server state)
- **Styling**: Tailwind CSS (via tokens)
- **Build Tool**: Vite
- **API Client**: Axios

## Architecture

### Core Structure
```
src/
├── components/
│   ├── layout/
│   │   └── Navigation.tsx          # Role-based navigation sidebar
│   └── shared/
│       ├── Button.tsx               # Primary UI button component
│       ├── Card.tsx                 # Container component
│       ├── MetricCard.tsx           # Dashboard metric display
│       ├── StatusBadge.tsx          # Request status indicators
│       └── AIExplainer.tsx          # "Why?" transparency component
├── pages/
│   ├── auth/
│   │   └── Login.tsx                # Authentication page
│   ├── buyer/
│   │   ├── Dashboard.tsx            # Buyer home with Kanban board
│   │   ├── NewRequest.tsx           # 5-step request creation wizard
│   │   ├── NegotiationTheater.tsx   # Live negotiation viewer
│   │   ├── ApprovalWorkspace.tsx    # One-screen approval interface
│   │   └── Portfolio.tsx            # Subscription management
│   └── seller/
│       └── SellerDashboard.tsx      # Seller pipeline overview
├── services/
│   └── api.ts                       # API client with interceptors
├── store/
│   └── auth.ts                      # Authentication state (Zustand)
├── types/
│   └── index.ts                     # TypeScript type definitions
└── routes/
    └── index.tsx                    # Route configuration
```

## Implemented Features

### ✅ Buyer Flows

#### 1. Dashboard (`/`)
- **Top Metrics**: Active requests, pending approvals, renewals, monthly spend
- **Kanban Board**: Visual pipeline (Draft → Sourcing → Negotiating → Approving → Contracted)
- **Smart Alerts**: Renewal warnings with savings opportunities
- **Role-based**: Shows different views for buyer/approver/admin

#### 2. New Request Flow (`/requests/new`)
**5-Step Wizard**:
1. **Budget Context**: Multiple input options (exact, range, see pricing, need approval)
2. **What & How Many**: Natural language description + type + quantity
3. **Requirements**: Must-have features + compliance requirements (SOC2, HIPAA, etc.)
4. **Policy Preview**: Shows approval chain and estimated timeline based on spend
5. **Confirm**: Review and submit

**Key Features**:
- Progress indicator with step navigation
- Pre-populated compliance toggles
- Budget-driven approval routing preview
- Clean, wizard-style UX

#### 3. Negotiation Theater (`/requests/:requestId/negotiate`)
**Three Sections**:
- **Top Offers**: Card view of best 3 vendors with utility scores
- **Live Feed**: Chronological negotiation transcript by vendor
- **Control Panel**: Budget adjustment, add requirements, stop/accept actions

**AI Transparency**:
- "Why this offer?" explainer on each vendor card
- "Why this move?" on each negotiation message
- Shows AI reasoning with score components

#### 4. Approval Workspace (`/approvals`)
**Single-Screen Decision View**:
- **Left Panel**: Offer summary, TCO breakdown, AI recommendation
- **Right Panel**: Risk/compliance status with traffic lights
- **Actions**: Approve, Request Changes, Reject, Escalate
- **Audit Trail**: Required comment field for decisions

**Compliance Indicators**:
- SOC2, ISO, GDPR, SLA, Security review
- Color-coded (green/amber/red) with details

#### 5. Portfolio Management (`/portfolio`)
**Features**:
- Subscription table with utilization bars
- Filters: All, Upcoming Renewals, Underutilized
- Bulk actions: Flag for renegotiation, request cancellation
- Renewal cards with AI recommendations
- Cost savings calculations

### ✅ Seller Flows

#### 1. Seller Dashboard (`/seller`)
- **Metrics**: Pipeline value, active deals, win rate, avg deal size
- **AI Activity Feed**: Real-time negotiation status by buyer
- **Deals at Risk**: Stalled negotiations requiring attention
- **Quick Actions**: Configure guardrails, view analytics, team performance

### ✅ Shared Components

#### AI Explainer
```tsx
<AIExplainer
  title="this offer was recommended"
  reasoning={[
    { label: 'Price vs Budget', value: '85% of ceiling' },
    { label: 'Feature Match', value: '95%' },
    { label: 'Risk Level', value: 'Low' },
  ]}
/>
```
- Expandable popup on click
- Used throughout for transparency
- Shows AI reasoning behind decisions

#### Status Badge
- Color-coded by request status
- Consistent across all views
- Maps to backend status enum

#### Metric Card
- Displays KPIs with trends
- Optional click action
- Icon support
- Trend indicators (↑ ↓ →)

## API Integration

### Client Configuration
```typescript
// Base URL from environment
VITE_API_BASE_URL=http://localhost:8000

// Automatic token injection
// 401 handling with redirect to login
// Error handling with user feedback
```

### Key Endpoints Used
- `POST /auth/login` - Authentication
- `GET /requests` - List requests
- `POST /requests` - Create request
- `GET /negotiations/:id` - Get negotiation session
- `POST /negotiations/start` - Start negotiations
- `GET /dashboard/metrics` - Dashboard data
- `GET /dashboard/renewals` - Upcoming renewals
- `POST /contracts/:id/approve` - Approve contract

## State Management

### Authentication (Zustand)
```typescript
useAuthStore()
  .user       // Current user object
  .token      // JWT token
  .isAuthenticated
  .login()    // Save token + user
  .logout()   // Clear state
```

### Server State (TanStack Query)
- Automatic caching (5 min stale time)
- Optimistic updates
- Background refetching
- Error handling
- Loading states

## Routing & Protection

### Protected Routes
All authenticated routes wrapped with `<ProtectedRoute>`:
- Redirects to `/login` if not authenticated
- Wraps pages in `<AuthenticatedLayout>` with navigation

### Role-Based Navigation
Navigation sidebar filters items by user role:
- **Buyer**: Dashboard, New Request, Requests, Approvals, Portfolio
- **Seller**: Dashboard, Negotiations, Guardrails, Analytics
- **Admin**: All routes

## Design System Alignment

### Colors
- Primary: Blue (#1D4ED8)
- Success: Green (#16A34A)
- Warning: Amber (#F59E0B)
- Danger: Red (#DC2626)
- Buyer Accent: Teal (#0F766E)
- Seller Accent: Orange (#F97316)

### Typography
- Font: Inter (system fallbacks)
- Sizes: Consistent scale (12-48px)
- Monospace for numbers (IBM Plex Mono)

### Spacing
- Consistent 8px grid system
- Responsive padding/margins
- Gap utilities for flex/grid

## Mobile Considerations

### Approval Workspace
- Optimized for mobile approvals
- Single-screen layout adapts to small screens
- Touch-friendly buttons
- Readable text sizes

### Dashboard
- Responsive grid (1 col mobile, 4 col desktop)
- Cards stack vertically on mobile
- Navigation collapses on small screens

## Next Steps for Full Implementation

### High Priority
1. **Seller Negotiation Control**
   - Guardrail configuration UI
   - Live deal room per negotiation
   - Manual intervention controls
   - Price override approvals

2. **Real-Time Updates**
   - WebSocket connection for live negotiation feed
   - Polling fallback for compatibility
   - Optimistic UI updates

3. **Request Detail Page**
   - Full request view with history
   - Vendor shortlist display
   - Negotiation progress tracking

4. **Analytics Pages**
   - Buyer spend analytics
   - Seller win/loss analysis
   - Performance trends

### Medium Priority
5. **Vendor Search**
   - Browse vendor catalog
   - Filter by capabilities
   - Compliance filtering

6. **Contract Management**
   - Contract viewer
   - E-signature integration
   - Document download

7. **Settings Pages**
   - User profile
   - Organization settings
   - Policy configuration

8. **Notifications**
   - In-app notification center
   - Email preferences
   - Real-time alerts

### Low Priority
9. **Dark Mode**
   - Theme toggle
   - Persistent preference
   - System preference detection

10. **Advanced Filters**
    - Saved filter presets
    - Complex query builder
    - Export functionality

## Running the Frontend

### Development
```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:5173
```

### Environment Variables
```bash
cp .env.example .env
# Edit VITE_API_BASE_URL if needed
```

### Build for Production
```bash
npm run build
# Outputs to dist/
```

## Integration with Backend

### Prerequisites
1. Backend API running on `http://localhost:8000`
2. Database migrations applied
3. Auth endpoints functional
4. CORS configured for frontend origin

### Test User Setup
Create test users via backend:
```bash
# Buyer user
POST /auth/register
{
  "email": "buyer@test.com",
  "password": "test123",
  "username": "test_buyer",
  "role": "buyer"
}

# Seller user
POST /auth/register
{
  "email": "seller@test.com",
  "password": "test123",
  "username": "test_seller",
  "role": "seller"
}
```

## Key UX Principles Implemented

1. **Transparency by Default**: Every AI decision has a "Why?" explainer
2. **Guided Autonomy**: AI handles work, but humans can override with one click
3. **Progressive Disclosure**: Summary → Detail drill-down pattern throughout
4. **Status over Stages**: Kanban shows current state, not abstract workflow
5. **Mobile-Friendly Approvals**: Critical decisions work well on phones

## Performance Optimizations

- Code splitting by route
- Lazy loading for heavy components
- Memoized calculations
- Debounced search inputs
- Virtual scrolling for large lists (TODO)
- Image lazy loading (when images added)

## Accessibility

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus management in modals
- Color contrast compliance (WCAG AA)
- Screen reader friendly labels

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Known Limitations

1. No WebSocket support yet (polling needed for real-time)
2. Mock data in some components (pending API completion)
3. No offline support
4. No PWA capabilities
5. Limited error boundary implementation
6. No A/B testing framework

## Testing TODO

- Unit tests for components (Vitest + React Testing Library)
- Integration tests for user flows
- E2E tests (Playwright)
- Visual regression tests
- Accessibility audits
- Performance benchmarks

---

**Status**: Core buyer and seller flows implemented. Ready for backend integration and user testing.

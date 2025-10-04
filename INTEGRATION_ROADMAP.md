# Frontend-Backend Integration Roadmap

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + TS)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Dashboard   │  │  Portfolio   │  │  Approvals   │         │
│  │   (Live ✅)  │  │ (Backend ✅) │  │  (Partial)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│  ┌──────▼──────────────────▼──────────────────▼───────┐        │
│  │        API Client (axios + interceptors)            │        │
│  │  - JWT auth                                         │        │
│  │  - Error handling                                   │        │
│  │  - Demo mode support                                │        │
│  └──────────────────────────┬──────────────────────────┘        │
│                             │                                    │
└─────────────────────────────┼────────────────────────────────────┘
                              │ HTTP/JSON
                              │ Bearer <token>
┌─────────────────────────────▼────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API Routes                           │   │
│  │  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐  │   │
│  │  │  /auth  │ │/requests │ │/portfolio │ │/contracts│  │   │
│  │  │   ✅    │ │   ✅     │ │   ✅      │ │   ✅     │  │   │
│  │  └─────────┘ └──────────┘ └───────────┘ └──────────┘  │   │
│  │  ┌─────────────┐ ┌───────────────┐ ┌──────────────┐   │   │
│  │  │/negotiations│ │  /dashboard   │ │   /seller    │   │   │
│  │  │     ✅      │ │      ✅       │ │     ❌       │   │   │
│  │  └─────────────┘ └───────────────┘ └──────────────┘   │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────▼────────────────────────────────┐   │
│  │              Business Logic (Services)                   │   │
│  │  - NegotiationEngine  - PolicyEngine                     │   │
│  │  - ScoringService     - ComplianceService                │   │
│  │  - AuditService       - ExplainabilityService            │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────▼────────────────────────────────┐   │
│  │              AI Agents (LLM-Powered)                     │   │
│  │  - BuyerAgent  → Request intake, negotiation planning    │   │
│  │  - SellerAgent → Counter-offers, guardrail enforcement   │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────▼────────────────────────────────┐   │
│  │          Data Access (Repository Pattern)                │   │
│  │  - UserRepository      - RequestRepository               │   │
│  │  - VendorRepository    - ContractRepository              │   │
│  │  - NegotiationRepository                                 │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │ SQLAlchemy ORM
┌───────────────────────────▼─────────────────────────────────────┐
│                     DATABASE (PostgreSQL)                        │
├─────────────────────────────────────────────────────────────────┤
│  Tables:                                                         │
│  - user_accounts          - requests                             │
│  - vendor_profiles  ✅    - offers                               │
│  - negotiation_sessions   - contracts  ✅                        │
│  - audit_logs             - policy_configs                       │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Status by Feature

### ✅ Complete (Working End-to-End)

#### 1. Authentication & Authorization
```
Login Page → POST /auth/login → JWT token → localStorage
  ↓
Protected Routes check token → GET /auth/me
  ↓
All API calls include Bearer token via interceptor
```

**Test**: Login with `buyer@test.com` / `password123` ✅

#### 2. Dashboard Metrics
```
Dashboard → useQuery(['dashboard-metrics'])
  ↓
GET /dashboard/metrics
  ↓
Returns: active_requests, pending_approvals, avg_savings, etc.
  ↓
Display in MetricCard components
```

**Test**: View dashboard after login ✅

#### 3. Request Management
```
NewRequest page → api.createRequest(data)
  ↓
POST /requests (or demo mode mock)
  ↓
Validates budget, requirements
  ↓
Returns Request object
  ↓
Navigate to NegotiationTheater
```

**Test**: Create new request via hero input ✅

#### 4. Negotiation Monitoring
```
NegotiationTheater → useQuery(['negotiations', requestId])
  ↓
GET /negotiations/request/{requestId} (or /demo/negotiations/...)
  ↓
Returns NegotiationSession[] with offers, messages
  ↓
Display top 3 offers, live feed
```

**Test**: Launch sourcing, view negotiations ✅

#### 5. Portfolio Backend (NEW!)
```
Portfolio page → api.getPortfolioSubscriptions()
  ↓
GET /portfolio/subscriptions
  ↓
Query contracts where user_id = current_user, status = 'active'
  ↓
Calculate utilization, status, monthly cost
  ↓
Returns Subscription[]
```

**Test**: API endpoint ready, frontend needs wiring 🔧

---

### 🟡 Partial (Backend Ready, Frontend Needs Work)

#### 6. Portfolio UI
**Backend**: ✅ Complete
- GET /portfolio/subscriptions ✅
- GET /portfolio/subscriptions/{id}/usage ✅
- POST /portfolio/subscriptions/{id}/actions ✅

**Frontend**: 🔧 Needs wiring
- Remove mock data from Portfolio.tsx
- Add useQuery to fetch subscriptions
- Wire bulk action buttons to API

**Files to Update**: 1 (`frontend/src/pages/buyer/Portfolio.tsx`)

#### 7. Approval Workflow
**Backend**: 🟡 Missing risk assessment
- GET /contracts/{id} exists ✅
- But lacks `risk_assessment` and `tco_breakdown` fields ❌

**Frontend**: 🔧 Using hardcoded data
- ApprovalWorkspace has static risk items
- TCO breakdown hardcoded ($5k implementation, $2.5k training)

**Files to Update**:
- `src/procur/services/scoring_service.py` (add TCO)
- `src/procur/api/routes/contracts.py` (add risk_assessment)
- `frontend/src/pages/buyer/ApprovalWorkspace.tsx` (use API data)

#### 8. Contract Auto-Creation
**Backend**: 🟡 Manual process
- POST /negotiations/{id}/approve exists ✅
- But doesn't auto-create contract ❌

**Frontend**: 🔧 No contract flow after approval
- Approving negotiation doesn't lead to contract
- No navigation to contract signing

**Files to Update**:
- `src/procur/api/routes/negotiations.py` (auto-create contract on approve)
- `frontend/src/pages/buyer/NegotiationTheater.tsx` (handle contract in response)

---

### ❌ Not Started (Planned for Future Phases)

#### 9. Seller Dashboard Backend
**Status**: ❌ Not implemented

**Needed Endpoints**:
- GET /seller/dashboard/metrics
- GET /seller/deals
- GET /seller/activity-feed

**Frontend**: Currently 100% mocked in SellerDashboard.tsx

**Priority**: Medium (Phase 2)

#### 10. Seller Sub-Pages
**Status**: ❌ Placeholder only

**Pages**:
- SellerNegotiations - Live deal monitoring
- SellerGuardrails - Pricing strategy config
- SellerIntelligence - Win/loss analytics
- SellerTerritory - Territory management

**Priority**: Low (Phase 3)

#### 11. Real-time Updates
**Status**: ❌ Not implemented

**Technology**: WebSocket or Server-Sent Events (SSE)

**Use Cases**:
- Live negotiation updates
- Dashboard metric refreshes
- Notification system

**Priority**: Medium (Phase 4)

#### 12. Advanced Analytics
**Status**: ❌ Not implemented

**Features**:
- Spend forecasting
- Vendor performance scoring
- Budget optimization recommendations
- Historical trend analysis

**Priority**: Low (Phase 5)

---

## Phase Roadmap

### Phase 1: Portfolio Integration (CURRENT) ✅
**Status**: Backend complete, frontend ready to wire

**Deliverables**:
- [x] Portfolio API endpoints
- [x] Data seeding script
- [x] Test users & sample data
- [x] Frontend types & API methods
- [x] Documentation
- [ ] Portfolio UI wiring (30 min remaining)

**Test Criteria**:
- Portfolio shows real subscriptions (not mocked)
- Utilization metrics display correctly
- Bulk actions trigger API calls

### Phase 2: Seller Backend (2-3 hours)
**Goal**: Enable seller persona

**Tasks**:
1. Create `/seller/dashboard/metrics` endpoint
2. Create `/seller/deals` endpoint
3. Create `/seller/activity-feed` endpoint
4. Add seller authorization filters
5. Update SellerDashboard.tsx to use API
6. Test with `seller@apollocrm.com`

**Deliverables**:
- Seller dashboard with real metrics
- Pipeline management
- AI agent activity log

### Phase 3: Enhanced Approvals (3-4 hours)
**Goal**: Real risk assessment & TCO

**Tasks**:
1. Add risk assessment service
2. Update scoring service with TCO breakdown
3. Enhance `GET /contracts/{id}` response
4. Update ApprovalWorkspace.tsx to use API data
5. Wire contract auto-creation on approval

**Deliverables**:
- Risk panel with compliance checks
- Accurate TCO calculations
- Automatic contract generation

### Phase 4: Real-time Updates (1-2 days)
**Goal**: Live negotiation monitoring

**Tasks**:
1. Implement WebSocket endpoint
2. Add SSE for dashboard updates
3. Create frontend WebSocket hook
4. Update NegotiationTheater with live data
5. Add notification system

**Deliverables**:
- Live negotiation updates
- Real-time dashboard refresh
- In-app notifications

### Phase 5: Advanced Features (1-2 weeks)
**Goal**: Production-ready platform

**Tasks**:
1. Real usage tracking (SSO integration)
2. Automated renewal negotiations
3. Cost optimization AI
4. Budget forecasting
5. Analytics dashboard
6. Multi-tenancy

**Deliverables**:
- Advanced analytics
- Predictive insights
- Enterprise features

---

## Critical Path

### Minimum Viable Integration (1 hour)
```
1. Wire Portfolio UI (30 min)
   └→ Update Portfolio.tsx with useQuery

2. Test end-to-end flow (30 min)
   └→ Login → Create request → Portfolio
```

### Full Buyer Experience (4-6 hours)
```
1. Portfolio integration (1 hour)
   └→ Phase 1 complete

2. Enhanced approvals (3-4 hours)
   └→ Risk assessment + TCO
   └→ Auto-contract creation

3. Testing & polish (1 hour)
   └→ E2E scenarios
   └→ Error handling
```

### Complete Platform (2-3 weeks)
```
1. Buyer features (6-8 hours)
   └→ Portfolio + Approvals

2. Seller features (2-3 hours)
   └→ Dashboard + Deals

3. Real-time updates (1-2 days)
   └→ WebSocket/SSE

4. Advanced features (1-2 weeks)
   └→ Analytics, forecasting
```

---

## Dependencies & Prerequisites

### For Portfolio UI (Next Step)
**Requirements**:
- [x] Backend running (python run_api.py)
- [x] Database seeded (python scripts/seed_demo_data.py)
- [x] Frontend types defined ✅
- [x] API methods added ✅
- [ ] Portfolio.tsx updated with useQuery

**Blockers**: None! Ready to implement.

### For Seller Backend
**Requirements**:
- [x] Database models exist (NegotiationSessionRecord, OfferRecord)
- [x] Repository pattern established
- [x] Test seller user created
- [ ] Seller-specific queries implemented

**Blockers**: None, straightforward implementation.

### For Enhanced Approvals
**Requirements**:
- [x] Scoring service exists
- [x] Contract model has metadata field
- [ ] Risk assessment logic defined
- [ ] TCO calculation logic implemented

**Blockers**: Business logic definition needed (risk criteria, TCO formula).

### For Real-time Updates
**Requirements**:
- [ ] WebSocket library (e.g., python-socketio)
- [ ] Frontend WebSocket hook
- [ ] Event bus for backend (may already exist)
- [ ] Authentication over WebSocket

**Blockers**: Technology choice, infrastructure setup.

---

## Testing Strategy

### Unit Tests
```python
# Backend
def test_portfolio_subscriptions_endpoint():
    response = client.get("/portfolio/subscriptions", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3  # Seeded subscriptions

def test_portfolio_action_flag_renegotiation():
    response = client.post(
        f"/portfolio/subscriptions/{contract_id}/actions",
        json={"action": "flag_renegotiation", "reason": "Low utilization"}
    )
    assert response.status_code == 200
```

```typescript
// Frontend
describe('Portfolio API', () => {
  it('fetches subscriptions', async () => {
    const subs = await api.getPortfolioSubscriptions()
    expect(subs).toHaveLength(3)
    expect(subs[0]).toHaveProperty('utilization_percent')
  })
})
```

### Integration Tests
```python
# E2E backend flow
def test_full_procurement_flow():
    # Create request
    request = create_request(user_id, data)

    # Start negotiations
    sessions = start_sourcing(request.id)

    # Approve best offer
    approved = approve_negotiation(sessions[0].id, offer_id)

    # Verify contract created
    contract = get_contract(approved.contract_id)
    assert contract.status == 'draft'
```

### E2E Tests (Frontend)
```typescript
// Playwright/Cypress
test('complete procurement flow', async ({ page }) => {
  await page.goto('/')
  await login(page, 'buyer@test.com', 'password123')

  // Create request
  await page.fill('[data-test="hero-input"]', 'Need CRM')
  await page.click('[data-test="new-request"]')

  // ... complete flow ...

  // Verify in portfolio
  await page.goto('/portfolio')
  await expect(page.locator('[data-test="subscription-card"]')).toBeVisible()
})
```

---

## Quick Reference

### Test Credentials
```
Buyer:  buyer@test.com / password123
Seller: seller@apollocrm.com / password123
```

### Key Commands
```bash
# Setup
./scripts/quickstart.sh

# Seed data
python scripts/seed_demo_data.py

# Start backend
python run_api.py

# Start frontend
cd frontend && npm run dev

# Run tests
pytest  # Backend
npm test  # Frontend
```

### Key URLs
```
Frontend:     http://localhost:5173
Backend API:  http://localhost:8000
API Docs:     http://localhost:8000/docs
OpenAPI Spec: http://localhost:8000/openapi.json
```

### Key Files
```
Backend Routes:  src/procur/api/routes/*.py
Frontend Pages:  frontend/src/pages/**/*.tsx
API Client:      frontend/src/services/api.ts
Types:           frontend/src/types/index.ts
Seeding:         scripts/seed_demo_data.py
Docs:            FRONTEND_BACKEND_INTEGRATION.md
```

---

## Success Metrics

### Phase 1 (Portfolio)
- [ ] Portfolio page uses API (not mocked)
- [ ] 3 subscriptions display correctly
- [ ] Utilization percentages shown
- [ ] Bulk actions call API endpoints
- [ ] No console errors
- [ ] No TypeScript errors

### Phase 2 (Seller)
- [ ] Seller login works
- [ ] Dashboard shows real metrics
- [ ] Deals list displays
- [ ] Activity feed populates
- [ ] Agent actions logged

### Phase 3 (Approvals)
- [ ] Risk panel shows backend data
- [ ] TCO breakdown accurate
- [ ] Contract auto-created on approval
- [ ] Approval comments saved
- [ ] Workflow completes

### Phase 4 (Real-time)
- [ ] Negotiations update live
- [ ] Dashboard refreshes automatically
- [ ] Notifications appear
- [ ] WebSocket reconnects on disconnect
- [ ] No performance degradation

---

## Decision Log

### Why Repository Pattern?
**Decision**: Use repository pattern for data access
**Rationale**: Abstracts SQLAlchemy from business logic, easier testing, consistent API
**Trade-off**: Extra layer of indirection, but worth it for maintainability

### Why TanStack Query?
**Decision**: Use TanStack Query for frontend data fetching
**Rationale**: Built-in caching, loading states, refetch logic, optimistic updates
**Alternative Considered**: Redux Toolkit Query (more boilerplate)

### Why Zustand for Auth?
**Decision**: Use Zustand only for authentication state
**Rationale**: Lightweight, persistent, simple API
**Why Not Redux**: Overkill for just auth, TanStack Query handles rest

### Why Demo Mode?
**Decision**: Support demo mode with in-memory negotiations
**Rationale**: Faster development, easier demos, doesn't require full backend
**Trade-off**: Maintain parallel code paths, but worth it for UX

### Why Portfolio First?
**Decision**: Implement portfolio before seller features
**Rationale**: Highest impact (fully mocked → fully functional), clear value, good test case
**Alternative**: Could have done seller first, but less user-facing impact

---

**Next Step**: Wire up Portfolio UI! 🚀

See `FRONTEND_BACKEND_INTEGRATION.md` for detailed instructions.

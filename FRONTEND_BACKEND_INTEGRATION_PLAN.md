# Frontend-Backend Integration Plan

## Executive Summary

This document outlines the comprehensive plan to integrate the Procur frontend with the backend API, enabling end-to-end procurement workflows with real data from the seeded database.

---

## ✅ Phase 1: Database Seeding (COMPLETED)

### Accomplished:
- ✅ Created seed script (`scripts/seed_vendors.py`)
- ✅ Seeded 7 vendors from `seeds.json`
- ✅ Created 8 organizations (7 vendors + 1 buyer)
- ✅ Created 9 test users (2 buyers + 7 sellers)
- ✅ Fixed database schema compatibility issues

### Test Accounts Available:

**Buyer Accounts:**
- `buyer@test.com / password123` (Demo Buyer)
- `admin@acme.com / admin123` (Admin/Superuser)

**Seller Accounts:**
- `seller@apollocrm.com / apollo123` (ApolloCRM)
- `seller@orbitcrm.com / orbit123` (OrbitCRM)
- `seller@celeritycrm.com / celerity123` (CelerityCRM)
- `seller@zenpayroll.com / zen123` (ZenPayroll)
- `seller@sentinelsecure.com / sentinel123` (SentinelSecure)
- `seller@atlasanalytics.com / atlas123` (AtlasAnalytics)
- `seller@globalerp.com / global123` (GlobalERP)

---

## 🔄 Phase 2: Backend API Enhancements (TODO)

### 2.1 Portfolio/Subscriptions Endpoints (NEW)

**File:** `src/procur/api/routes/portfolio.py`

```python
# Required Endpoints:

GET /portfolio/subscriptions
→ List all active contracts with utilization data
Response: {
  subscriptions: [
    {
      contract_id: str
      vendor_name: str
      service_name: str
      cost_per_month: float
      seats_licensed: int
      seats_active: int
      utilization_percent: float
      renewal_date: str
      auto_renew: bool
      status: "active" | "expiring_soon" | "underutilized"
    }
  ]
}

GET /portfolio/subscriptions/{contract_id}/usage
→ Detailed usage metrics

POST /portfolio/subscriptions/{contract_id}/actions
→ Queue portfolio actions (flag_renegotiation, request_cancellation, adjust_seats)
```

**Database Requirements:**
- Add utilization tracking to contracts
- Create usage metrics table or fields
- Link contracts to active subscriptions

### 2.2 Seller Dashboard Endpoints (NEW)

**File:** `src/procur/api/routes/seller.py`

```python
# Required Endpoints:

GET /seller/dashboard/metrics
→ Seller-specific metrics
Response: {
  pipeline_value: float
  active_deals: int
  win_rate_percent: float
  avg_deal_size: float
  deals_at_risk: int
  avg_response_time_hours: float
}

GET /seller/deals
→ List all deals for seller's vendor
Response: [
  {
    deal_id: str
    buyer_org: str
    product: str
    stage: "discovery" | "negotiation" | "closing" | "won" | "lost"
    value: float
    probability: float
    last_activity: str
  }
]

GET /seller/activity-feed
→ AI agent activity log
```

**Authorization:**
- Filter by vendor_id from user's organization
- Ensure sellers only see their vendor's deals

### 2.3 Enhanced Contract Endpoints

**File:** `src/procur/api/routes/contracts.py` (UPDATE)

```python
# Enhance GET /contracts/{contract_id}
# Add risk_assessment and tco_breakdown to response

Response: {
  # ... existing fields ...
  risk_assessment: {
    compliance_status: "passed" | "review_needed" | "blocked"
    security_review: "approved" | "pending" | "flagged"
    legal_review: "approved" | "pending" | "flagged"
    budget_check: "within_budget" | "exceeds_budget"
    risks: [
      {
        category: "compliance" | "security" | "financial"
        severity: "low" | "medium" | "high"
        description: str
        recommendation: str
      }
    ]
  }
  tco_breakdown: {
    base_cost: float
    implementation_cost: float
    training_cost: float
    ongoing_support: float
    total_year_one: float
    total_three_year: float
  }
}

# Add POST /contracts/{contract_id}/approve
Body: {
  approved_by: str
  comments: str
  conditions: str[]
}
```

**Service Layer Updates:**
- Update `scoring_service.py` to include TCO breakdown
- Add risk assessment logic to contract generation

### 2.4 Negotiation Approval Flow (FIX)

**File:** `src/procur/api/routes/negotiations.py` (UPDATE)

```python
# Fix POST /negotiations/{session_id}/approve
# Auto-create contract from approved offer

@router.post("/{session_id}/approve")
async def approve_negotiation(
    session_id: str,
    data: NegotiationApprove,
    current_user: UserAccount = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    # ... existing validation ...
    
    # NEW: Auto-create contract from approved offer
    contract = await contract_service.create_from_offer(
        request_id=negotiation.request_id,
        vendor_id=negotiation.vendor_id,
        offer_id=data.offer_id,
        approved_by=current_user.id
    )
    
    return {
        "negotiation": negotiation,
        "contract": contract  # Return contract for immediate display
    }
```

---

## 🎨 Phase 3: Frontend Integration (TODO)

### 3.1 Portfolio Page Integration

**File:** `frontend/src/pages/buyer/Portfolio.tsx`

**Changes:**
1. Remove mock data (hardcoded subscriptions array)
2. Add API query:
```typescript
const { data: subscriptions, isLoading } = useQuery({
  queryKey: ['portfolio-subscriptions'],
  queryFn: () => api.getPortfolioSubscriptions()
})
```
3. Add bulk action handlers:
```typescript
const flagForRenegotiation = useMutation({
  mutationFn: (contractIds: string[]) =>
    Promise.all(contractIds.map(id =>
      api.performPortfolioAction(id, { action: 'flag_renegotiation' })
    ))
})
```

### 3.2 Seller Dashboard Integration

**File:** `frontend/src/pages/seller/SellerDashboard.tsx`

**Changes:**
1. Remove all mock data
2. Add API queries:
```typescript
const { data: metrics } = useQuery({
  queryKey: ['seller-metrics'],
  queryFn: () => api.getSellerMetrics()
})

const { data: deals } = useQuery({
  queryKey: ['seller-deals'],
  queryFn: () => api.getSellerDeals()
})

const { data: activity } = useQuery({
  queryKey: ['seller-activity'],
  queryFn: () => api.getSellerActivityFeed()
})
```

### 3.3 Approval Workflow Integration

**File:** `frontend/src/pages/buyer/ApprovalWorkspace.tsx`

**Changes:**
1. Remove hardcoded risk items
2. Use contract.risk_assessment from API:
```typescript
const { data: contract } = useQuery({
  queryKey: ['contract', selectedApproval.contract_id],
  queryFn: () => api.getContract(selectedApproval.contract_id)
})

// Use contract.risk_assessment instead of hardcoded risks
```

3. Update TCO display:
```typescript
// Use contract.tco_breakdown instead of hardcoded values
<div>
  <div>Base: ${contract.tco_breakdown.base_cost}</div>
  <div>Implementation: ${contract.tco_breakdown.implementation_cost}</div>
  <div>Training: ${contract.tco_breakdown.training_cost}</div>
  <div>Total (Year 1): ${contract.tco_breakdown.total_year_one}</div>
</div>
```

4. Wire up approval action:
```typescript
const approveMutation = useMutation({
  mutationFn: (data: { contract_id: string, comments: string }) =>
    api.approveContract(data.contract_id, data.comments),
  onSuccess: () => {
    queryClient.invalidateQueries(['pending-approvals'])
    // Navigate to dashboard or show success
  }
})
```

### 3.4 API Service Updates

**File:** `frontend/src/services/api.ts`

**Add New Methods:**
```typescript
// Portfolio
async getPortfolioSubscriptions(): Promise<Subscription[]> {
  const response = await this.client.get('/portfolio/subscriptions')
  return response.data
}

async getSubscriptionUsage(contractId: string): Promise<UsageMetrics> {
  const response = await this.client.get(`/portfolio/subscriptions/${contractId}/usage`)
  return response.data
}

async performPortfolioAction(contractId: string, data: { action: string }): Promise<void> {
  await this.client.post(`/portfolio/subscriptions/${contractId}/actions`, data)
}

// Seller
async getSellerMetrics(): Promise<SellerMetrics> {
  const response = await this.client.get('/seller/dashboard/metrics')
  return response.data
}

async getSellerDeals(): Promise<Deal[]> {
  const response = await this.client.get('/seller/deals')
  return response.data
}

async getSellerActivityFeed(): Promise<Activity[]> {
  const response = await this.client.get('/seller/activity-feed')
  return response.data
}

// Enhanced contract
async approveContract(contractId: string, comments: string): Promise<Contract> {
  const response = await this.client.post(`/contracts/${contractId}/approve`, { comments })
  return response.data
}
```

### 3.5 Type Definitions

**File:** `frontend/src/types/index.ts`

**Add New Types:**
```typescript
export interface Subscription {
  contract_id: string
  vendor_name: string
  service_name: string
  cost_per_month: number
  seats_licensed: number
  seats_active: number
  utilization_percent: number
  renewal_date: string
  auto_renew: boolean
  status: 'active' | 'expiring_soon' | 'underutilized'
}

export interface SellerMetrics {
  pipeline_value: number
  active_deals: number
  win_rate_percent: number
  avg_deal_size: number
  deals_at_risk: number
  avg_response_time_hours: number
}

export interface Deal {
  deal_id: string
  buyer_org: string
  product: string
  stage: 'discovery' | 'negotiation' | 'closing' | 'won' | 'lost'
  value: number
  probability: number
  last_activity: string
}

export interface Activity {
  timestamp: string
  type: 'offer_sent' | 'counter_received' | 'deal_won' | 'deal_lost'
  deal_id: string
  summary: string
  agent_reasoning: string
}

export interface RiskAssessment {
  compliance_status: 'passed' | 'review_needed' | 'blocked'
  security_review: 'approved' | 'pending' | 'flagged'
  legal_review: 'approved' | 'pending' | 'flagged'
  budget_check: 'within_budget' | 'exceeds_budget'
  risks: RiskItem[]
}

export interface RiskItem {
  category: 'compliance' | 'security' | 'financial'
  severity: 'low' | 'medium' | 'high'
  description: string
  recommendation: string
}

export interface TCOBreakdown {
  base_cost: number
  implementation_cost: number
  training_cost: number
  ongoing_support: number
  total_year_one: number
  total_three_year: number
}

// Update Contract interface
export interface Contract {
  // ... existing fields ...
  risk_assessment?: RiskAssessment
  tco_breakdown?: TCOBreakdown
}
```

---

## 🧪 Phase 4: End-to-End Testing (TODO)

### Test Scenario: Complete Procurement Lifecycle

**User Journey:**

1. **Login as Buyer** (`buyer@test.com / password123`)
   - View dashboard with real metrics
   - See upcoming renewals from contracts table

2. **Create New Request**
   - Description: "Need CRM for 100 sales reps"
   - Budget: $100k - $120k
   - Requirements: SOC2, API, mobile
   - Launch sourcing

3. **Monitor Negotiations**
   - Backend runs BuyerAgent vs SellerAgent for ApolloCRM
   - View real-time offers in NegotiationTheater
   - See top 3 ranked offers

4. **Approve Best Offer**
   - Click "Approve" in theater
   - Backend creates contract
   - Navigate to ApprovalWorkspace

5. **Review Contract**
   - See risk_assessment from backend
   - See TCO breakdown
   - Approve with comments
   - Contract status → "approved"

6. **Sign Contract**
   - Navigate to contracts list
   - Click "Sign"
   - Contract status → "signed" (buyer)
   - Seller auto-signs for demo

7. **View in Portfolio**
   - New subscription appears in Portfolio page
   - Shows utilization (0% initially)
   - Shows renewal date (12 months out)

8. **Login as Seller** (`seller@apollocrm.com / apollo123`)
   - View SellerDashboard
   - See won deal in pipeline
   - See AI agent activity log

---

## 📋 Implementation Checklist

### Week 1: Backend Foundation
- [ ] Create `/portfolio/subscriptions` endpoint
- [ ] Enhance `/contracts/{id}` with risk_assessment & tco_breakdown
- [ ] Fix `/negotiations/{id}/approve` to create contract
- [ ] Add contract utilization tracking

### Week 2: Seller Backend
- [ ] Create `/seller/dashboard/metrics` endpoint
- [ ] Create `/seller/deals` endpoint
- [ ] Create `/seller/activity-feed` endpoint
- [ ] Add seller authorization filters

### Week 3: Frontend Integration
- [ ] Update Portfolio page (remove mocks, add queries)
- [ ] Update ApprovalWorkspace (remove hardcoded risk/TCO)
- [ ] Update SellerDashboard (remove mocks, add queries)
- [ ] Add new types to `types/index.ts`
- [ ] Add new API methods to `services/api.ts`

### Week 4: Testing & Polish
- [ ] End-to-end test buyer flow
- [ ] End-to-end test seller flow
- [ ] Test contract approval → portfolio pipeline
- [ ] Add loading states & error handling
- [ ] Update environment configs

---

## 🔧 Environment Configuration

### Backend `.env`
```bash
# Already configured
PROCUR_API_SECRET_KEY=your-secret-key
PROCUR_API_HOST=0.0.0.0
PROCUR_API_PORT=8000
PROCUR_API_CORS_ORIGINS=http://localhost:5173,http://localhost:5174
DATABASE_URL=postgresql://user:pass@localhost/procur
```

### Frontend `.env`
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_DEMO_MODE=false  # Set to true for demo endpoints
```

---

## ⚠️ Risk Mitigation

### Data Consistency
- Ensure contracts reference valid requests/vendors
- Add foreign key constraints in migrations
- Implement transaction handling for multi-step operations

### Authorization
- Verify seller can only see their vendor's deals
- Buyer can only see their org's requests/contracts
- Add ownership checks in all endpoints

### Performance
- Add pagination to portfolio/deals endpoints
- Consider caching for dashboard metrics (Redis)
- Optimize negotiation session queries (eager load offers)

### Error Handling
- Graceful degradation when backend unavailable
- Clear error messages for validation failures
- Rollback transactions on negotiation approval failures

---

## ✅ Success Criteria

**Buyer Can:**
- ✅ View real portfolio subscriptions
- ✅ Approve contracts with risk assessment
- ✅ See accurate TCO breakdowns
- ✅ Complete full procurement lifecycle (request → negotiate → approve → sign → portfolio)

**Seller Can:**
- ✅ View pipeline metrics
- ✅ Monitor active deals
- ✅ See AI agent activity
- ✅ Respond to negotiations (future)

**System Can:**
- ✅ Seed test vendors from seeds.json
- ✅ Run negotiations with test seller profile
- ✅ Create contracts from approved offers
- ✅ Track subscriptions in portfolio

---

## 🚀 Quick Start Commands

```bash
# Seed database (run once)
python3 scripts/seed_vendors.py

# Start backend API
python run_api.py

# Start frontend (in separate terminal)
cd frontend
npm run dev

# Test as buyer
# Login: buyer@test.com / password123

# Test as seller
# Login: seller@apollocrm.com / apollo123
```

---

## 📝 Notes

- Database seeding is idempotent - safe to run multiple times
- All test passwords are simple for development (e.g., "password123", "apollo123")
- Seller agents are linked to vendor organizations via `organization_id`
- Current schema uses string-based organization_id (not foreign key)
- Demo mode endpoints already exist for rapid prototyping

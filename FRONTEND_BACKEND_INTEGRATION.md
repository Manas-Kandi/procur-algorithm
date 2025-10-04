# Frontend-Backend Integration Guide

## Overview

This document outlines the comprehensive plan to integrate the Procur-2 frontend with the backend holistically. The integration focuses on:

1. **Portfolio Management** - Real subscription tracking with utilization metrics
2. **Test Data Seeding** - Proper vendor and user setup for testing
3. **End-to-End Flow** - Complete procurement lifecycle from request → negotiate → approve → portfolio

---

## Architecture Summary

### Backend (FastAPI + PostgreSQL)
- **API**: RESTful endpoints with JWT authentication
- **Database**: SQLAlchemy ORM with repository pattern
- **Agents**: AI-powered buyer/seller negotiation agents
- **Services**: Policy engine, compliance checker, scoring service

### Frontend (React + TypeScript)
- **State**: Zustand for auth, TanStack Query for data fetching
- **Routing**: React Router v7 with protected routes
- **Design**: Minimal squared aesthetic with Tailwind CSS
- **API Client**: Axios with interceptors for auth

---

## What's New (Phase 1 Implementation)

### ✅ Backend Enhancements

#### 1. Portfolio API (`/portfolio`)
**File**: `src/procur/api/routes/portfolio.py`

**Endpoints**:
- `GET /portfolio/subscriptions` - List all active subscriptions with utilization
- `GET /portfolio/subscriptions/{id}/usage` - Detailed usage metrics
- `POST /portfolio/subscriptions/{id}/actions` - Portfolio management actions

**Features**:
- Real-time utilization tracking (simulated for demo)
- Status detection (active/expiring_soon/underutilized)
- Bulk actions (flag for renegotiation, request cancellation, adjust seats)

#### 2. Data Seeding Script
**File**: `scripts/seed_demo_data.py`

**Capabilities**:
- Seeds 7 vendors from `assets/seeds.json`
- Creates test buyer (`buyer@test.com`) and seller (`seller@apollocrm.com`)
- Generates 3 sample portfolio contracts with varying utilization rates
- Idempotent (can run multiple times safely)

### ✅ Frontend Updates

#### 1. New Types
**File**: `frontend/src/types/index.ts`

```typescript
interface Subscription {
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

interface UsageMetrics {
  daily_active_users: number[]
  feature_usage: Record<string, number>
  cost_per_user: number
  waste_estimate: number
}

interface PortfolioAction {
  action: 'flag_renegotiation' | 'request_cancellation' | 'adjust_seats'
  reason?: string
  target_seats?: number
}
```

#### 2. API Client Methods
**File**: `frontend/src/services/api.ts`

```typescript
// New methods
api.getPortfolioSubscriptions(): Promise<Subscription[]>
api.getSubscriptionUsage(contractId): Promise<UsageMetrics>
api.performPortfolioAction(contractId, action): Promise<void>
```

---

## Setup & Testing

### 1. Database Setup

Ensure your database is configured and migrations are up to date:

```bash
# From project root
alembic upgrade head
```

### 2. Seed Demo Data

Run the seeding script to populate vendors and test users:

```bash
# From project root
python scripts/seed_demo_data.py
```

**Expected Output**:
```
🚀 Seeding demo data for Procur...

============================================================
STEP 1: Seeding vendors from seeds.json
============================================================
✓ Seeded vendor: ApolloCRM
✓ Seeded vendor: OrbitCRM
✓ Seeded vendor: CelerityCRM
✓ Seeded vendor: ZenPayroll
✓ Seeded vendor: SentinelSecure
✓ Seeded vendor: AtlasAnalytics
✓ Seeded vendor: GlobalERP Cloud

✅ Seeded 7 vendors

============================================================
STEP 2: Creating test users
============================================================
✓ Created buyer: buyer@test.com / password123
✓ Created seller: seller@apollocrm.com / password123

✅ Test users created

============================================================
STEP 3: Creating sample portfolio data
============================================================
✓ Created portfolio item: ApolloCRM (42/50 seats)
✓ Created portfolio item: ZenPayroll (100/100 seats)
✓ Created portfolio item: SentinelSecure (15/25 seats)

✅ Sample portfolio data created

============================================================
✅ SEEDING COMPLETE!
============================================================

Test Credentials:
  Buyer:  buyer@test.com / password123
  Seller: seller@apollocrm.com / password123

Seeded 7 vendors and 3 portfolio contracts
```

### 3. Start Backend

```bash
# From project root
python run_api.py
```

API will be available at: `http://localhost:8000`
Docs available at: `http://localhost:8000/docs`

### 4. Start Frontend

```bash
# From frontend directory
cd frontend
npm install  # If first time
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 5. Environment Configuration

**Frontend `.env`** (create if needed):
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_DEMO_MODE=false
```

**Backend `.env`** (should already exist):
```bash
PROCUR_API_SECRET_KEY=your-secret-key
PROCUR_API_HOST=0.0.0.0
PROCUR_API_PORT=8000
PROCUR_API_CORS_ORIGINS=http://localhost:5173,http://localhost:5174
DATABASE_URL=postgresql://user:pass@localhost/procur
```

---

## End-to-End Testing Scenarios

### Scenario 1: View Portfolio (Immediate Test)

**Goal**: Verify portfolio integration works

**Steps**:
1. Login as buyer: `buyer@test.com` / `password123`
2. Navigate to `/portfolio`
3. **Expected**: See 3 subscriptions instead of mock data:
   - ApolloCRM: 50 seats, 84% utilization, Active
   - ZenPayroll: 100 seats, 100% utilization, Active
   - SentinelSecure: 25 seats, 60% utilization, Underutilized

**Verify**:
- Subscription data comes from backend (not hardcoded)
- Utilization percentages are displayed
- Status badges show correct states
- Monthly costs are calculated

### Scenario 2: Portfolio Actions

**Goal**: Test portfolio management actions

**Steps**:
1. From Portfolio page, select "SentinelSecure" (underutilized)
2. Click "Flag for Renegotiation"
3. Provide reason: "Low utilization, reduce seats to 15"
4. Submit action

**Expected**:
- API call to `POST /portfolio/subscriptions/{id}/actions`
- Success message displayed
- Contract flagged in backend (check DB or logs)

### Scenario 3: Full Procurement Flow (Advanced)

**Goal**: Test complete lifecycle from request to portfolio

**Steps**:

1. **Create Request**:
   - Dashboard → Hero Input: "Need project management tool for 75 people"
   - Click "New Request"
   - Budget: $50k - $60k
   - Category: SaaS
   - Must-haves: API, SSO
   - Launch Sourcing

2. **Monitor Negotiations** (if using demo mode):
   - View negotiations in real-time
   - See agent exchanges with vendors
   - Review top 3 offers

3. **Approve Offer**:
   - Select best offer
   - Navigate to Approvals
   - Review risk assessment (future: will be real)
   - Review TCO breakdown (future: will be real)
   - Approve contract

4. **Sign Contract**:
   - Contract auto-created (future enhancement)
   - Sign as buyer
   - Vendor auto-signs (simulated)

5. **View in Portfolio**:
   - Navigate to Portfolio
   - See new subscription appear
   - Verify cost, seats, renewal date

---

## Current Integration Status

### ✅ Fully Integrated
- Authentication & session management
- Dashboard metrics
- Request creation & management
- Negotiation monitoring (with demo mode)
- Pending approvals list
- Upcoming renewals
- **Portfolio subscriptions** ← NEW!

### 🟡 Partially Integrated
- Approval workflow (UI exists, missing risk/TCO backend data)
- Contract management (endpoints exist, not fully wired)

### ❌ Not Yet Integrated
- Seller dashboard (100% mocked)
- Seller sub-pages (placeholders only)
- Real-time negotiation updates (WebSocket/SSE)
- Portfolio bulk actions UI
- Advanced analytics

---

## Next Steps (Future Phases)

### Phase 2: Seller Backend
**Endpoints to implement**:
- `GET /seller/dashboard/metrics` - Seller-specific metrics
- `GET /seller/deals` - Pipeline management
- `GET /seller/activity-feed` - AI agent activity log

### Phase 3: Enhanced Approval Flow
**Backend updates**:
- Add `risk_assessment` to contract endpoint
- Add `tco_breakdown` with implementation/training costs
- Wire contract auto-creation on negotiation approval

### Phase 4: Real-time Updates
**Implementation**:
- WebSocket endpoint for live negotiations
- SSE for dashboard updates
- Optimistic UI updates

### Phase 5: Advanced Portfolio Features
**Features**:
- Real usage tracking (SSO integration)
- Automated renewal negotiations
- Cost optimization recommendations
- Budget forecasting

---

## API Endpoint Reference

### Portfolio Endpoints

#### List Subscriptions
```http
GET /portfolio/subscriptions
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "contract_id": "contract-portfolio-0",
    "vendor_name": "ApolloCRM",
    "service_name": "CRM for sales team",
    "cost_per_month": 1200.00,
    "seats_licensed": 50,
    "seats_active": 42,
    "utilization_percent": 84.0,
    "renewal_date": "2025-06-15",
    "auto_renew": true,
    "status": "active"
  }
]
```

#### Get Usage Metrics
```http
GET /portfolio/subscriptions/{contract_id}/usage
Authorization: Bearer <token>

Response: 200 OK
{
  "daily_active_users": [40, 42, 38, ...],
  "feature_usage": {
    "core_features": 95,
    "advanced_features": 45,
    "integrations": 30,
    "mobile_app": 60
  },
  "cost_per_user": 28.57,
  "waste_estimate": 228.57
}
```

#### Perform Action
```http
POST /portfolio/subscriptions/{contract_id}/actions
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "flag_renegotiation",
  "reason": "Low utilization, reduce seats"
}

Response: 200 OK
{
  "status": "flagged",
  "message": "Contract flagged for renegotiation"
}
```

---

## Troubleshooting

### Issue: "Login failed - 401 Unauthorized"
**Solution**: Ensure backend is running and database is seeded with test users

### Issue: "Portfolio shows no data"
**Solution**: Run `python scripts/seed_demo_data.py` to create sample contracts

### Issue: "CORS error in browser"
**Solution**: Verify `PROCUR_API_CORS_ORIGINS` includes your frontend URL

### Issue: "TypeError: Cannot read property 'vendor_name'"
**Solution**: Check that contracts have proper vendor relationships in DB

### Issue: "Database connection error"
**Solution**: Verify `DATABASE_URL` in `.env` and ensure PostgreSQL is running

---

## Development Workflow

### Adding New Endpoints

1. **Backend**:
   ```python
   # src/procur/api/routes/new_feature.py
   @router.get("/endpoint")
   async def get_data(current_user = Depends(get_current_active_user)):
       return {"data": "value"}
   ```

2. **Register Route**:
   ```python
   # src/procur/api/routes/__init__.py
   from .new_feature import router as new_feature_router

   # src/procur/api/app.py
   app.include_router(new_feature_router)
   ```

3. **Frontend Types**:
   ```typescript
   // frontend/src/types/index.ts
   export interface NewData {
     field: string
   }
   ```

4. **Frontend API Method**:
   ```typescript
   // frontend/src/services/api.ts
   async getNewData(): Promise<NewData> {
     const response = await this.client.get('/endpoint')
     return response.data
   }
   ```

5. **Frontend Usage**:
   ```typescript
   // In component
   const { data } = useQuery({
     queryKey: ['new-data'],
     queryFn: () => api.getNewData()
   })
   ```

---

## Key Files Reference

### Backend
- **Routes**: `src/procur/api/routes/*.py`
- **Models**: `src/procur/db/models.py`
- **Repositories**: `src/procur/db/repositories/*.py`
- **Services**: `src/procur/services/*.py`
- **Agents**: `src/procur/agents/*.py`

### Frontend
- **Types**: `frontend/src/types/index.ts`
- **API Client**: `frontend/src/services/api.ts`
- **Auth Store**: `frontend/src/store/auth.ts`
- **Routes**: `frontend/src/routes/index.tsx`
- **Pages**: `frontend/src/pages/**/*.tsx`
- **Components**: `frontend/src/components/**/*.tsx`

### Configuration
- **Backend Config**: `src/procur/api/config.py`
- **Frontend Env**: `frontend/.env`
- **Database**: `alembic/` (migrations)
- **Seeds**: `assets/seeds.json`

---

## Testing Checklist

- [ ] Backend starts without errors (`python run_api.py`)
- [ ] Frontend starts without errors (`npm run dev`)
- [ ] Seeding script completes successfully
- [ ] Login works with test credentials
- [ ] Dashboard shows real metrics
- [ ] Portfolio shows 3 seeded subscriptions
- [ ] Portfolio utilization percentages display correctly
- [ ] Can navigate between all pages
- [ ] API calls include Bearer token (check Network tab)
- [ ] No CORS errors in console

---

## Success Criteria

### Immediate (Phase 1)
- ✅ Portfolio page uses real backend data (not mocked)
- ✅ Test users can login and access protected routes
- ✅ Seeding script reliably creates demo data
- ✅ Portfolio actions trigger backend API calls

### Short-term (Phase 2-3)
- 🎯 Seller dashboard shows real metrics
- 🎯 Approval flow uses backend risk assessment
- 🎯 Contract auto-creation on negotiation approval
- 🎯 Full procurement lifecycle works end-to-end

### Long-term (Phase 4-5)
- 🎯 Real-time negotiation updates
- 🎯 Production-ready usage tracking
- 🎯 Advanced analytics and forecasting
- 🎯 Multi-tenancy support

---

## Contributing

When adding new features:

1. **Backend First**: Implement endpoint with proper auth/validation
2. **Types**: Define TypeScript interfaces matching backend models
3. **API Client**: Add method to `api.ts`
4. **Component**: Use TanStack Query for data fetching
5. **Test**: Add to testing scenarios above
6. **Document**: Update this guide

---

## Contact & Support

**Documentation**:
- Backend API: `http://localhost:8000/docs`
- This guide: `FRONTEND_BACKEND_INTEGRATION.md`
- Design system: `DESIGN_SYSTEM.md`

**Architecture Docs**:
- API Implementation: `API_IMPLEMENTATION_SUMMARY.md`
- Authentication: `AUTHENTICATION_README.md`
- Event Bus: `EVENT_BUS_README.md`

---

*Last Updated: 2025-10-03*
*Integration Phase: 1 (Portfolio Management)*

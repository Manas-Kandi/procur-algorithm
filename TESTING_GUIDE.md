# Procur Testing Guide

Quick reference for testing the frontend-backend integration with seeded data.

---

## 🚀 Quick Start

### 1. Start Backend API
```bash
python run_api.py
# API will be available at http://localhost:8000
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
# Frontend will be available at http://localhost:5173
```

---

## 👥 Test Accounts

### Buyer Accounts
| Email | Password | Role | Notes |
|-------|----------|------|-------|
| `buyer@test.com` | `test123` | Buyer | Standard demo buyer |
| `admin@acme.com` | `admin123` | Buyer | Superuser with admin privileges |

### Seller Accounts
| Email | Password | Vendor | Price/Seat/Year |
|-------|----------|--------|-----------------|
| `seller@apollocrm.com` | `apollo123` | ApolloCRM | $1,200 |
| `seller@orbitcrm.com` | `orbit123` | OrbitCRM | $240 |
| `seller@celeritycrm.com` | `celerity123` | CelerityCRM | $360 |
| `seller@zenpayroll.com` | `zen123` | ZenPayroll | $25/month |
| `seller@sentinelsecure.com` | `sentinel123` | SentinelSecure | $1,500 |
| `seller@atlasanalytics.com` | `atlas123` | AtlasAnalytics | $900 |
| `seller@globalerp.com` | `global123` | GlobalERP | $1,800 |

---

## 🧪 Test Scenarios

### Scenario 1: Basic Buyer Flow

**Goal:** Create a request and start negotiations

1. **Login as Buyer**
   - Navigate to http://localhost:5173
   - Login: `buyer@test.com / test123`

2. **View Dashboard**
   - Check metrics are loading from API
   - Verify no mock data is displayed

3. **Create Request**
   - Click "New Request" or use HeroInput
   - Fill in:
     - Description: "Need CRM for 100 sales reps"
     - Category: SaaS/CRM
     - Budget: $100,000 - $120,000
     - Quantity: 100 seats
     - Requirements: SOC2, API, mobile

4. **Start Sourcing**
   - Click "Launch Sourcing"
   - Backend should match with ApolloCRM, OrbitCRM, CelerityCRM

5. **Monitor Negotiations**
   - Navigate to negotiations page
   - Watch real-time offers from vendors
   - Verify NegotiationStoryboard shows live data

### Scenario 2: Contract Approval Flow

**Goal:** Approve an offer and create a contract

1. **Approve Best Offer**
   - In NegotiationTheater, select top-ranked offer
   - Click "Approve"
   - Verify contract is created

2. **Review in ApprovalWorkspace**
   - Navigate to Approvals
   - Select the new contract
   - Verify risk assessment displays (when backend implemented)
   - Verify TCO breakdown displays (when backend implemented)

3. **Approve Contract**
   - Add approval comments
   - Click "Approve"
   - Verify status changes to "approved"

4. **Sign Contract**
   - Navigate to Contracts list
   - Click "Sign" on approved contract
   - Verify status changes to "signed"

### Scenario 3: Portfolio Management

**Goal:** View and manage active subscriptions

1. **Navigate to Portfolio**
   - Login as `buyer@test.com / test123`
   - Go to Portfolio page

2. **View Subscriptions**
   - Verify signed contracts appear as subscriptions
   - Check utilization metrics (when backend implemented)
   - Check renewal dates

3. **Bulk Actions**
   - Select multiple subscriptions
   - Flag for renegotiation (when backend implemented)
   - Verify action queued

### Scenario 4: Seller Dashboard

**Goal:** Monitor deals as a seller

1. **Login as Seller**
   - Navigate to http://localhost:5173
   - Login: `seller@apollocrm.com / apollo123`

2. **View Dashboard**
   - Check pipeline metrics (when backend implemented)
   - Verify only ApolloCRM deals are visible

3. **Monitor Active Deals**
   - View deals list (when backend implemented)
   - Check deal stages and values
   - Verify buyer organization names

4. **AI Agent Activity**
   - View activity feed (when backend implemented)
   - Check agent reasoning and actions
   - Verify timestamps

---

## 🔍 API Testing

### Direct API Endpoints

#### Authentication
```bash
# Login as buyer
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "buyer@test.com", "password": "test123"}'

# Response: {"access_token": "...", "token_type": "bearer"}
```

#### Get Current User
```bash
# Replace TOKEN with access_token from login
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer TOKEN"
```

#### Create Request
```bash
curl -X POST http://localhost:8000/requests \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Need CRM for 100 sales reps",
    "request_type": "saas",
    "category": "crm",
    "budget_min": 100000,
    "budget_max": 120000,
    "quantity": 100,
    "must_haves": ["SOC2", "API", "mobile"]
  }'
```

#### Start Sourcing
```bash
# Replace REQUEST_ID with request_id from previous response
curl -X POST http://localhost:8000/sourcing/start/REQUEST_ID \
  -H "Authorization: Bearer TOKEN"
```

#### Get Negotiations
```bash
curl http://localhost:8000/negotiations/request/REQUEST_ID \
  -H "Authorization: Bearer TOKEN"
```

---

## 🐛 Debugging Tips

### Backend Issues

**Check API is running:**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

**Check database connection:**
```bash
python -c "from src.procur.db.session import get_db_session; db = get_db_session(); print('DB connected')"
```

**View API logs:**
- Check terminal where `run_api.py` is running
- Look for error stack traces
- Verify CORS headers if frontend can't connect

**Re-seed database:**
```bash
python3 scripts/seed_vendors.py
# Safe to run multiple times - checks for existing data
```

### Frontend Issues

**Check API connection:**
- Open browser DevTools (F12)
- Go to Network tab
- Look for failed API requests
- Check CORS errors in Console

**Verify environment variables:**
```bash
cd frontend
cat .env
# Should have: VITE_API_BASE_URL=http://localhost:8000
```

**Clear React Query cache:**
- In browser DevTools Console:
```javascript
localStorage.clear()
sessionStorage.clear()
location.reload()
```

**Check for mock data:**
- Search codebase for hardcoded arrays
- Look for `const mockData = [...]` patterns
- Verify API calls are being made

---

## 📊 Data Verification

### Check Seeded Data

**Organizations:**
```bash
python -c "
from src.procur.db.session import session_context
from src.procur.db.models_auth import Organization

with session_context() as session:
    orgs = session.query(Organization).all()
    for org in orgs:
        print(f'{org.organization_id}: {org.name}')
"
```

**Vendors:**
```bash
python -c "
from src.procur.db.session import session_context
from src.procur.db.models import VendorProfileRecord

with session_context() as session:
    vendors = session.query(VendorProfileRecord).all()
    for v in vendors:
        print(f'{v.vendor_id}: {v.name} - \${v.list_price}')
"
```

**Users:**
```bash
python -c "
from src.procur.db.session import session_context
from src.procur.db.models import UserAccount

with session_context() as session:
    users = session.query(UserAccount).all()
    for u in users:
        print(f'{u.email} ({u.role}) - Org: {u.organization_id}')
"
```

---

## 🔄 Reset & Re-seed

### Full Database Reset
```bash
# WARNING: This will delete all data!

# 1. Downgrade to base
alembic downgrade base

# 2. Upgrade to latest
alembic upgrade head

# 3. Re-seed data
python3 scripts/seed_vendors.py
```

### Partial Reset (Keep Schema)
```bash
# Delete all data but keep tables
python -c "
from src.procur.db.session import session_context
from src.procur.db.models import *
from src.procur.db.models_auth import *

with session_context() as session:
    # Delete in order to respect foreign keys
    session.query(ContractRecord).delete()
    session.query(OfferRecord).delete()
    session.query(NegotiationSessionRecord).delete()
    session.query(RequestRecord).delete()
    session.query(VendorProfileRecord).delete()
    session.query(UserAccount).delete()
    session.query(Organization).delete()
    session.commit()
    print('All data deleted')
"

# Re-seed
python3 scripts/seed_vendors.py
```

---

## 📝 Common Issues & Solutions

### Issue: "No vendors found for request"
**Solution:** 
- Verify vendors are seeded: Check with data verification script above
- Check request category matches vendor categories in seeds.json
- Ensure must_haves are not too restrictive

### Issue: "Negotiation not starting"
**Solution:**
- Check backend logs for errors
- Verify LLM API key is configured
- Check NegotiationEngine is properly initialized

### Issue: "Frontend shows mock data"
**Solution:**
- Search for hardcoded data in component files
- Verify API calls are being made (Network tab)
- Check if demo mode is enabled (VITE_DEMO_MODE)

### Issue: "Authentication failed"
**Solution:**
- Verify user exists in database
- Check password hash is correct
- Ensure JWT secret key is configured
- Check token expiration settings

### Issue: "CORS errors"
**Solution:**
- Verify PROCUR_API_CORS_ORIGINS includes frontend URL
- Check backend is running on expected port
- Restart backend after .env changes

---

## ✅ Integration Checklist

Use this checklist to verify integration is complete:

### Backend
- [ ] All endpoints return real data (no mocks)
- [ ] Authentication works for all test users
- [ ] Negotiations create real offers
- [ ] Contracts are created from approved offers
- [ ] Risk assessment is calculated
- [ ] TCO breakdown is included

### Frontend
- [ ] No hardcoded/mock data in components
- [ ] All API calls use real endpoints
- [ ] Loading states display correctly
- [ ] Error handling shows user-friendly messages
- [ ] Data refreshes after mutations

### End-to-End
- [ ] Can create request as buyer
- [ ] Negotiations start automatically
- [ ] Offers appear in real-time
- [ ] Can approve offers and create contracts
- [ ] Contracts appear in portfolio
- [ ] Seller dashboard shows deals
- [ ] All test accounts work correctly

---

## 🎯 Success Metrics

**Integration is successful when:**

1. ✅ Buyer can complete full procurement cycle without errors
2. ✅ Seller can view their deals and activity
3. ✅ No mock data is visible in UI
4. ✅ All API endpoints return real database data
5. ✅ Negotiations produce realistic offers
6. ✅ Contracts are created and tracked properly
7. ✅ Portfolio shows active subscriptions
8. ✅ All test accounts authenticate successfully

---

## 📞 Support

If you encounter issues:

1. Check this guide for common solutions
2. Review backend logs for errors
3. Check browser console for frontend errors
4. Verify database has seeded data
5. Ensure all services are running

**Quick Health Check:**
```bash
# Backend
curl http://localhost:8000/health

# Database
python -c "from src.procur.db.session import get_db_session; get_db_session()"

# Frontend
curl http://localhost:5173
```

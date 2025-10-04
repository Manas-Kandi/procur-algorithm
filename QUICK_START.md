# Procur-2 Quick Start Guide

## 🚀 Get Running in 3 Minutes

### Option 1: Automated Setup (Recommended)

```bash
# From project root
./scripts/quickstart.sh

# Terminal 1: Start backend
python run_api.py

# Terminal 2: Start frontend
cd frontend && npm run dev
```

**Done!** Visit http://localhost:5173 and login with `buyer@test.com` / `password123`

### Option 2: Manual Setup

```bash
# 1. Activate Python environment
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 2. Install backend
pip install -e .

# 3. Run migrations
alembic upgrade head

# 4. Seed demo data
python scripts/seed_demo_data.py

# 5. Install frontend
cd frontend
npm install

# 6. Create frontend .env
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
echo "VITE_DEMO_MODE=false" >> .env

# 7. Start backend (in one terminal)
cd .. && python run_api.py

# 8. Start frontend (in another terminal)
cd frontend && npm run dev
```

---

## 🧪 Test the Integration

### 1. Portfolio (NEW!)
```
✅ Login: buyer@test.com / password123
✅ Navigate to /portfolio
✅ Expect: 3 real subscriptions (not mocked):
   - ApolloCRM: 50 seats, 84% utilization
   - ZenPayroll: 100 seats, 100% utilization
   - SentinelSecure: 25 seats, 60% utilization
```

### 2. Full Procurement Flow
```
✅ Login as buyer
✅ Dashboard → Hero Input: "Need CRM for 100 reps"
✅ Create Request → Launch Sourcing
✅ Monitor negotiations in theater
✅ Approve best offer
✅ View in Portfolio (future)
```

### 3. Seller Login
```
✅ Login: seller@apollocrm.com / password123
✅ View SellerDashboard (currently mocked)
✅ Future: See real pipeline metrics
```

---

## 📍 Where to Go Next

### Immediate (30 min)
**Wire up Portfolio UI**
- File: `frontend/src/pages/buyer/Portfolio.tsx`
- Task: Replace mock data with `useQuery`
- Guide: See `FRONTEND_BACKEND_INTEGRATION.md` section "3.1 Portfolio Page Integration"

### Short-term (2-3 hours)
**Implement Seller Backend**
- Files: Create `src/procur/api/routes/seller.py`
- Task: Add seller metrics, deals, activity endpoints
- Guide: See `INTEGRATION_ROADMAP.md` Phase 2

### Medium-term (4-6 hours)
**Enhanced Approval Flow**
- Files: Update `contracts.py`, `ApprovalWorkspace.tsx`
- Task: Add risk assessment & TCO to contracts
- Guide: See `INTEGRATION_ROADMAP.md` Phase 3

---

## 🔍 Key Endpoints

### Already Working ✅
```
POST   /auth/login               - Login
GET    /auth/me                  - Current user
GET    /dashboard/metrics        - Dashboard stats
GET    /requests                 - List requests
POST   /requests                 - Create request
POST   /sourcing/start/{id}      - Launch negotiations
GET    /negotiations/request/{id} - Get negotiations
GET    /portfolio/subscriptions  - List subscriptions ⭐ NEW!
```

### Coming Soon 🔜
```
GET    /seller/dashboard/metrics - Seller stats
GET    /seller/deals             - Pipeline
POST   /portfolio/*/actions      - Portfolio actions
```

---

## 📊 Current Status

### ✅ Fully Integrated
- Authentication & sessions
- Dashboard metrics
- Request management
- Negotiation monitoring (demo mode)
- **Portfolio backend** ⭐ NEW!

### 🟡 Needs Frontend Wiring
- Portfolio UI (backend ready)
- Approval risk panel
- Contract auto-creation

### ❌ Not Yet Built
- Seller dashboard backend
- Real-time updates
- Advanced analytics

---

## 🐛 Troubleshooting

### "Login failed"
→ Backend not running: `python run_api.py`
→ Check terminal for errors

### "Portfolio shows no data"
→ Data not seeded: `python scripts/seed_demo_data.py`
→ Check database connection

### "CORS error"
→ Verify `.env`: `PROCUR_API_CORS_ORIGINS` includes frontend URL

### "Module not found"
→ Backend: `pip install -e .`
→ Frontend: `cd frontend && npm install`

---

## 📁 Key Files

### Backend
```
src/procur/api/routes/
  ├── portfolio.py     ⭐ NEW! Portfolio management
  ├── auth.py          ✅ Authentication
  ├── requests.py      ✅ Request CRUD
  ├── negotiations.py  ✅ Negotiation tracking
  ├── contracts.py     ✅ Contract management
  └── dashboard.py     ✅ Metrics
```

### Frontend
```
frontend/src/
  ├── types/index.ts          ✅ Type definitions
  ├── services/api.ts         ✅ API client
  ├── store/auth.ts           ✅ Auth state
  └── pages/
      ├── buyer/
      │   ├── Dashboard.tsx          ✅ Working
      │   ├── Portfolio.tsx          🔧 Needs wiring
      │   └── ApprovalWorkspace.tsx  🔧 Partial
      └── seller/
          └── SellerDashboard.tsx    ❌ Mocked
```

### Scripts
```
scripts/
  ├── seed_demo_data.py    ⭐ NEW! Seed vendors & users
  └── quickstart.sh        ⭐ NEW! Automated setup
```

### Documentation
```
FRONTEND_BACKEND_INTEGRATION.md  📚 Complete guide
INTEGRATION_ROADMAP.md           🗺️  Visual roadmap
INTEGRATION_SUMMARY.md           📝 What we built
QUICK_START.md                   ⚡ This file
```

---

## 🎯 Test Credentials

```
Buyer:  buyer@test.com / password123
Seller: seller@apollocrm.com / password123
```

---

## 🔗 URLs

```
Frontend:   http://localhost:5173
Backend:    http://localhost:8000
API Docs:   http://localhost:8000/docs
```

---

## 📞 Need Help?

1. **Check docs**: `FRONTEND_BACKEND_INTEGRATION.md`
2. **View roadmap**: `INTEGRATION_ROADMAP.md`
3. **Test endpoints**: http://localhost:8000/docs
4. **Check logs**: Terminal running `python run_api.py`

---

## ✨ What's New (Phase 1)

### Backend
- ✅ Portfolio API (`/portfolio/subscriptions`)
- ✅ Subscription usage metrics
- ✅ Portfolio action endpoints
- ✅ Demo data seeding script

### Frontend
- ✅ Portfolio types (Subscription, UsageMetrics)
- ✅ API client methods
- 🔧 Portfolio UI (needs wiring)

### Tooling
- ✅ Automated setup script
- ✅ Comprehensive documentation
- ✅ Visual roadmap

---

## 🚦 Next Steps

```
1. Run quickstart    →  ./scripts/quickstart.sh
2. Test portfolio    →  http://localhost:5173/portfolio
3. Wire up UI        →  Update Portfolio.tsx (30 min)
4. Celebrate! 🎉
```

**Ready to go!** 🚀

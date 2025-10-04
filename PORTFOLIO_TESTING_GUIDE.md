# Portfolio Integration Testing Guide

## What Was Changed

The Portfolio page (`frontend/src/pages/buyer/Portfolio.tsx`) has been updated to use **real backend data** instead of hardcoded mock subscriptions.

### Key Changes

1. **API Integration**:
   - Added `useQuery` to fetch subscriptions from `GET /portfolio/subscriptions`
   - Maps backend `Subscription` type to frontend `PortfolioSubscription` format
   - Added loading and error states

2. **Bulk Actions**:
   - Wired up "Flag for Renegotiation" button → `POST /portfolio/subscriptions/{id}/actions`
   - Wired up "Request Cancellation" button → `POST /portfolio/subscriptions/{id}/actions`
   - Added mutation with optimistic updates and error handling

3. **Empty State**:
   - Shows friendly message when no subscriptions exist
   - Guides users on what to expect

4. **Dynamic Calculations**:
   - Summary metrics (total cost, utilization, renewals) now calculated from real data
   - Risk levels determined by utilization percentage

---

## Testing Steps

### Prerequisites

1. **Backend Running**:
   ```bash
   # Terminal 1 - from project root
   python run_api.py
   ```

2. **Data Seeded**:
   ```bash
   # If not already done
   python scripts/seed_demo_data.py
   ```

3. **Frontend Running**:
   ```bash
   # Terminal 2 - from frontend directory
   cd frontend
   npm run dev
   ```

---

### Test 1: Basic Portfolio Display

**Goal**: Verify portfolio loads with real backend data

**Steps**:
1. Navigate to http://localhost:5173
2. Login with `buyer@test.com` / `password123`
3. Click "Portfolio" in sidebar (or navigate to `/portfolio`)

**Expected Results**:
- ✅ Page loads without errors
- ✅ Shows "Loading portfolio..." spinner briefly
- ✅ Displays 3 subscriptions from seeded data:
  - **ApolloCRM**: ~50 seats, ~84% utilization
  - **ZenPayroll**: ~100 seats, ~100% utilization
  - **SentinelSecure**: ~25 seats, ~60% utilization
- ✅ Summary cards show correct totals:
  - Total Subscriptions: 3
  - Monthly Cost: calculated sum
  - Avg Utilization: ~80%
  - Renewals (60d): varies by renewal date

**How to Verify Backend Data**:
- Open http://localhost:8000/docs
- Try `GET /portfolio/subscriptions` endpoint
- Should return JSON array with 3 subscriptions

---

### Test 2: Utilization Display

**Goal**: Verify utilization percentages and status badges

**Steps**:
1. In Portfolio table, check utilization column
2. Look for colored progress bars

**Expected Results**:
- ✅ Each subscription shows utilization percentage
- ✅ Progress bar colors:
  - **Green**: ≥80% utilization (low risk)
  - **Amber**: 60-79% utilization (medium risk)
  - **Red**: <60% utilization (high risk)
- ✅ Seats display as "active / total" (e.g., "42 / 50")

**Example from Seeded Data**:
- ApolloCRM: ~84% → Green bar (low risk)
- ZenPayroll: ~100% → Green bar (low risk)
- SentinelSecure: ~60% → Amber bar (medium risk)

---

### Test 3: Filtering

**Goal**: Test subscription filters

**Steps**:
1. Click "All Subscriptions" (default)
2. Click "Upcoming Renewals" filter
3. Click "Underutilized" filter

**Expected Results**:
- ✅ "All Subscriptions": Shows all 3
- ✅ "Upcoming Renewals": Shows subscriptions with renewal ≤60 days
- ✅ "Underutilized": Shows subscriptions with utilization <75%
  - Should include SentinelSecure (~60%)

**Note**: Filter behavior depends on renewal dates in seeded data, which are calculated relative to contract start dates.

---

### Test 4: Bulk Action - Flag for Renegotiation

**Goal**: Test bulk action to flag subscriptions

**Steps**:
1. Select checkbox next to "SentinelSecure" (underutilized)
2. Click "Flag for Renegotiation (1)"
3. Wait for action to complete

**Expected Results**:
- ✅ Button shows "Processing..." during mutation
- ✅ Success: Selection clears, page refreshes
- ✅ Backend logs action (check terminal running API)
- ✅ Contract metadata updated in database

**Verify Backend**:
```bash
# In Python console
from procur.db.session import get_session
from procur.db.repositories import ContractRepository

session = next(get_session())
repo = ContractRepository(session)
contract = repo.get_by_contract_id("contract-portfolio-2")  # SentinelSecure
print(contract.metadata)
# Should see: {'flagged_for_renegotiation': True, 'flag_reason': '...', 'flagged_at': '...'}
```

---

### Test 5: Bulk Action - Request Cancellation

**Goal**: Test bulk cancellation request

**Steps**:
1. Select multiple subscriptions (e.g., ApolloCRM + ZenPayroll)
2. Click "Request Cancellation"
3. Wait for action to complete

**Expected Results**:
- ✅ Both subscriptions processed
- ✅ Selections clear after success
- ✅ Backend marks both contracts with cancellation request

**Verify Backend**:
```bash
# Check API logs for POST requests to /portfolio/subscriptions/*/actions
# Should see 2 requests with action: "request_cancellation"
```

---

### Test 6: Empty State

**Goal**: Verify empty state when no subscriptions exist

**Steps**:
1. Clear database contracts (or login with a user who has no contracts)
2. Navigate to `/portfolio`

**Expected Results**:
- ✅ Shows empty state message:
  - "No active subscriptions"
  - "Completed contracts will appear here once you approve and sign them."
- ✅ No table displayed
- ✅ Summary cards show zeros

**To Reset Database** (optional):
```bash
# Delete seeded contracts
python -c "
from procur.db.session import get_session
from procur.db.repositories import ContractRepository
session = next(get_session())
repo = ContractRepository(session)
# Delete all contracts for test user
session.query(repo.model).delete()
session.commit()
"
# Then refresh portfolio page
```

---

### Test 7: Error Handling

**Goal**: Test error states

**Steps**:
1. Stop the backend (`Ctrl+C` in terminal running `python run_api.py`)
2. Refresh portfolio page
3. Click "Retry" button
4. Restart backend
5. Click "Retry" again

**Expected Results**:
- ✅ With backend down: Shows error message
  - "Failed to load portfolio"
  - Displays error details
  - Shows "Retry" button
- ✅ Clicking retry attempts to refetch
- ✅ With backend up: Retry succeeds and loads data

---

### Test 8: Loading State

**Goal**: Verify loading spinner

**Steps**:
1. Open browser DevTools → Network tab
2. Set network throttling to "Slow 3G"
3. Navigate to `/portfolio`

**Expected Results**:
- ✅ Shows loading spinner with "Loading portfolio..." message
- ✅ Spinner displays while request is pending
- ✅ Transitions smoothly to data display when loaded

---

### Test 9: API Network Inspection

**Goal**: Verify correct API calls

**Steps**:
1. Open browser DevTools → Network tab
2. Navigate to `/portfolio`
3. Check network requests

**Expected Requests**:
- ✅ `GET /portfolio/subscriptions`
  - Status: 200 OK
  - Response: Array of 3 subscription objects
  - Authorization header: `Bearer <token>`

**After Bulk Action**:
- ✅ `POST /portfolio/subscriptions/{contract_id}/actions`
  - Status: 200 OK
  - Request body: `{"action": "flag_renegotiation", "reason": "..."}`
  - Response: `{"status": "flagged", "message": "..."}`

---

### Test 10: End-to-End Flow (Future)

**Goal**: Test complete procurement → portfolio flow

**Steps** (once contract creation is wired):
1. Create new request via Dashboard
2. Launch sourcing
3. Monitor negotiations
4. Approve best offer
5. Sign contract
6. Navigate to Portfolio
7. Verify new subscription appears

**Expected Results**:
- ✅ New subscription visible in portfolio
- ✅ Shows correct vendor, seats, cost
- ✅ Utilization starts at 0% (no usage yet)
- ✅ Renewal date 12 months from contract start

**Note**: This requires Phase 3 (contract auto-creation) to be implemented.

---

## Common Issues & Troubleshooting

### Issue: "Failed to load portfolio" on page load

**Possible Causes**:
1. Backend not running
2. Database not seeded
3. Authentication token expired
4. CORS error

**Solutions**:
```bash
# 1. Check backend is running
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

# 2. Verify data exists
curl -H "Authorization: Bearer <token>" http://localhost:8000/portfolio/subscriptions
# Should return array of subscriptions

# 3. Re-login to get fresh token
# Logout and login again at http://localhost:5173/login

# 4. Check CORS settings in backend .env
# PROCUR_API_CORS_ORIGINS should include http://localhost:5173
```

---

### Issue: Empty portfolio despite seeding

**Possible Causes**:
1. Logged in as wrong user
2. Seeding script failed
3. Database reset

**Solutions**:
```bash
# 1. Verify you're logged in as buyer@test.com
# Check Network tab → /auth/me response

# 2. Re-run seeding script
python scripts/seed_demo_data.py

# 3. Check database directly
python -c "
from procur.db.session import get_session
from procur.db.repositories import ContractRepository, UserRepository
session = next(get_session())

# Get buyer user
user_repo = UserRepository(session)
buyer = user_repo.get_by_email('buyer@test.com')
print(f'Buyer ID: {buyer.id}')

# Check contracts
contract_repo = ContractRepository(session)
contracts = session.query(contract_repo.model).all()
print(f'Total contracts: {len(contracts)}')
for c in contracts:
    print(f'  {c.contract_id} - {c.vendor.name if c.vendor else \"No vendor\"}')
"
```

---

### Issue: Bulk actions not working

**Possible Causes**:
1. Network error
2. Invalid contract IDs
3. Backend validation error

**Solutions**:
1. Open DevTools → Console for error messages
2. Check Network tab for failed requests
3. Verify contract IDs match backend data
4. Check backend logs for validation errors

---

### Issue: Utilization percentages seem wrong

**Expected Behavior**:
The backend simulates seat usage with `_simulate_seat_usage()` function, which generates 60-95% utilization randomly. Each page refresh may show slightly different numbers.

**This is intentional** for demo purposes. In production, this would come from SSO/directory integration.

---

## Success Criteria Checklist

After completing all tests, verify:

- [ ] Portfolio loads without errors
- [ ] Shows 3 seeded subscriptions
- [ ] Utilization percentages display correctly
- [ ] Summary metrics calculated accurately
- [ ] Filters work (All/Upcoming/Underutilized)
- [ ] Bulk "Flag for Renegotiation" works
- [ ] Bulk "Request Cancellation" works
- [ ] Empty state displays when no data
- [ ] Error state displays when backend down
- [ ] Loading state shows during fetch
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] API calls include Bearer token
- [ ] Backend logs show successful actions

---

## Next Steps After Testing

Once portfolio integration is verified:

1. **Wire Contract Auto-Creation** (Phase 3)
   - Update `/negotiations/{id}/approve` to create contract
   - Test: Approve negotiation → see subscription in portfolio

2. **Implement Seller Dashboard** (Phase 2)
   - Create `/seller/dashboard/metrics` endpoint
   - Update `SellerDashboard.tsx` to use API

3. **Add Real-time Updates** (Phase 4)
   - WebSocket for live negotiation updates
   - SSE for dashboard refreshes

---

## API Reference (Quick)

### Get Subscriptions
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

### Perform Action
```http
POST /portfolio/subscriptions/{contract_id}/actions
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "flag_renegotiation",
  "reason": "Low utilization"
}

Response: 200 OK
{
  "status": "flagged",
  "message": "Contract flagged for renegotiation"
}
```

---

## Resources

- **Integration Guide**: `FRONTEND_BACKEND_INTEGRATION.md`
- **Roadmap**: `INTEGRATION_ROADMAP.md`
- **Quick Start**: `QUICK_START.md`
- **API Docs**: http://localhost:8000/docs

---

**Happy Testing!** 🚀

Report any issues or questions in the main integration guide.

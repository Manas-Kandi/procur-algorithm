# Quick Start: See AI Negotiate in Real-Time

## TL;DR - 5 Steps to See AI in Action

1. **Start servers** (backend + frontend running)
2. **Login** → `buyer@test.com` / `password123`
3. **Create request** → Dashboard → New Request
4. **Launch sourcing** → From request page, click "Launch AI Sourcing"
5. **Navigate to:** `http://localhost:5173/requests/{requestId}/negotiate`

**You're now at the Negotiation Theater!**

---

## What You're Seeing vs What We Built

### Current UI: NegotiationTheater (Static Demo)
- **URL:** `/requests/{requestId}/negotiate`
- **What it shows:** Mock negotiation data from `seeds.json`
- **Component:** `NegotiationTheater.tsx` (existing)
- **Status:** ✅ Working, but using demo data

### What We Built: Real AI Auto-Negotiation
- **API:** `POST /negotiations/{session_id}/auto-negotiate`
- **WebSocket:** `WS /negotiations/ws/{session_id}`
- **Component:** `NegotiationTheaterLive.tsx` (new, but not wired to routes yet)
- **Status:** ✅ Backend working, ⚠️ Frontend not connected to routes

---

## How to Connect Everything (Choose One)

### Option A: Quick Test - Add Live Button to Current Page

**Easiest way to see it working RIGHT NOW:**

1. **Update `NegotiationTheater.tsx`** to add auto-negotiate button:

```typescript
// Add this import at top
import { useMutation } from '@tanstack/react-query'
import { api } from '../../services/api'
import { Button } from '@chakra-ui/react'

// Add this inside the component
const autoNegotiate = useMutation({
  mutationFn: async (sessionId: string) => {
    return await api.autoNegotiate(sessionId, 8)
  },
  onSuccess: () => {
    toast({
      title: 'Negotiation completed!',
      status: 'success',
    })
    refetch()
  },
})

// Add button in the render (after OfferCard)
<Button
  onClick={() => autoNegotiate.mutate(session.session_id)}
  isLoading={autoNegotiate.isPending}
  colorScheme="blue"
  size="sm"
>
  🤖 Auto-Negotiate
</Button>
```

### Option B: Switch to Live Theater Page

**Replace the existing component with the new live one:**

Update `/frontend/src/routes/index.tsx`:

```typescript
// Change import from:
import { NegotiationTheater } from '../pages/buyer/NegotiationTheater'

// To:
import { NegotiationTheaterLive } from '../pages/buyer/NegotiationTheaterLive'

// Change route from:
<Route path=":requestId/negotiate" element={<NegotiationTheater />} />

// To:
<Route path=":requestId/negotiate" element={<NegotiationTheaterLive />} />
```

---

## Test It Right Now (Backend API)

**You don't even need the frontend! Test with cURL:**

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST 'http://localhost:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"buyer@test.com","password":"password123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Create a request
curl -X POST 'http://localhost:8000/requests' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "description": "100 Slack licenses for team",
    "request_type": "saas",
    "quantity": 100,
    "budget_max": 150000,
    "must_haves": ["SSO", "API"]
  }' | jq '.'

# Note the request_id from response

# 3. Start sourcing (creates negotiation sessions)
curl -X POST "http://localhost:8000/sourcing/start/req-YOUR-ID-HERE" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Note one of the session_ids from response

# 4. TRIGGER AI NEGOTIATION! 🎉
curl -X POST "http://localhost:8000/negotiations/neg-YOUR-SESSION-ID/auto-negotiate" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"max_rounds": 8}' | jq '.'

# You'll see the full negotiation result!
```

**What you'll see in the response:**
```json
{
  "session_id": "neg-abc123",
  "status": "completed",
  "outcome": "accepted",
  "rounds_completed": 5,
  "final_offer": {
    "offer_id": "offer-xyz",
    "unit_price": 98.50,
    "term_months": 24,
    "payment_terms": "net_30",
    "utility": 0.85,
    "tco": 118200
  }
}
```

**This proves the AI negotiation IS WORKING!** 🎉

---

## Current Flow Diagram

```
User Creates Request
    ↓
Clicks "Launch AI Sourcing"
    ↓
POST /sourcing/start/{request_id}
    → Creates negotiation sessions
    → Sets status to "negotiating"
    ↓
User navigates to Negotiation Theater
URL: /requests/{requestId}/negotiate
    ↓
Frontend loads NegotiationTheater component
    → Shows mock data from demo endpoint
    ⚠️  NOT using real AI yet
    ↓
[MANUAL STEP NEEDED]
User must manually trigger AI:
    → Option A: Add button to call auto-negotiate API
    → Option B: Use cURL to call API directly
    → Option C: Switch to NegotiationTheaterLive component
```

---

## Why Demo Data Shows Instead of Real Negotiations

**The issue is in the API call:**

```typescript
// In NegotiationTheater.tsx line 18
const { data: sessions } = useQuery({
  queryKey: ['negotiations', requestId],
  queryFn: async () => {
    if (!requestId) return []
    return await api.getNegotiationsForRequest(requestId)  // ← HERE
  },
})

// In api.ts line 179
async getNegotiationsForRequest(requestId: string) {
  if (DEMO) {  // ← DEMO mode is TRUE
    // Returns mock data
    const response = await this.client.get(
      `/demo/negotiations/request/${requestId}`  // ← DEMO ENDPOINT
    )
    return response.data
  }
  // Real endpoint (not reached because DEMO=true)
  const response = await this.client.get(`/negotiations/request/${requestId}`)
  return response.data
}
```

**Solution:** Turn off demo mode or use real endpoint

```bash
# In frontend/.env
VITE_DEMO_MODE=false  # ← Change this
```

OR update `api.ts` to always use real endpoint.

---

## What Happens When You Call Auto-Negotiate

```
POST /negotiations/{session_id}/auto-negotiate
    ↓
Backend loads:
  - Request from database
  - Vendor from database
  - Creates BuyerAgent
  - Creates SellerAgent (simulated)
    ↓
Negotiation Engine runs:
    ↓
Round 1:
  - Buyer: Analyze vendor, choose strategy (PRICE_ANCHOR)
  - Buyer: Generate opening offer ($95/user, 12 months)
  - Seller: Counter with ($108/user, 12 months)
  - Check: Should accept? NO (utility too low)
    ↓
Round 2:
  - Buyer: New strategy (TERM_TRADE)
  - Buyer: Offer ($98/user, 24 months) - "Give discount for commitment"
  - Seller: Accept ($98/user, 24 months with 5% multi-year discount)
  - Check: Should accept? YES (utility 0.85 > threshold 0.70)
    ↓
DONE! Save to database:
  - Final offer created
  - Negotiation status = "completed"
  - Return result to frontend
```

**All this happens in ~2-3 seconds!**

---

## Summary

**✅ What's Working:**
- AI negotiation engine (1,304 lines of sophisticated logic)
- Auto-negotiate API endpoint
- WebSocket infrastructure
- Database persistence
- Live feed component (NegotiationTheaterLive)

**⚠️ What's Not Connected:**
- Frontend still shows demo data
- Manual trigger needed (no automatic negotiation after sourcing)
- Live theater component not in routes

**🎯 Quick Fix to See It:**
1. Turn off DEMO mode in `.env`
2. Add "Auto-Negotiate" button to current page
3. OR switch routes to use `NegotiationTheaterLive`

**Want me to make any of these changes for you?**

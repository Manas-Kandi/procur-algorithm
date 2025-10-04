#!/bin/bash
# Test the complete sourcing and negotiation flow

echo "=== Testing Procur Sourcing Flow ==="
echo ""

# 1. Login and get token
echo "1. Logging in..."
TOKEN=$(curl -s -X POST 'http://localhost:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"buyer@test.com","password":"password123"}' | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  echo "❌ Login failed"
  exit 1
fi
echo "✅ Login successful"
echo ""

# 2. Create a new request
echo "2. Creating purchase request..."
REQUEST_ID=$(curl -s -X POST "http://localhost:8000/requests" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description":"Test CRM for 100 seats",
    "request_type":"saas",
    "quantity":100,
    "budget_max":50000,
    "must_haves":["SSO"],
    "compliance_requirements":["SOC2"]
  }' | jq -r '.request_id')

if [ -z "$REQUEST_ID" ] || [ "$REQUEST_ID" = "null" ]; then
  echo "❌ Request creation failed"
  exit 1
fi
echo "✅ Request created: $REQUEST_ID"
echo ""

# 3. Start negotiations
echo "3. Starting negotiations with vendors..."
SESSIONS=$(curl -s -X POST "http://localhost:8000/sourcing/start/$REQUEST_ID" \
  -H "Authorization: Bearer $TOKEN")

SESSION_COUNT=$(echo "$SESSIONS" | jq 'length')
if [ "$SESSION_COUNT" -eq 0 ]; then
  echo "❌ No sessions created"
  echo "Response: $SESSIONS"
  exit 1
fi
echo "✅ Created $SESSION_COUNT negotiation sessions"
echo ""

# 4. Wait for background tasks to start
echo "4. Waiting 3 seconds for background negotiations to start..."
sleep 3
echo ""

# 5. Check session data
echo "5. Fetching negotiation sessions..."
FETCHED_SESSIONS=$(curl -s -X GET "http://localhost:8000/negotiations/request/$REQUEST_ID" \
  -H "Authorization: Bearer $TOKEN")

FETCHED_COUNT=$(echo "$FETCHED_SESSIONS" | jq 'length')
if [ "$FETCHED_COUNT" -eq 0 ]; then
  echo "❌ No sessions found (not persisted)"
  exit 1
fi
echo "✅ Found $FETCHED_COUNT sessions"
echo ""

# 6. Show first session details
echo "6. Sample session data:"
echo "$FETCHED_SESSIONS" | jq '.[0] | {session_id, status, vendor_id, current_round, total_messages}'
echo ""

echo "=== ✅ All tests passed! ==="
echo ""
echo "Next steps:"
echo "1. Check your backend console for [Background] logs"
echo "2. Open frontend and navigate to /negotiations/$REQUEST_ID"
echo "3. Watch live negotiation updates via WebSocket"

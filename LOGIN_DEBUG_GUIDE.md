# Login Blank Screen - Debugging Guide

## Issue
After entering credentials and clicking "Sign in", the screen goes blank.

## What I Fixed

### 1. Added Error Handling to Dashboard
**File**: `frontend/src/pages/buyer/Dashboard.tsx`

**Changes**:
- Added loading states for API queries
- Added error states with retry button
- Shows helpful error messages when backend is unreachable

### 2. Added Global Error Boundary
**File**: `frontend/src/components/ErrorBoundary.tsx` (NEW)

**Features**:
- Catches React errors globally
- Shows user-friendly error screen
- Provides "Reload" and "Clear Cache" options
- Displays error details for debugging

### 3. Wrapped App with Error Boundary
**File**: `frontend/src/main.tsx`

**Change**: Added `<ErrorBoundary>` wrapper around the entire app

---

## How to Debug the Blank Screen

### Step 1: Open Browser DevTools

**Chrome/Edge**:
- Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
- Press `Cmd+Option+I` (Mac)

**Firefox**:
- Press `F12` or `Ctrl+Shift+K`

### Step 2: Check Console Tab

Look for error messages in red. Common errors:

#### Error 1: "Failed to fetch" or "Network Error"
**Cause**: Backend API is not running

**Solution**:
```bash
# In terminal, start the backend
python run_api.py

# Should see:
# Starting Procur API v1.0.0
# Uvicorn running on http://0.0.0.0:8000
```

#### Error 2: "401 Unauthorized"
**Cause**: Login failed - user doesn't exist or wrong password

**Solution**:
```bash
# Re-run seeding script to create test users
python scripts/seed_demo_data.py

# Test credentials:
# buyer@test.com / password123
# seller@apollocrm.com / password123
```

#### Error 3: "CORS policy blocked"
**Cause**: Backend CORS settings don't allow frontend URL

**Solution**:
Check backend `.env` file:
```bash
PROCUR_API_CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

Restart backend after changing.

#### Error 4: "Cannot read property 'X' of undefined"
**Cause**: Dashboard trying to access missing data

**With my fix**: Should now show error screen instead of blank

---

### Step 3: Check Network Tab

1. Go to "Network" tab in DevTools
2. Login again
3. Look for failed requests (red text)

#### Check Login Request

Find: `POST /auth/login`

**If Status = 200** ✅
- Login succeeded
- Check response for `access_token`

**If Status = 401** ❌
- Wrong credentials
- User doesn't exist
- Check request body has `username` and `password`

**If Status = 500** ❌
- Backend error
- Check backend terminal for stack trace

**If "Failed" or no status** ❌
- Backend not running
- CORS issue
- Network problem

#### Check Dashboard Requests

After login, look for:
- `GET /auth/me` - Should return user data
- `GET /dashboard/metrics` - Should return metrics
- `GET /requests` - Should return requests

**If any fail**: That's causing the blank screen

---

### Step 4: Check Application Tab

1. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
2. Expand "Local Storage"
3. Click on your site URL

**Check for**:
- `auth_token` - Should contain a long JWT string
- `auth-storage` - Zustand persisted state

**If missing**: Login didn't complete successfully

---

## Quick Diagnostics

### Test 1: Backend Health Check

```bash
# In terminal or browser
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"..."}
```

**If fails**: Backend not running

### Test 2: Login API Directly

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"buyer@test.com","password":"password123"}'

# Should return:
# {"access_token":"eyJ...","token_type":"bearer"}
```

**If fails**: Check backend logs

### Test 3: Dashboard Metrics

```bash
# Replace <TOKEN> with access_token from Test 2
curl http://localhost:8000/dashboard/metrics \
  -H "Authorization: Bearer <TOKEN>"

# Should return metrics JSON
```

**If fails**: Metrics endpoint has issues

---

## Common Scenarios & Solutions

### Scenario 1: Blank Screen Immediately After Login

**Symptoms**:
- Login button worked
- Screen went blank
- No error message

**Likely Cause**: Dashboard failed to load

**Check**:
1. Open DevTools Console
2. With my fix, you should now see either:
   - "Loading dashboard..." spinner
   - "Failed to load dashboard" error with retry button

**Solution**:
- If loading forever: Backend not responding
- If error shown: Follow error message instructions

---

### Scenario 2: "Failed to load dashboard"

**With My Fix**: You'll see this error screen with details

**Solution**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Check backend logs for errors
3. Click "Retry" button
4. If still fails, restart backend

---

### Scenario 3: Login Button Does Nothing

**Symptoms**:
- Click "Sign in"
- Button shows loading state
- Nothing happens

**Check Console for**:
- Network errors
- CORS errors
- 401 Unauthorized

**Solution**:
- Ensure backend running
- Check CORS settings
- Verify credentials

---

### Scenario 4: "Cannot read property..." errors

**Before My Fix**: Blank screen
**After My Fix**: Error boundary catches it and shows error screen

**Solution**:
1. Click "Clear Cache & Go to Login"
2. Login again
3. If persists, check backend data

---

## Step-by-Step Resolution

### If Backend Not Running

```bash
# Terminal 1
cd /Users/manaskandimalla/Desktop/Projects/procur-2
python run_api.py

# Should see startup messages
# Keep this running
```

### If Backend Running But Blank Screen

```bash
# Check backend logs
# Look for errors when you login

# Check database connection
python -c "from procur.db.session import get_session; next(get_session())"

# Should not error
```

### If Users Don't Exist

```bash
# Re-seed database
python scripts/seed_demo_data.py

# Should see:
# ✓ Created buyer: buyer@test.com / password123
# ✓ Created seller: seller@apollocrm.com / password123
```

### If CORS Error

**Edit**: `/Users/manaskandimalla/Desktop/Projects/procur-2/.env`

```bash
# Add or update this line
PROCUR_API_CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000
```

**Restart backend** after changing.

---

## Expected Behavior After Fix

### During Login
1. Enter credentials
2. Click "Sign in"
3. Button shows "Signing in..." (loading state)
4. One of:
   - Success: Redirect to dashboard
   - Error: Red error message appears

### After Login
1. **Loading State**: Shows spinner with "Loading dashboard..."
2. **Success**: Dashboard appears with metrics
3. **Error**: Shows error screen with:
   - Error message
   - Retry button
   - Helpful instructions

### No More Blank Screen!

---

## Detailed Error Messages

With my fixes, you'll see helpful errors instead of blank screen:

### Loading State
```
[Spinner Animation]
Loading dashboard...
```

### Network Error
```
Failed to load dashboard

Unable to connect to the backend.
Please ensure the API server is running.

[Retry Button]
```

### API Error
```
Failed to load dashboard

Request failed with status code 500

[Retry Button]
```

### React Error (Error Boundary)
```
Something went wrong

TypeError: Cannot read property 'map' of undefined

[Reload Page] [Clear Cache & Go to Login]

▶ Error Details (expandable)
```

---

## Testing the Fix

### Test 1: Backend Down

1. Stop backend (`Ctrl+C` in terminal running API)
2. Login to frontend
3. **Expected**:
   - Loading spinner briefly
   - Then error: "Unable to connect to the backend..."
   - Retry button visible

### Test 2: Backend Up

1. Start backend: `python run_api.py`
2. Seed data: `python scripts/seed_demo_data.py`
3. Login: `buyer@test.com` / `password123`
4. **Expected**:
   - Loading spinner briefly
   - Dashboard loads with metrics
   - No blank screen!

### Test 3: Wrong Credentials

1. Login with: `wrong@email.com` / `wrongpass`
2. **Expected**:
   - Login page shows red error: "Login failed"
   - Stays on login page
   - No blank screen

---

## Backend Startup Checklist

Before testing frontend, ensure:

- [ ] Backend running: `python run_api.py`
- [ ] See: "Uvicorn running on http://0.0.0.0:8000"
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] Database connection OK (no errors in backend logs)
- [ ] Test users exist (or run `python scripts/seed_demo_data.py`)

---

## Frontend Startup Checklist

Before testing login:

- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] See: "Local: http://localhost:5173"
- [ ] `.env` file exists with `VITE_API_BASE_URL=http://localhost:8000`
- [ ] Open browser to http://localhost:5173
- [ ] DevTools open (F12)
- [ ] Console tab visible
- [ ] Network tab visible

---

## Verification Commands

Run these to verify everything is ready:

```bash
# 1. Check backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}

# 2. Check frontend can reach backend
curl -I http://localhost:5173
# Expected: HTTP/1.1 200 OK

# 3. Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"buyer@test.com","password":"password123"}'
# Expected: {"access_token":"..."}

# 4. Test dashboard (use token from step 3)
curl http://localhost:8000/dashboard/metrics \
  -H "Authorization: Bearer <YOUR_TOKEN>"
# Expected: {...metrics...}
```

If all 4 pass, frontend login should work!

---

## What to Look For Now

With error handling added, you should see **one of these** instead of blank screen:

### Scenario A: Everything Works ✅
```
[Dashboard loads with metrics]
```

### Scenario B: Backend Down ⚠️
```
Failed to load dashboard
Unable to connect to the backend.
Please ensure the API server is running.
[Retry]
```

### Scenario C: Login Failed ❌
```
[Login page with red error]
Login failed
```

### Scenario D: React Error 🔴
```
Something went wrong
[Error message]
[Reload Page] [Clear Cache]
```

---

## Next Steps

1. **Try logging in now** with the fixes applied
2. **Check what you see**:
   - Loading spinner? ✅ Good
   - Error message? Follow instructions in error
   - Blank screen? Send me console errors

3. **If still blank**, run:
```bash
# Open browser console and paste this
console.log('Auth State:', localStorage.getItem('auth-storage'))
console.log('Token:', localStorage.getItem('auth_token'))
```

Send me the output.

---

## Contact Info

If still stuck, provide:
1. Screenshot of browser console (errors in red)
2. Screenshot of network tab (failed requests)
3. Backend terminal output
4. What you see on screen

---

**The blank screen should now show helpful error messages!** 🎯

# Comprehensive Error Fix Guide

This guide addresses all the errors you encountered in your console and terminal.

## Issues Identified

1. **CORS Error**: Frontend at `http://localhost:5173` blocked from accessing backend
2. **Database Schema Mismatch**: `offers.negotiation_session_id` column missing
3. **Missing API Keys**: Environment variables not loaded
4. **bcrypt Warning**: Version compatibility issue

## Fixes Applied

### 1. Environment Variable Loading ✅

**File**: `run_api.py`
- Added `python-dotenv` import and explicit `.env` file loading
- Environment variables now load before API starts

**File**: `.env.example`
- Added `NVIDIA_API_KEY` and `OPENAI_API_KEY` placeholders
- Updated CORS origins to include `http://localhost:5173` and `http://localhost:5177`

### 2. Database Schema Fix ✅

**File**: `alembic/versions/20251005_fix_offers_schema.py`
- Created new migration to align `offers` table with `OfferRecord` model
- Adds missing `negotiation_session_id` column with foreign key constraint
- Removes obsolete columns and adds all new columns from the model

### 3. CORS Configuration ✅

**File**: `src/procur/api/config.py`
- Default CORS origins already include `http://localhost:5173`
- Configuration properly loads from environment variables

### 4. bcrypt Compatibility ✅

**File**: `pyproject.toml`
- Added explicit `bcrypt>=4.0.0` dependency
- Ensures compatibility with latest passlib

## Steps to Apply Fixes

### Option 1: Automated Fix (Recommended)

```bash
# Make the script executable
chmod +x scripts/fix_all_errors.sh

# Run the fix script
./scripts/fix_all_errors.sh
```

### Option 2: Manual Steps

```bash
# 1. Kill existing processes
lsof -ti:8000,8001,5173,3000 | xargs kill -9
pkill -f uvicorn

# 2. Upgrade bcrypt
pip install --upgrade bcrypt>=4.0.0

# 3. Run database migration
alembic upgrade head

# 4. Verify your .env file exists and has API keys
# Copy from .env.example if needed:
cp .env.example .env
# Then edit .env and add your actual API keys
```

## Required: Update Your .env File

Make sure your `.env` file (in the project root) contains:

```bash
# LLM Configuration (REQUIRED for auto-negotiation)
NVIDIA_API_KEY=your-actual-nvidia-api-key-here
# OR
OPENAI_API_KEY=your-actual-openai-api-key-here

# CORS Settings (should include your frontend URL)
PROCUR_API_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:5177","http://localhost:8000"]

# Database settings (adjust if needed)
PROCUR_DB_HOST=localhost
PROCUR_DB_PORT=5432
PROCUR_DB_DATABASE=procur
PROCUR_DB_USERNAME=procur_user
PROCUR_DB_PASSWORD=procur_password
```

## Starting the Application

After applying fixes:

```bash
# Terminal 1: Start API server
python run_api.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

## Verification

1. **API Server**: Should show "Loaded environment variables from..." message
2. **Database**: Migration should complete without errors
3. **Frontend**: Should connect to backend without CORS errors
4. **Auto-negotiation**: Should work without API key errors

## Troubleshooting

### If you still see CORS errors:
- Check that API is running on port 8000
- Verify frontend is on port 5173
- Check browser console for the exact origin being blocked

### If database errors persist:
```bash
# Check current migration status
alembic current

# View migration history
alembic history

# If needed, downgrade and re-upgrade
alembic downgrade -1
alembic upgrade head
```

### If API key errors persist:
```bash
# Verify environment variables are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print('NVIDIA_API_KEY:', 'SET' if os.getenv('NVIDIA_API_KEY') else 'NOT SET')"
```

### If bcrypt warning persists:
```bash
# Reinstall bcrypt
pip uninstall bcrypt passlib -y
pip install bcrypt>=4.0.0 passlib[bcrypt]>=1.7
```

## Summary of Changes

| File | Change | Purpose |
|------|--------|---------|
| `run_api.py` | Added dotenv loading | Load .env before API starts |
| `.env.example` | Added API keys, updated CORS | Template for required env vars |
| `alembic/versions/20251005_fix_offers_schema.py` | New migration | Fix database schema mismatch |
| `pyproject.toml` | Added bcrypt>=4.0.0 | Fix compatibility warning |
| `scripts/fix_all_errors.sh` | New script | Automated fix application |

All fixes are backward compatible and won't break existing functionality.

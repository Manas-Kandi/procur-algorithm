#!/bin/bash
# Comprehensive fix script for all Procur errors

set -e  # Exit on error

echo "🔧 Starting comprehensive error fixes..."

# 1. Kill any existing processes on ports
echo "📍 Step 1: Cleaning up existing processes..."
lsof -ti:8000,8001,5173,3000 | xargs kill -9 2>/dev/null || true
pkill -f uvicorn 2>/dev/null || true
sleep 2

# 2. Upgrade bcrypt to fix compatibility warning
echo "📍 Step 2: Upgrading bcrypt package..."
pip install --upgrade bcrypt>=4.0.0

# 3. Run database migration to fix schema
echo "📍 Step 3: Running database migration..."
alembic upgrade head

echo "✅ All fixes applied successfully!"
echo ""
echo "Next steps:"
echo "1. Ensure your .env file has NVIDIA_API_KEY or OPENAI_API_KEY set"
echo "2. Start the API server: python run_api.py"
echo "3. Start the frontend: cd frontend && npm run dev"

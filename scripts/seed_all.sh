#!/bin/bash
# Seed all test data for Procur platform

set -e

echo "🌱 Procur Database Seeding Script"
echo "=================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo "📦 Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Check if database is initialized
echo ""
echo "🔍 Checking database status..."
python3 -c "from src.procur.db.session import get_db_session; db = get_db_session(); print('✓ Database connection successful')" 2>/dev/null || {
    echo "❌ Database not initialized. Running migrations first..."
    cd "$PROJECT_ROOT"
    alembic upgrade head
}

# Run seed script
echo ""
echo "🌱 Running seed script..."
cd "$PROJECT_ROOT"
python3 scripts/seed_vendors.py

echo ""
echo "✅ Seeding complete!"

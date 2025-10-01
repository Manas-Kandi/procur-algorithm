#!/bin/bash
# Complete platform initialization script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Procur Platform Initialization      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}[1/7] Checking prerequisites...${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "  ✓ Python $PYTHON_VERSION found"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: PostgreSQL is not installed${NC}"
    echo "Install with: brew install postgresql@14 (macOS) or apt-get install postgresql (Linux)"
    exit 1
fi
echo "  ✓ PostgreSQL found"

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    echo -e "${RED}Error: Redis is not installed${NC}"
    echo "Install with: brew install redis (macOS) or apt-get install redis-server (Linux)"
    exit 1
fi
echo "  ✓ Redis found"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}  ! .env file not found, copying from .env.example${NC}"
    cp .env.example .env
    echo -e "${YELLOW}  ! Please edit .env with your configuration before continuing${NC}"
    read -p "Press Enter to continue after editing .env..."
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check services are running
echo ""
echo -e "${YELLOW}[2/7] Checking services...${NC}"

# Check PostgreSQL
if ! pg_isready -h ${PROCUR_DB_HOST:-localhost} -p ${PROCUR_DB_PORT:-5432} > /dev/null 2>&1; then
    echo -e "${RED}Error: PostgreSQL is not running${NC}"
    echo "Start with: brew services start postgresql@14 (macOS) or systemctl start postgresql (Linux)"
    exit 1
fi
echo "  ✓ PostgreSQL is running"

# Check Redis
if ! redis-cli -h ${PROCUR_EVENT_REDIS_HOST:-localhost} -p ${PROCUR_EVENT_REDIS_PORT:-6379} ping > /dev/null 2>&1; then
    echo -e "${RED}Error: Redis is not running${NC}"
    echo "Start with: brew services start redis (macOS) or systemctl start redis (Linux)"
    exit 1
fi
echo "  ✓ Redis is running"

# Install Python dependencies
echo ""
echo -e "${YELLOW}[3/7] Installing Python dependencies...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✓ Virtual environment created"
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -e .
echo "  ✓ Dependencies installed"

# Setup database
echo ""
echo -e "${YELLOW}[4/7] Setting up database...${NC}"
bash scripts/setup_database.sh

# Run migrations
echo ""
echo -e "${YELLOW}[5/7] Running database migrations...${NC}"
alembic upgrade head
echo "  ✓ Migrations applied"

# Initialize data (optional)
echo ""
echo -e "${YELLOW}[6/7] Initializing seed data...${NC}"
if [ -f "scripts/seed_data.py" ]; then
    python scripts/seed_data.py
    echo "  ✓ Seed data loaded"
else
    echo "  ⊘ No seed data script found (optional)"
fi

# Verify installation
echo ""
echo -e "${YELLOW}[7/7] Verifying installation...${NC}"

# Test database connection
python -c "
from src.procur.db import get_session
try:
    with get_session() as session:
        session.execute('SELECT 1')
    print('  ✓ Database connection successful')
except Exception as e:
    print(f'  ✗ Database connection failed: {e}')
    exit(1)
"

# Test Redis connection
python -c "
from src.procur.events.bus import get_event_bus
try:
    bus = get_event_bus()
    bus.redis_client.ping()
    print('  ✓ Redis connection successful')
except Exception as e:
    print(f'  ✗ Redis connection failed: {e}')
    exit(1)
"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Platform Initialization Complete!   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo -e "  ${GREEN}1.${NC} Start the API server:"
echo -e "     ${YELLOW}python run_api.py${NC}"
echo ""
echo -e "  ${GREEN}2.${NC} Start Celery workers (in another terminal):"
echo -e "     ${YELLOW}bash scripts/start_workers.sh${NC}"
echo ""
echo -e "  ${GREEN}3.${NC} Start Flower monitoring (optional):"
echo -e "     ${YELLOW}bash scripts/start_flower.sh${NC}"
echo ""
echo -e "  ${GREEN}4.${NC} Run tests:"
echo -e "     ${YELLOW}pytest tests/integration/ -v${NC}"
echo ""
echo -e "  ${GREEN}5.${NC} Access the API:"
echo -e "     ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "  ${GREEN}6.${NC} Monitor workers:"
echo -e "     ${YELLOW}http://localhost:5555${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  • Operational Setup: ${YELLOW}OPERATIONAL_SETUP.md${NC}"
echo -e "  • API Reference: ${YELLOW}API_README.md${NC}"
echo -e "  • Database Schema: ${YELLOW}DATABASE_README.md${NC}"
echo ""

#!/bin/bash
# Quickstart script for Procur-2 development environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Procur-2 Quickstart Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if we're in the project root
if [ ! -f "run_api.py" ]; then
    echo -e "${RED}Error: Must be run from project root directory${NC}"
    exit 1
fi

# Step 1: Check Python environment
echo -e "${BLUE}[1/6] Checking Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "${GREEN}✓ Python environment ready${NC}\n"

# Step 2: Install backend dependencies
echo -e "${BLUE}[2/6] Installing backend dependencies...${NC}"
pip install -q -e .
echo -e "${GREEN}✓ Backend dependencies installed${NC}\n"

# Step 3: Check database
echo -e "${BLUE}[3/6] Checking database...${NC}"
if ! python -c "from procur.db.session import get_session; next(get_session())" 2>/dev/null; then
    echo -e "${YELLOW}Database connection failed. Please ensure PostgreSQL is running and DATABASE_URL is set in .env${NC}"
    echo -e "${YELLOW}Continuing anyway (some features may not work)...${NC}"
else
    echo -e "${GREEN}✓ Database connection successful${NC}"
fi
echo ""

# Step 4: Run migrations
echo -e "${BLUE}[4/6] Running database migrations...${NC}"
if command -v alembic &> /dev/null; then
    alembic upgrade head || echo -e "${YELLOW}Warning: Migration failed${NC}"
    echo -e "${GREEN}✓ Migrations complete${NC}"
else
    echo -e "${YELLOW}Alembic not found, skipping migrations${NC}"
fi
echo ""

# Step 5: Seed demo data
echo -e "${BLUE}[5/6] Seeding demo data...${NC}"
if [ -f "scripts/seed_demo_data.py" ]; then
    python scripts/seed_demo_data.py || echo -e "${YELLOW}Warning: Seeding failed${NC}"
else
    echo -e "${YELLOW}Seed script not found, skipping...${NC}"
fi
echo ""

# Step 6: Frontend setup
echo -e "${BLUE}[6/6] Setting up frontend...${NC}"
if [ -d "frontend" ]; then
    cd frontend

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies (this may take a minute)...${NC}"
        npm install -q
    else
        echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
    fi

    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Creating frontend .env file...${NC}"
        cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_DEMO_MODE=false
EOF
        echo -e "${GREEN}✓ Frontend .env created${NC}"
    fi

    cd ..
    echo -e "${GREEN}✓ Frontend ready${NC}"
else
    echo -e "${YELLOW}Frontend directory not found, skipping...${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${BLUE}Next steps:${NC}"
echo ""
echo -e "  ${YELLOW}1. Start the backend:${NC}"
echo -e "     ${GREEN}python run_api.py${NC}"
echo -e "     → API at http://localhost:8000"
echo -e "     → Docs at http://localhost:8000/docs"
echo ""
echo -e "  ${YELLOW}2. Start the frontend (in a new terminal):${NC}"
echo -e "     ${GREEN}cd frontend && npm run dev${NC}"
echo -e "     → App at http://localhost:5173"
echo ""
echo -e "${BLUE}Test credentials:${NC}"
echo -e "  Buyer:  ${GREEN}buyer@test.com${NC} / ${GREEN}test123${NC}"
echo -e "  Seller: ${GREEN}seller@apollocrm.com${NC} / ${GREEN}test123${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  → FRONTEND_BACKEND_INTEGRATION.md"
echo -e "  → API docs: http://localhost:8000/docs"
echo ""

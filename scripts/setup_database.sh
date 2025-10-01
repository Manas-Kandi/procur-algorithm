#!/bin/bash
# Database setup script for Procur platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Procur Database Setup ===${NC}"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}Warning: .env file not found, using defaults${NC}"
fi

# Database configuration
DB_HOST=${PROCUR_DB_HOST:-localhost}
DB_PORT=${PROCUR_DB_PORT:-5432}
DB_NAME=${PROCUR_DB_DATABASE:-procur}
DB_USER=${PROCUR_DB_USERNAME:-procur_user}
DB_PASSWORD=${PROCUR_DB_PASSWORD:-procur_password}

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"

# Check if PostgreSQL is running
if ! pg_isready -h $DB_HOST -p $DB_PORT > /dev/null 2>&1; then
    echo -e "${RED}Error: PostgreSQL is not running on $DB_HOST:$DB_PORT${NC}"
    echo "Please start PostgreSQL and try again."
    exit 1
fi

echo -e "${GREEN}PostgreSQL is running${NC}"

# Detect PostgreSQL superuser (macOS uses system username, Linux uses 'postgres')
if psql -h $DB_HOST -p $DB_PORT -U postgres -d postgres -c '\q' 2>/dev/null; then
    PG_SUPERUSER="postgres"
    PG_DEFAULT_DB="postgres"
else
    PG_SUPERUSER=$(whoami)
    PG_DEFAULT_DB="postgres"
    echo "Using system user '$PG_SUPERUSER' as PostgreSQL superuser (macOS default)"
fi

# Create database user if it doesn't exist
echo "Creating database user..."
psql -h $DB_HOST -p $DB_PORT -U $PG_SUPERUSER -d $PG_DEFAULT_DB -tc "SELECT 1 FROM pg_user WHERE usename = '$DB_USER'" | grep -q 1 || \
    psql -h $DB_HOST -p $DB_PORT -U $PG_SUPERUSER -d $PG_DEFAULT_DB -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

# Create database if it doesn't exist
echo "Creating database..."
psql -h $DB_HOST -p $DB_PORT -U $PG_SUPERUSER -d $PG_DEFAULT_DB -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    psql -h $DB_HOST -p $DB_PORT -U $PG_SUPERUSER -d $PG_DEFAULT_DB -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Grant privileges
echo "Granting privileges..."
psql -h $DB_HOST -p $DB_PORT -U $PG_SUPERUSER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
psql -h $DB_HOST -p $DB_PORT -U $PG_SUPERUSER -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

echo -e "${GREEN}Database setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Run migrations: alembic upgrade head"
echo "  2. Start the API: python run_api.py"

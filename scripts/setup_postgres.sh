#!/bin/bash
# Setup PostgreSQL database for Procur

set -e

DB_NAME="${PROCUR_DB_DATABASE:-procur}"
DB_USER="${PROCUR_DB_USERNAME:-procur_user}"
DB_PASSWORD="${PROCUR_DB_PASSWORD:-procur_password}"

echo "Setting up PostgreSQL database for Procur..."
echo "Database: $DB_NAME"
echo "User: $DB_USER"

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Create database user
echo "Creating database user..."
psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User already exists"

# Create database
echo "Creating database..."
psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || echo "Database already exists"

# Grant privileges
echo "Granting privileges..."
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "✅ PostgreSQL setup complete!"
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""
echo "Connection string:"
echo "  postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"

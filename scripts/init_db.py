#!/usr/bin/env python
"""Initialize the database with tables and seed data."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from procur.db import init_db


def main():
    """Initialize database."""
    print("Initializing Procur database...")
    
    try:
        db = init_db(create_tables=True)
        print("✅ Database initialized successfully!")
        print(f"   Connection: {db.config.host}:{db.config.port}/{db.config.database}")
        print("\nNext steps:")
        print("1. Run migrations: alembic upgrade head")
        print("2. Create a user account")
        print("3. Start using the platform!")
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

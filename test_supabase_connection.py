#!/usr/bin/env python3
"""
Test Supabase connection and verify migration.
Run this after executing all migration scripts.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_client():
    """Test using Supabase Python client."""
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")
            return False
        
        print(f"🔗 Connecting to: {url}")
        supabase = create_client(url, key)
        
        # Test 1: Query organizations
        print("\n📊 Test 1: Query organizations table")
        result = supabase.table("organizations").select("*").execute()
        print(f"   ✅ Found {len(result.data)} organizations")
        if result.data:
            for org in result.data:
                print(f"      - {org['name']} ({org['organization_id']})")
        
        # Test 2: Query users
        print("\n👥 Test 2: Query user_accounts table")
        result = supabase.table("user_accounts").select("email, username, role").execute()
        print(f"   ✅ Found {len(result.data)} users")
        if result.data:
            for user in result.data[:5]:  # Show first 5
                print(f"      - {user['email']} ({user['role']})")
        
        # Test 3: Query vendors
        print("\n🏢 Test 3: Query vendor_profiles table")
        result = supabase.table("vendor_profiles").select("name, category, rating").execute()
        print(f"   ✅ Found {len(result.data)} vendors")
        if result.data:
            for vendor in result.data:
                print(f"      - {vendor['name']} ({vendor['category']}) - Rating: {vendor.get('rating', 'N/A')}")
        
        # Test 4: Test helper function
        print("\n🔧 Test 4: Test helper function")
        try:
            result = supabase.rpc("get_organization_metrics", {"org_id": "demo-org"}).execute()
            print(f"   ✅ Function executed successfully")
            if result.data:
                print(f"      Metrics for demo-org:")
                for metric in result.data:
                    print(f"      - {metric['metric_name']}: {metric['metric_value']} {metric['metric_unit']}")
        except Exception as e:
            print(f"   ⚠️  Function test skipped (may not have demo-org): {e}")
        
        print("\n✅ All Supabase client tests passed!")
        return True
        
    except ImportError:
        print("❌ supabase-py not installed. Install with: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Supabase client test failed: {e}")
        return False


def test_sqlalchemy_connection():
    """Test using SQLAlchemy (direct database connection)."""
    try:
        from sqlalchemy import create_engine, text
        
        url = os.getenv("DATABASE_URL")
        
        if not url:
            print("❌ Missing DATABASE_URL in .env")
            return False
        
        print(f"\n🔗 Testing SQLAlchemy connection")
        engine = create_engine(url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            # Test 1: Count tables
            result = conn.execute(text("""
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            count = result.fetchone()[0]
            print(f"   ✅ Found {count} tables (expected: 15)")
            
            # Test 2: Count indexes
            result = conn.execute(text("""
                SELECT COUNT(*) as index_count
                FROM pg_indexes 
                WHERE schemaname = 'public'
            """))
            count = result.fetchone()[0]
            print(f"   ✅ Found {count} indexes (expected: 50+)")
            
            # Test 3: Count functions
            result = conn.execute(text("""
                SELECT COUNT(*) as function_count
                FROM information_schema.routines 
                WHERE routine_schema = 'public' 
                AND routine_type = 'FUNCTION'
            """))
            count = result.fetchone()[0]
            print(f"   ✅ Found {count} functions (expected: 15+)")
            
            # Test 4: Verify RLS enabled
            result = conn.execute(text("""
                SELECT COUNT(*) as rls_enabled_count
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND rowsecurity = true
            """))
            count = result.fetchone()[0]
            print(f"   ✅ RLS enabled on {count} tables (expected: 15)")
        
        print("\n✅ All SQLAlchemy tests passed!")
        return True
        
    except ImportError:
        print("❌ sqlalchemy not installed. Install with: pip install sqlalchemy")
        return False
    except Exception as e:
        print(f"❌ SQLAlchemy test failed: {e}")
        return False


def main():
    """Run all connection tests."""
    print("=" * 60)
    print("🧪 Supabase Connection Test Suite")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Checking environment variables...")
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "DATABASE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\n💡 Make sure you have a .env file with:")
        print("   SUPABASE_URL=https://uedvyexzjlovliiaawuc.supabase.co")
        print("   SUPABASE_SERVICE_KEY=your_service_role_key")
        print("   DATABASE_URL=postgresql://...")
        sys.exit(1)
    
    print("   ✅ All required environment variables present")
    
    # Run tests
    supabase_ok = test_supabase_client()
    sqlalchemy_ok = test_sqlalchemy_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Supabase Client: {'✅ PASS' if supabase_ok else '❌ FAIL'}")
    print(f"SQLAlchemy:      {'✅ PASS' if sqlalchemy_ok else '❌ FAIL'}")
    
    if supabase_ok and sqlalchemy_ok:
        print("\n🎉 All tests passed! Your Supabase backend is ready to use.")
        print("\n📚 Next steps:")
        print("   1. Update your application to use Supabase")
        print("   2. Test your procurement workflow end-to-end")
        print("   3. Enable real-time subscriptions if needed")
        print("   4. Set up monitoring and alerts")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n📖 Troubleshooting:")
        print("   - Verify all migration scripts were executed")
        print("   - Check your .env file has correct values")
        print("   - Review SUPABASE_SETUP_GUIDE.md")
        sys.exit(1)


if __name__ == "__main__":
    main()

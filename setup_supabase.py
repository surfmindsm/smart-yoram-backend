import os
import sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
    sys.exit(1)

print(f"Connecting to Supabase project: {supabase_url}")

# Initialize Supabase client
supabase = create_client(supabase_url, supabase_key)

print("\n📋 Database Setup Instructions:")
print("=" * 50)
print("\nSince we cannot connect directly to the database from this network,")
print("please follow these steps to set up your database:\n")

print("1. Go to your Supabase dashboard")
print(f"   URL: {supabase_url}")
print("")
print("2. Navigate to the SQL Editor")
print("   (It's in the left sidebar)")
print("")
print("3. Copy and paste the contents of 'supabase_schema.sql'")
print("   This file has been created in the backend directory")
print("")
print("4. Click 'Run' to execute the SQL")
print("")
print("5. The database schema will be created with:")
print("   - churches table")
print("   - members table") 
print("   - users table (with admin user)")
print("   - attendances table")
print("   - bulletins table")
print("   - All necessary indexes and triggers")
print("")

print("\n🔐 Default Admin Credentials:")
print("   Username: admin")
print("   Password: admin123")
print("")

print("\n📡 Testing Supabase REST API connection...")
try:
    # Try to query a table (it might not exist yet)
    response = supabase.from_("churches").select("*").limit(1).execute()
    print("✅ Supabase REST API is working!")
    print(f"   Found {len(response.data)} churches")
except Exception as e:
    error_msg = str(e)
    if "relation" in error_msg and "does not exist" in error_msg:
        print("⚠️  Tables not created yet. Please run the SQL script first.")
    else:
        print(f"❌ Error: {error_msg}")

print("\n🚀 After running the SQL script, you can:")
print("1. Start the backend server: uvicorn app.main:app --reload")
print("2. The API will use Supabase REST API for now")
print("3. Direct database connections will work when IPv6 is available")

print("\n💡 Alternative: Use Pooler Connection")
print("If you need direct database access, try using the pooler connection")
print("from a cloud environment or a server with proper network configuration.")
print("The pooler connection string format is:")
print("postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres")
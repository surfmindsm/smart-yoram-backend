import os
from supabase import create_client
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Get credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
project_ref = supabase_url.split('//')[1].split('.')[0]

print(f"Project Reference: {project_ref}")
print(f"Supabase URL: {supabase_url}")

# Initialize Supabase client
supabase = create_client(supabase_url, supabase_key)

# Test if we can access the database via REST API
try:
    # Try to get tables info
    response = supabase.from_("_prisma_migrations").select("*").limit(1).execute()
    print("✓ Supabase REST API is working")
except Exception as e:
    print(f"✗ Supabase REST API error: {e}")
    # Try creating a test table
    try:
        response = supabase.from_("test_connection").select("*").limit(1).execute()
        print("✓ Connected to Supabase")
    except:
        print("Note: No tables exist yet in the database")

# Based on Supabase patterns, try these connection strings
password = "Windsurfsm24!"

print("\nTrying database connections based on Supabase patterns...")

# Most common patterns for Supabase
patterns = [
    # Standard Supabase direct connection
    f"postgresql://postgres.{project_ref}:{password}@db.{project_ref}.supabase.co:5432/postgres",
    f"postgresql://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres",
    
    # With project ID in hostname
    f"postgresql://postgres:{password}@{project_ref}.db.supabase.co:5432/postgres",
    
    # Pooler connections with regions
    f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres",
    f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres",
    f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-south-1.pooler.supabase.com:5432/postgres",
    f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres",
    
    # Try with URL encoding
    f"postgresql://postgres:{password.replace('!', '%21')}@db.{project_ref}.supabase.co:5432/postgres",
]

for i, conn_str in enumerate(patterns):
    print(f"\n{i+1}. Testing: {conn_str[:60]}...")
    try:
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), version()")
        db_name, version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"   ✓ SUCCESS! Connected to database: {db_name}")
        print(f"   PostgreSQL version: {version[:50]}...")
        print(f"\n   Add this to your .env file:")
        print(f"   DATABASE_URL={conn_str}")
        break
    except Exception as e:
        error_msg = str(e).split('\n')[0]  # Get first line of error
        print(f"   ✗ Failed: {error_msg}")
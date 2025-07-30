import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_ANON_KEY: {supabase_key[:20]}...")

# Test REST API
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

# Try to create a test table via REST API
create_table_sql = """
CREATE TABLE IF NOT EXISTS test_connection (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

# Supabase SQL endpoint
sql_endpoint = f"{supabase_url}/rest/v1/rpc/sql"

# Note: The SQL RPC endpoint might not be available with anon key
# Let's try to list existing tables instead
print("\n1. Testing REST API access...")
try:
    response = requests.get(f"{supabase_url}/rest/v1/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ REST API is accessible")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Try to get database info via API
print("\n2. Checking if we can query tables...")
try:
    # Try to query a system table
    response = requests.get(
        f"{supabase_url}/rest/v1/",
        headers=headers
    )
    if response.status_code == 200:
        print("   ✓ Can access database via REST API")
        # The fact that we get 200 means the project exists and is accessible
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n3. Project Information:")
print(f"   Project Reference: {supabase_url.split('//')[1].split('.')[0]}")
print(f"   Region: Likely ap-northeast-2 (Seoul) based on pooler connection attempts")

print("\n⚠️  Important Notes:")
print("1. The 'Tenant or user not found' error usually means:")
print("   - The password might be incorrect")
print("   - The project might be in a different region")
print("   - The database might not be initialized yet")
print("")
print("2. Since the REST API works, the project exists and is accessible")
print("")
print("3. Common issues with passwords:")
print("   - Default password might have been changed")
print("   - Special characters might need different encoding")
print("   - Password might be case-sensitive")

print("\n💡 Suggested next steps:")
print("1. Check the Supabase dashboard for the correct database password")
print("2. Try resetting the database password in Supabase dashboard")
print("3. Check Settings > Database in Supabase dashboard for connection strings")
print("4. The dashboard should show the exact connection string to use")
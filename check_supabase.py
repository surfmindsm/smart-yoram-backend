import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

print(f"SUPABASE_URL: {supabase_url}")
print(f"Project Reference: {supabase_url.split('//')[1].split('.')[0]}")

# Test API connection
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}"
}

# Try to get database settings
try:
    response = requests.get(f"{supabase_url}/rest/v1/", headers=headers)
    print(f"\nAPI Status: {response.status_code}")
    
    # Try auth endpoint
    auth_response = requests.get(f"{supabase_url}/auth/v1/health", headers=headers)
    print(f"Auth Health: {auth_response.status_code}")
    
except Exception as e:
    print(f"Error: {e}")

# Common Supabase connection patterns
project_ref = supabase_url.split('//')[1].split('.')[0]
print(f"\nPossible connection strings for project '{project_ref}':")
print(f"1. Direct (IPv4): postgresql://postgres:[PASSWORD]@db.{project_ref}.supabase.co:5432/postgres")
print(f"2. Direct (IPv6): postgresql://postgres:[PASSWORD]@[xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx]:5432/postgres")
print(f"3. Pooler Session: postgresql://postgres.{project_ref}:[PASSWORD]@aws-0-[region].pooler.supabase.com:5432/postgres")
print(f"4. Pooler Transaction: postgresql://postgres.{project_ref}:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres")
print(f"\nNote: Replace [PASSWORD] with your database password and [region] with your AWS region")
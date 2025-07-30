import psycopg2
import urllib.parse
import os

# Test different connection strings
password = "Windsurfsm24!"
encoded_password = urllib.parse.quote(password, safe="")

print(f"Original password: {password}")
print(f"URL-encoded password: {encoded_password}")

# Get project reference from SUPABASE_URL
project_ref = "adzhdsajdamrflvybhxq"

connections_to_test = [
    # Direct connection - try different regions
    f"postgresql://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres",
    f"postgresql://postgres:{encoded_password}@db.{project_ref}.supabase.co:5432/postgres",
    
    # Try with port 6543 for direct connection
    f"postgresql://postgres:{password}@db.{project_ref}.supabase.co:6543/postgres",
    
    # Pooler with different formats
    f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres",
    f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres",
    
    # Try different regions
    f"postgresql://postgres.{project_ref}:{password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
    f"postgresql://postgres.{project_ref}:{password}@aws-0-us-west-1.pooler.supabase.com:6543/postgres",
    
    # Alternative format
    f"postgres://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres",
]

for i, conn_string in enumerate(connections_to_test):
    print(f"\n{i+1}. Testing: {conn_string}")
    try:
        conn = psycopg2.connect(conn_string)
        print("   ✓ Connected successfully!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"   PostgreSQL version: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        
        print(f"\n   Use this connection string in .env:")
        print(f"   DATABASE_URL={conn_string}")
        break
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
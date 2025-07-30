import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Try different approaches based on the research
project_ref = "adzhdsajdamrflvybhxq"
password = "Windsurfsm24!"

print("Testing Supabase connections based on 2025 documentation...\n")

# Test configurations
tests = [
    {
        "name": "Pooler Transaction Mode (recommended)",
        "url": f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres",
        "note": "Uses project ref in username"
    },
    {
        "name": "Pooler Session Mode",
        "url": f"postgresql://postgres.{project_ref}:{password}@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres",
        "note": "Port 5432 for session mode"
    },
    {
        "name": "Direct Connection (IPv6)",
        "url": f"postgresql://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres",
        "note": "Direct connection - requires IPv6"
    }
]

# Also test with encoded password
encoded_password = password.replace("!", "%21")
tests.extend([
    {
        "name": "Pooler with encoded password",
        "url": f"postgresql://postgres.{project_ref}:{encoded_password}@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres",
        "note": "URL-encoded special characters"
    }
])

for test in tests:
    print(f"Testing: {test['name']}")
    print(f"Note: {test['note']}")
    print(f"URL: {test['url'][:80]}...")
    
    try:
        conn = psycopg2.connect(test['url'])
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT current_database(), current_user, version()")
        db, user, version = cursor.fetchone()
        
        print(f"✓ SUCCESS!")
        print(f"  Database: {db}")
        print(f"  User: {user}")
        print(f"  PostgreSQL: {version[:50]}...")
        
        # Test if we can create tables
        cursor.execute("SELECT 1")
        print(f"  Can execute queries: Yes")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Use this connection string in your .env:")
        print(f"DATABASE_URL={test['url']}")
        break
        
    except Exception as e:
        error_msg = str(e).replace('\n', ' ')[:100]
        print(f"✗ Failed: {error_msg}...")
        
    print("-" * 80 + "\n")
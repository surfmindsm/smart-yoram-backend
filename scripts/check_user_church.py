import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("Checking users and their church assignments:")
cur.execute("""
    SELECT id, username, email, church_id, role, is_active 
    FROM users 
    ORDER BY id
""")

users = cur.fetchall()
for user in users:
    user_id, username, email, church_id, role, is_active = user
    print(f"User {user_id}: {username} (email: {email}) - Church ID: {church_id}, Role: {role}, Active: {is_active}")

print("\nChecking churches:")
cur.execute("""
    SELECT id, name 
    FROM churches 
    ORDER BY id
""")

churches = cur.fetchall()
for church in churches:
    church_id, name = church
    print(f"Church {church_id}: {name}")

# Check worship services for church 6
print(f"\nChecking worship services for church 6:")
cur.execute("""
    SELECT id, name, location, start_time, service_type, target_group
    FROM worship_services 
    WHERE church_id = 6
    ORDER BY order_index
""")

services = cur.fetchall()
print(f"Found {len(services)} worship services:")
for service in services:
    service_id, name, location, start_time, service_type, target_group = service
    print(f"  - {name}: {location} at {start_time}")

# Close the connection
cur.close()
conn.close()
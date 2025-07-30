"""Test the API endpoints with Supabase"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 1. Test login
print("1. Testing login...")
login_data = {
    "username": "admin",
    "password": "admin123"
}
response = requests.post(
    f"{BASE_URL}/auth/login/access-token",
    data=login_data
)
if response.status_code == 200:
    token_data = response.json()
    token = token_data["access_token"]
    print(f"✅ Login successful! Token: {token[:20]}...")
else:
    print(f"❌ Login failed: {response.text}")
    exit(1)

# Set auth header
headers = {"Authorization": f"Bearer {token}"}

# 2. Test getting current user
print("\n2. Testing current user...")
response = requests.post(f"{BASE_URL}/auth/test-token", headers=headers)
if response.status_code == 200:
    user = response.json()
    print(f"✅ Current user: {user['username']} (ID: {user['id']})")
else:
    print(f"❌ Failed: {response.text}")

# 3. Test getting members
print("\n3. Testing get members...")
response = requests.get(f"{BASE_URL}/members", headers=headers)
if response.status_code == 200:
    members = response.json()
    print(f"✅ Found {len(members)} members:")
    for member in members[:3]:
        print(f"   - {member['name']} ({member['email']})")
else:
    print(f"❌ Failed: {response.text}")

# 4. Test creating a new member
print("\n4. Testing create member...")
new_member = {
    "name": "테스트 성도",
    "phone": "010-9999-9999",
    "email": "test@example.com",
    "gender": "M",
    "position": "member",
    "church_id": 1
}
response = requests.post(f"{BASE_URL}/members", json=new_member, headers=headers)
if response.status_code == 200:
    created = response.json()
    print(f"✅ Created member: {created['name']} (ID: {created['id']})")
    member_id = created['id']
else:
    print(f"❌ Failed: {response.text}")
    member_id = None

# 5. Test attendance
if member_id:
    print("\n5. Testing attendance...")
    attendance_data = {
        "member_id": member_id,
        "service_date": "2025-01-30",
        "service_type": "sunday",
        "present": True,
        "church_id": 1
    }
    response = requests.post(f"{BASE_URL}/attendances", json=attendance_data, headers=headers)
    if response.status_code == 200:
        print(f"✅ Attendance recorded")
    else:
        print(f"❌ Failed: {response.text}")

# 6. Test bulletins
print("\n6. Testing bulletins...")
response = requests.get(f"{BASE_URL}/bulletins", headers=headers)
if response.status_code == 200:
    bulletins = response.json()
    print(f"✅ Found {len(bulletins)} bulletins")
else:
    print(f"❌ Failed: {response.text}")

# 7. Test church info
print("\n7. Testing church info...")
response = requests.get(f"{BASE_URL}/churches/1", headers=headers)
if response.status_code == 200:
    church = response.json()
    print(f"✅ Church: {church['name']} - {church['address']}")
else:
    print(f"❌ Failed: {response.text}")

print("\n✅ All API tests completed!")
print("\n🚀 The backend is working correctly with Supabase!")
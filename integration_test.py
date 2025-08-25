#!/usr/bin/env python
"""Integration tests for the Smart Yoram API."""

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000/api/v1"


def test_integration():
    print("🧪 Smart Yoram Integration Test\n" + "=" * 50 + "\n")

    # 1. Login
    print("1. Testing Login...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login/access-token",
        data={"username": "admin", "password": "changeme"},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")

    # 2. Get current user
    print("\n2. Testing Get Current User...")
    user_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    assert user_response.status_code == 200
    user = user_response.json()
    print(f"✅ Current user: {user['username']} (Church ID: {user['church_id']})")

    # 3. Get church info
    print("\n3. Testing Get Church Info...")
    church_response = requests.get(f"{BASE_URL}/churches/my", headers=headers)
    assert church_response.status_code == 200
    church = church_response.json()
    print(f"✅ Church: {church['name']}")

    # 4. Get members
    print("\n4. Testing Get Members...")
    members_response = requests.get(f"{BASE_URL}/members/", headers=headers)
    assert members_response.status_code == 200
    members = members_response.json()
    print(f"✅ Found {len(members)} members")

    # 5. Create a new member
    print("\n5. Testing Create Member...")
    new_member = {
        "church_id": church["id"],
        "name": "테스트 성도",
        "phone": "010-9999-0000",
        "position": "member",
        "department": "새가족부",
        "status": "active",
    }
    create_response = requests.post(
        f"{BASE_URL}/members/", json=new_member, headers=headers
    )
    assert create_response.status_code == 200
    created_member = create_response.json()
    print(f"✅ Created member: {created_member['name']} (ID: {created_member['id']})")

    # 6. Get attendance
    print("\n6. Testing Get Attendance...")
    attendance_params = {
        "service_date": str(date.today()),
        "service_type": "sunday_morning",
    }
    attendance_response = requests.get(
        f"{BASE_URL}/attendances/", params=attendance_params, headers=headers
    )
    assert attendance_response.status_code == 200
    attendances = attendance_response.json()
    print(f"✅ Found {len(attendances)} attendance records")

    # 7. Mark attendance
    print("\n7. Testing Mark Attendance...")
    new_attendance = {
        "church_id": church["id"],
        "member_id": created_member["id"],
        "service_date": str(date.today()),
        "service_type": "sunday_morning",
        "present": True,
        "check_in_method": "manual",
    }
    attendance_create = requests.post(
        f"{BASE_URL}/attendances/", json=new_attendance, headers=headers
    )
    if attendance_create.status_code == 400:
        print("✅ Attendance already recorded (expected)")
    else:
        assert attendance_create.status_code == 200
        print("✅ Attendance marked successfully")

    # 8. Get bulletins
    print("\n8. Testing Get Bulletins...")
    bulletins_response = requests.get(f"{BASE_URL}/bulletins/", headers=headers)
    assert bulletins_response.status_code == 200
    bulletins = bulletins_response.json()
    print(f"✅ Found {len(bulletins)} bulletins")

    # 9. Create a bulletin
    print("\n9. Testing Create Bulletin...")
    new_bulletin = {
        "church_id": church["id"],
        "title": "Integration Test 주보",
        "date": str(date.today()),
        "content": "This is a test bulletin",
    }
    bulletin_create = requests.post(
        f"{BASE_URL}/bulletins/", json=new_bulletin, headers=headers
    )
    assert bulletin_create.status_code == 200
    created_bulletin = bulletin_create.json()
    print(f"✅ Created bulletin: {created_bulletin['title']}")

    # 10. Update church info
    print("\n10. Testing Update Church Info...")
    church_update = {"phone": "02-9876-5432"}
    update_response = requests.put(
        f"{BASE_URL}/churches/{church['id']}", json=church_update, headers=headers
    )
    assert update_response.status_code == 200
    print("✅ Church info updated")

    print("\n" + "=" * 50)
    print("✅ All integration tests passed!")
    print("\nAPI Endpoints tested:")
    print("- POST   /auth/login/access-token")
    print("- GET    /users/me")
    print("- GET    /churches/my")
    print("- PUT    /churches/{id}")
    print("- GET    /members/")
    print("- POST   /members/")
    print("- GET    /attendances/")
    print("- POST   /attendances/")
    print("- GET    /bulletins/")
    print("- POST   /bulletins/")


if __name__ == "__main__":
    try:
        test_integration()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API server")
        print("Make sure the backend server is running on http://localhost:8000")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

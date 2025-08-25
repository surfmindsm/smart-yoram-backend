import psycopg2
from datetime import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

church_id = 6

# Insert worship service categories
categories = [
    ("주일예배", "주일에 드리는 예배", 1),
    ("주중예배", "주중에 드리는 예배", 2),
    ("부서예배", "각 부서별 예배", 3),
    ("새벽기도회", "새벽에 드리는 기도회", 4),
]

print("Inserting worship categories...")
for name, description, order_index in categories:
    cur.execute(
        """
        INSERT INTO worship_service_categories (church_id, name, description, order_index)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """,
        (church_id, name, description, order_index),
    )

# Insert worship services
services = [
    # 주일예배
    {
        "name": "주일예배 1부",
        "location": "예루살렘성전",
        "day_of_week": 6,  # Sunday (0=Monday, 6=Sunday)
        "start_time": time(9, 0),
        "service_type": "sunday_worship",
        "target_group": "all",
        "is_online": False,
        "order_index": 1,
    },
    {
        "name": "주일예배 2부",
        "location": "예루살렘성전",
        "day_of_week": 6,
        "start_time": time(11, 0),
        "service_type": "sunday_worship",
        "target_group": "all",
        "is_online": False,
        "order_index": 2,
    },
    {
        "name": "주일예배 3부",
        "location": "예루살렘성전",
        "day_of_week": 6,
        "start_time": time(13, 30),
        "service_type": "sunday_worship",
        "target_group": "all",
        "is_online": False,
        "order_index": 3,
    },
    # 부서예배
    {
        "name": "새싹부",
        "location": "새싹부실",
        "day_of_week": 6,
        "start_time": time(11, 0),
        "service_type": "sunday_worship",
        "target_group": "children",
        "is_online": False,
        "order_index": 4,
    },
    {
        "name": "어린이부",
        "location": "어린이부실",
        "day_of_week": 6,
        "start_time": time(11, 0),
        "service_type": "sunday_worship",
        "target_group": "children",
        "is_online": False,
        "order_index": 5,
    },
    {
        "name": "청소년부",
        "location": "벧엘성전",
        "day_of_week": 6,
        "start_time": time(11, 0),
        "service_type": "sunday_worship",
        "target_group": "youth",
        "is_online": False,
        "order_index": 6,
    },
    {
        "name": "대학청년부",
        "location": "시온성전",
        "day_of_week": 6,
        "start_time": time(13, 30),
        "service_type": "sunday_worship",
        "target_group": "college",
        "is_online": False,
        "order_index": 7,
    },
    # 수요예배
    {
        "name": "수요 예배",
        "location": "예루살렘성전",
        "day_of_week": 2,  # Wednesday
        "start_time": time(20, 0),
        "service_type": "wednesday_worship",
        "target_group": "all",
        "is_online": False,
        "order_index": 8,
    },
    # 새벽기도회 (월요일)
    {
        "name": "새벽기도회 (월)",
        "location": "온라인",
        "day_of_week": 0,  # Monday
        "start_time": time(5, 30),
        "service_type": "dawn_prayer",
        "target_group": "all",
        "is_online": True,
        "order_index": 9,
    },
    # 새벽기도회 (화요일)
    {
        "name": "새벽기도회 (화)",
        "location": "온라인",
        "day_of_week": 1,  # Tuesday
        "start_time": time(5, 30),
        "service_type": "dawn_prayer",
        "target_group": "all",
        "is_online": True,
        "order_index": 10,
    },
    # 새벽기도회 (수요일)
    {
        "name": "새벽기도회 (수)",
        "location": "온라인",
        "day_of_week": 2,  # Wednesday
        "start_time": time(5, 30),
        "service_type": "dawn_prayer",
        "target_group": "all",
        "is_online": True,
        "order_index": 11,
    },
    # 새벽기도회 (목요일)
    {
        "name": "새벽기도회 (목)",
        "location": "온라인",
        "day_of_week": 3,  # Thursday
        "start_time": time(5, 30),
        "service_type": "dawn_prayer",
        "target_group": "all",
        "is_online": True,
        "order_index": 12,
    },
    # 새벽기도회 (금요일)
    {
        "name": "새벽기도회 (금)",
        "location": "온라인",
        "day_of_week": 4,  # Friday
        "start_time": time(5, 30),
        "service_type": "dawn_prayer",
        "target_group": "all",
        "is_online": True,
        "order_index": 13,
    },
]

print("\nInserting worship services...")
for service in services:
    cur.execute(
        """
        INSERT INTO worship_services (
            church_id, name, location, day_of_week, start_time, 
            service_type, target_group, is_online, is_active, order_index
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (
            church_id,
            service["name"],
            service["location"],
            service["day_of_week"],
            service["start_time"],
            service["service_type"],
            service["target_group"],
            service["is_online"],
            True,  # is_active
            service["order_index"],
        ),
    )
    print(f"  - Added: {service['name']}")

# Commit the transaction
conn.commit()
print("\nAll worship services have been added successfully!")

# Close the connection
cur.close()
conn.close()

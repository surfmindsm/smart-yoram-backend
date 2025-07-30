"""
Script to create database tables directly without circular dependencies
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Connect to database
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

# Create tables in the correct order
try:
    # Create churches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS churches (
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            address VARCHAR,
            phone VARCHAR,
            email VARCHAR,
            pastor_name VARCHAR,
            subscription_status VARCHAR DEFAULT 'active',
            subscription_end_date TIMESTAMP,
            member_limit INTEGER DEFAULT 100,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    print("✓ Created churches table")

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR UNIQUE NOT NULL,
            username VARCHAR UNIQUE NOT NULL,
            hashed_password VARCHAR NOT NULL,
            full_name VARCHAR,
            phone VARCHAR,
            church_id INTEGER REFERENCES churches(id),
            role VARCHAR DEFAULT 'user',
            is_active BOOLEAN DEFAULT true,
            is_superuser BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    print("✓ Created users table")

    # Create members table (without family_id for now)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id SERIAL PRIMARY KEY,
            church_id INTEGER NOT NULL REFERENCES churches(id),
            user_id INTEGER REFERENCES users(id),
            name VARCHAR NOT NULL,
            phone VARCHAR,
            email VARCHAR,
            address VARCHAR,
            photo_url VARCHAR,
            birthdate DATE,
            gender VARCHAR,
            marital_status VARCHAR,
            position VARCHAR DEFAULT 'member',
            department VARCHAR,
            district VARCHAR,
            baptism_date DATE,
            baptism_church VARCHAR,
            registration_date DATE DEFAULT CURRENT_DATE,
            status VARCHAR DEFAULT 'active',
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    print("✓ Created members table")

    # Create attendances table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendances (
            id SERIAL PRIMARY KEY,
            church_id INTEGER NOT NULL REFERENCES churches(id),
            member_id INTEGER NOT NULL REFERENCES members(id),
            service_date DATE NOT NULL,
            service_type VARCHAR NOT NULL DEFAULT 'sunday',
            present BOOLEAN DEFAULT true,
            check_in_time TIMESTAMP WITH TIME ZONE,
            check_in_method VARCHAR,
            notes VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by INTEGER REFERENCES users(id),
            UNIQUE(member_id, service_date, service_type)
        )
    """)
    print("✓ Created attendances table")

    # Create bulletins table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bulletins (
            id SERIAL PRIMARY KEY,
            church_id INTEGER NOT NULL REFERENCES churches(id),
            title VARCHAR NOT NULL,
            date DATE NOT NULL,
            content TEXT,
            file_url VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by INTEGER REFERENCES users(id),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    print("✓ Created bulletins table")

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_church_id ON members(church_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendances_date ON attendances(service_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendances_member_id ON attendances(member_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bulletins_church_id ON bulletins(church_id)")
    print("✓ Created indexes")

    # Insert default data
    cursor.execute("""
        INSERT INTO churches (name, address, phone, email, pastor_name)
        VALUES ('Smart Yoram Church', '123 Main St, Seoul', '02-1234-5678', 'info@smartyoram.church', 'Pastor Kim')
        ON CONFLICT DO NOTHING
        RETURNING id
    """)
    
    result = cursor.fetchone()
    if result:
        church_id = result[0]
        print(f"✓ Created default church (ID: {church_id})")
    else:
        cursor.execute("SELECT id FROM churches WHERE name = 'Smart Yoram Church'")
        church_id = cursor.fetchone()[0]
        print(f"✓ Church already exists (ID: {church_id})")

    # Create admin user (password: admin123)
    cursor.execute("""
        INSERT INTO users (username, email, hashed_password, church_id, role, is_superuser)
        VALUES (
            'admin',
            'admin@smartyoram.church',
            '$2b$12$LQv9vC9Ji2YM0F7WQZGOQe4OZHiXnXso8Q8SpbLPHat8HkKSKLD2W',
            %s,
            'admin',
            true
        )
        ON CONFLICT (username) DO NOTHING
    """, (church_id,))
    print("✓ Created admin user (username: admin, password: admin123)")

    # Create sample members
    cursor.execute("""
        INSERT INTO members (church_id, name, phone, email, gender, position)
        VALUES 
            (%s, '김철수', '010-1234-5678', 'chulsoo@example.com', 'M', 'member'),
            (%s, '이영희', '010-2345-6789', 'younghee@example.com', 'F', 'member'),
            (%s, '박민수', '010-3456-7890', 'minsoo@example.com', 'M', 'member'),
            (%s, '정수진', '010-4567-8901', 'soojin@example.com', 'F', 'member')
        ON CONFLICT DO NOTHING
    """, (church_id, church_id, church_id, church_id))
    print("✓ Created sample members")

    # Commit the transaction
    conn.commit()
    print("\n✅ Database setup complete!")

except Exception as e:
    conn.rollback()
    print(f"\n❌ Error: {e}")
    raise

finally:
    cursor.close()
    conn.close()
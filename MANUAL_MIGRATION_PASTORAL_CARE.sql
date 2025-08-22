-- Manual Migration: Add Location Fields to pastoral_care_requests
-- Execute this SQL on your database to add the new location-related columns
-- Date: 2025-08-22
-- Description: Add address, latitude, longitude, contact_info, and is_urgent fields

-- Step 1: Add new columns to pastoral_care_requests table
ALTER TABLE public.pastoral_care_requests 
ADD COLUMN IF NOT EXISTS address VARCHAR(500),
ADD COLUMN IF NOT EXISTS latitude NUMERIC(10,8),
ADD COLUMN IF NOT EXISTS longitude NUMERIC(11,8),
ADD COLUMN IF NOT EXISTS contact_info VARCHAR(500),
ADD COLUMN IF NOT EXISTS is_urgent BOOLEAN DEFAULT FALSE;

-- Step 2: Create indexes for location-based queries
CREATE INDEX IF NOT EXISTS idx_pastoral_care_location 
ON public.pastoral_care_requests (latitude, longitude);

-- Step 3: Create index for urgent requests filtering
CREATE INDEX IF NOT EXISTS idx_pastoral_care_is_urgent 
ON public.pastoral_care_requests (is_urgent);

-- Step 4: Verify the changes (optional - run to check)
-- SELECT column_name, data_type, is_nullable, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'pastoral_care_requests' 
-- AND table_schema = 'public'
-- ORDER BY ordinal_position;

-- Step 5: Verify indexes (optional - run to check)
-- SELECT indexname, indexdef 
-- FROM pg_indexes 
-- WHERE tablename = 'pastoral_care_requests' 
-- AND schemaname = 'public';

-- ============================================
-- ROLLBACK SCRIPT (if needed to undo changes)
-- ============================================
/*
-- Drop indexes first
DROP INDEX IF EXISTS public.idx_pastoral_care_is_urgent;
DROP INDEX IF EXISTS public.idx_pastoral_care_location;

-- Drop columns
ALTER TABLE public.pastoral_care_requests 
DROP COLUMN IF EXISTS is_urgent,
DROP COLUMN IF EXISTS contact_info,
DROP COLUMN IF EXISTS longitude,
DROP COLUMN IF EXISTS latitude,
DROP COLUMN IF EXISTS address;
*/
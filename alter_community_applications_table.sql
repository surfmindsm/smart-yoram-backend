-- Add new columns to existing community_applications table
-- Run this if the table already exists

-- Add password hash column
ALTER TABLE community_applications 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Add agreement columns
ALTER TABLE community_applications 
ADD COLUMN IF NOT EXISTS agree_terms BOOLEAN DEFAULT FALSE;

ALTER TABLE community_applications 
ADD COLUMN IF NOT EXISTS agree_privacy BOOLEAN DEFAULT FALSE;

ALTER TABLE community_applications 
ADD COLUMN IF NOT EXISTS agree_marketing BOOLEAN DEFAULT FALSE;

-- Update existing records with default values
UPDATE community_applications 
SET 
    password_hash = 'NEEDS_RESET',  -- Placeholder for existing records
    agree_terms = FALSE,
    agree_privacy = FALSE,
    agree_marketing = FALSE
WHERE password_hash IS NULL;

-- Add NOT NULL constraints after setting default values
ALTER TABLE community_applications 
ALTER COLUMN password_hash SET NOT NULL;

ALTER TABLE community_applications 
ALTER COLUMN agree_terms SET NOT NULL;

ALTER TABLE community_applications 
ALTER COLUMN agree_privacy SET NOT NULL;

ALTER TABLE community_applications 
ALTER COLUMN agree_marketing SET NOT NULL;

COMMENT ON COLUMN community_applications.password_hash IS 'Bcrypt hashed password for user login';
COMMENT ON COLUMN community_applications.agree_terms IS 'User agreed to terms of service';
COMMENT ON COLUMN community_applications.agree_privacy IS 'User agreed to privacy policy';
COMMENT ON COLUMN community_applications.agree_marketing IS 'User agreed to marketing communications';
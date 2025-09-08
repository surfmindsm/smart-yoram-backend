-- Create community_applications table for production PostgreSQL
CREATE TABLE IF NOT EXISTS community_applications (
    id SERIAL PRIMARY KEY,
    applicant_type VARCHAR(20) NOT NULL,
    organization_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    business_number VARCHAR(50),
    address TEXT,
    description TEXT NOT NULL,
    service_area VARCHAR(200),
    website VARCHAR(500),
    attachments TEXT,  -- JSON string for file info
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by INTEGER,
    rejection_reason TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_community_applications_email ON community_applications(email);
CREATE INDEX IF NOT EXISTS idx_community_applications_status ON community_applications(status);
CREATE INDEX IF NOT EXISTS idx_community_applications_submitted_at ON community_applications(submitted_at);
CREATE INDEX IF NOT EXISTS idx_community_applications_applicant_type ON community_applications(applicant_type);

-- Add comment for documentation
COMMENT ON TABLE community_applications IS 'Community member application submissions';
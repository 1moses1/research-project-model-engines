-- Rwanda NCSA Compliance Auditor - Database Schema
-- PostgreSQL initialization script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- ORGANIZATIONS TABLE
-- ============================================================================
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    industry VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Rwanda',
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'auditor', -- admin, auditor, viewer
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AUDIT TARGETS TABLE (Machines/Systems to audit)
-- ============================================================================
CREATE TABLE audit_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    hostname VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    os_type VARCHAR(50) NOT NULL, -- macos, linux, windows
    os_version VARCHAR(100),
    description TEXT,
    ssh_user VARCHAR(100),
    ssh_port INTEGER DEFAULT 22,
    auth_method VARCHAR(50) DEFAULT 'ssh_key', -- ssh_key, password, local
    is_active BOOLEAN DEFAULT TRUE,
    last_audit_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- POLICY DOCUMENTS TABLE
-- ============================================================================
CREATE TABLE policy_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    framework VARCHAR(100) DEFAULT 'Rwanda-NCSA', -- Rwanda-NCSA, NIST-800-53, ISO-27001
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    extracted_controls JSONB,
    extracted_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- AUDITS TABLE
-- ============================================================================
CREATE TABLE audits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id VARCHAR(100) UNIQUE NOT NULL, -- Human-readable: AUDIT-20251122-123456
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    target_id UUID REFERENCES audit_targets(id),
    initiated_by UUID REFERENCES users(id),
    framework VARCHAR(100) DEFAULT 'Rwanda-NCSA',
    status VARCHAR(50) DEFAULT 'initialized', -- initialized, running, completed, failed
    stage VARCHAR(50) DEFAULT 'initialized',
    progress INTEGER DEFAULT 0,
    message TEXT,

    -- Target info snapshot
    target_hostname VARCHAR(255),
    target_os_type VARCHAR(50),
    target_user VARCHAR(100),
    auth_method VARCHAR(50),

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,

    -- Results summary
    overall_score DECIMAL(5,2),
    total_controls INTEGER DEFAULT 0,
    compliant_controls INTEGER DEFAULT 0,
    partial_controls INTEGER DEFAULT 0,
    non_compliant_controls INTEGER DEFAULT 0,
    logs_collected INTEGER DEFAULT 0,

    -- Full results
    results JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AUDIT LOGS TABLE (Real-time audit progress)
-- ============================================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID REFERENCES audits(id) ON DELETE CASCADE,
    stage VARCHAR(50) NOT NULL,
    level VARCHAR(20) DEFAULT 'info', -- info, warning, error, success
    message TEXT NOT NULL,
    command VARCHAR(500), -- The actual command executed
    output TEXT, -- Command output (truncated)
    control_id VARCHAR(50), -- Associated control if applicable
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COMPLIANCE DECISIONS TABLE (Per-control decisions)
-- ============================================================================
CREATE TABLE compliance_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID REFERENCES audits(id) ON DELETE CASCADE,
    control_id VARCHAR(50) NOT NULL,
    control_name VARCHAR(255),
    control_family VARCHAR(100),
    framework VARCHAR(100),
    status VARCHAR(50) NOT NULL, -- COMPLIANT, PARTIALLY_COMPLIANT, NON_COMPLIANT
    confidence DECIMAL(5,4),
    evidence TEXT,
    indicators JSONB,
    recommendation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- REPORTS TABLE
-- ============================================================================
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID REFERENCES audits(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id),
    report_type VARCHAR(50) DEFAULT 'compliance', -- compliance, executive, detailed
    format VARCHAR(20) DEFAULT 'pdf', -- pdf, html, json
    filename VARCHAR(255),
    file_path TEXT,
    file_size BIGINT,
    generated_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- OS AUDIT TAXONOMIES TABLE (Commands per OS)
-- ============================================================================
CREATE TABLE os_audit_taxonomies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    os_type VARCHAR(50) NOT NULL, -- macos, linux, windows
    os_version VARCHAR(100), -- Optional: specific version
    command_name VARCHAR(100) NOT NULL,
    command_args TEXT[] NOT NULL, -- Array of command arguments
    control_id VARCHAR(50) NOT NULL,
    control_name VARCHAR(255),
    control_family VARCHAR(100),
    description TEXT,
    expected_indicators JSONB, -- What to look for in output
    compliance_criteria JSONB, -- How to determine compliance
    timeout_seconds INTEGER DEFAULT 30,
    requires_sudo BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(os_type, command_name)
);

-- ============================================================================
-- SESSIONS TABLE (For Redis backup/persistence)
-- ============================================================================
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_audits_organization ON audits(organization_id);
CREATE INDEX idx_audits_status ON audits(status);
CREATE INDEX idx_audits_created ON audits(created_at DESC);
CREATE INDEX idx_audit_logs_audit ON audit_logs(audit_id);
CREATE INDEX idx_compliance_decisions_audit ON compliance_decisions(audit_id);
CREATE INDEX idx_policy_documents_org ON policy_documents(organization_id);
CREATE INDEX idx_os_taxonomies_os ON os_audit_taxonomies(os_type);
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_sessions_token ON sessions(session_token);

-- ============================================================================
-- UPDATE TIMESTAMP TRIGGER
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audit_targets_updated_at BEFORE UPDATE ON audit_targets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audits_updated_at BEFORE UPDATE ON audits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA: Default Organization
-- ============================================================================
INSERT INTO organizations (name, description, industry, country)
VALUES ('Demo Organization', 'Default organization for testing', 'Technology', 'Rwanda');

-- ============================================================================
-- INITIAL DATA: Admin User (password: admin123)
-- ============================================================================
INSERT INTO users (organization_id, email, password_hash, full_name, role)
SELECT id, 'admin@rwanda-ncsa.rw', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.0RLT6UwJKdTHNe', 'System Administrator', 'admin'
FROM organizations WHERE name = 'Demo Organization';

COMMIT;

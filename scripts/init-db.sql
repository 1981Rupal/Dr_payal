-- Initialize Hospital CRM Database
-- This script sets up the initial database configuration

-- Create database if it doesn't exist (for PostgreSQL)
-- Note: This is typically handled by Docker Compose

-- Set timezone
SET timezone = 'UTC';

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance (will be created by SQLAlchemy migrations)
-- These are just examples of what might be created

-- Performance optimization settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';

-- Restart required for some settings to take effect
-- This will be handled by the Docker container restart

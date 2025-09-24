-- Multi-Tenant PostgreSQL Schema Setup
-- Creates separate schemas for 3 companies with their own tables

-- Create company schemas
CREATE SCHEMA IF NOT EXISTS company_a;
CREATE SCHEMA IF NOT EXISTS company_b;
CREATE SCHEMA IF NOT EXISTS company_c;

-- Create shared enums (can be used across all companies)
DO $$ BEGIN
    CREATE TYPE engagement_status_enum AS ENUM (
        'new', 'in_progress', 'resolved', 'closed', 'escalated'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE direction AS ENUM (
        'inbound', 'outbound'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE closing_reason AS ENUM (
        'resolved', 'duplicate', 'no_response', 'spam', 'escalated'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Function to create company-specific tables
CREATE OR REPLACE FUNCTION create_company_schema(company_name TEXT)
RETURNS VOID AS $$
BEGIN
    -- Create eng_interactions table for the company
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I.eng_interactions (
            id BIGSERIAL NOT NULL,
            channel VARCHAR(50) NOT NULL,
            channel_interaction_id TEXT NOT NULL,
            user_identifier TEXT NOT NULL,
            status engagement_status_enum NOT NULL DEFAULT ''new'',
            created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
            original_created_at TIMESTAMP(3) NOT NULL,
            engagement_id UUID NOT NULL DEFAULT gen_random_uuid(),
            entity_id TEXT NOT NULL,
            reference_id TEXT NOT NULL,
            is_replied BOOLEAN NOT NULL DEFAULT FALSE,
            is_delayed BOOLEAN NOT NULL DEFAULT FALSE,
            is_spam BOOLEAN NOT NULL DEFAULT FALSE,
            is_reopened BOOLEAN NOT NULL DEFAULT FALSE,
            channel_closing_reason closing_reason DEFAULT NULL,
            last_reply_id TEXT NOT NULL,
            last_reply_created_at TIMESTAMP(3) NOT NULL,
            last_reply_direction direction NOT NULL,
            frontend_json JSONB NOT NULL,
            text TEXT NOT NULL,
            sort_key BIGINT NOT NULL,
            company_id TEXT NOT NULL DEFAULT %L,
            UNIQUE (id, channel)
        ) PARTITION BY LIST (channel)', company_name, company_name);
    
    -- Create partitions for each channel
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I.eng_interactions_whatsapp PARTITION OF %I.eng_interactions FOR VALUES IN (''whatsapp'')', company_name, company_name);
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I.eng_interactions_twitter PARTITION OF %I.eng_interactions FOR VALUES IN (''twitter'')', company_name, company_name);
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I.eng_interactions_facebook PARTITION OF %I.eng_interactions FOR VALUES IN (''facebook'')', company_name, company_name);
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I.eng_interactions_email PARTITION OF %I.eng_interactions FOR VALUES IN (''email'')', company_name, company_name);
    
    -- Create notification functions for the company
    EXECUTE format('
        CREATE OR REPLACE FUNCTION %I.notify_interaction_change()
        RETURNS TRIGGER AS $func$
        BEGIN
            PERFORM pg_notify(''interaction_changes'', json_build_object(
                ''company'', %L,
                ''action'', TG_OP,
                ''id'', COALESCE(NEW.id, OLD.id),
                ''channel'', COALESCE(NEW.channel, OLD.channel),
                ''status'', COALESCE(NEW.status, OLD.status),
                ''timestamp'', NOW()
            )::text);
            RETURN COALESCE(NEW, OLD);
        END;
        $func$ LANGUAGE plpgsql', company_name, company_name);
    
    EXECUTE format('
        CREATE OR REPLACE FUNCTION %I.notify_status_change()
        RETURNS TRIGGER AS $func$
        BEGIN
            IF OLD.status IS DISTINCT FROM NEW.status THEN
                PERFORM pg_notify(''status_changes'', json_build_object(
                    ''company'', %L,
                    ''id'', NEW.id,
                    ''old_status'', OLD.status,
                    ''new_status'', NEW.status,
                    ''channel'', NEW.channel,
                    ''timestamp'', NOW()
                )::text);
            END IF;
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql', company_name, company_name);
    
    -- Create triggers
    EXECUTE format('
        DROP TRIGGER IF EXISTS interaction_insert_trigger ON %I.eng_interactions;
        CREATE TRIGGER interaction_insert_trigger
            AFTER INSERT ON %I.eng_interactions
            FOR EACH ROW EXECUTE FUNCTION %I.notify_interaction_change()', company_name, company_name, company_name);
    
    EXECUTE format('
        DROP TRIGGER IF EXISTS interaction_update_trigger ON %I.eng_interactions;
        CREATE TRIGGER interaction_update_trigger
            AFTER UPDATE ON %I.eng_interactions
            FOR EACH ROW EXECUTE FUNCTION %I.notify_status_change()', company_name, company_name, company_name);
    
    -- Create company-specific additional tables
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I.company_settings (
            id SERIAL PRIMARY KEY,
            setting_key VARCHAR(100) NOT NULL,
            setting_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(setting_key)
        )', company_name);
    
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I.users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT ''agent'',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )', company_name);
    
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I.analytics (
            id SERIAL PRIMARY KEY,
            metric_name VARCHAR(100) NOT NULL,
            metric_value NUMERIC NOT NULL,
            metric_date DATE NOT NULL,
            channel VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )', company_name);
END;
$$ LANGUAGE plpgsql;

-- Create schemas for all companies
SELECT create_company_schema('company_a');
SELECT create_company_schema('company_b');
SELECT create_company_schema('company_c');

-- Create a shared companies table for metadata
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    company_code VARCHAR(50) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(50) NOT NULL UNIQUE,
    frontend_port INTEGER NOT NULL UNIQUE,
    backend_port INTEGER NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert company configurations
INSERT INTO companies (company_code, company_name, schema_name, frontend_port, backend_port) VALUES
('COMP_A', 'Company Alpha', 'company_a', 3001, 5001),
('COMP_B', 'Company Beta', 'company_b', 3002, 5002),
('COMP_C', 'Company Gamma', 'company_c', 3003, 5003)
ON CONFLICT (company_code) DO NOTHING;

-- Create a function to get company configuration
CREATE OR REPLACE FUNCTION get_company_config(company_code_param VARCHAR(50))
RETURNS TABLE(
    company_code VARCHAR(50),
    company_name VARCHAR(255),
    schema_name VARCHAR(50),
    frontend_port INTEGER,
    backend_port INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.company_code, c.company_name, c.schema_name, c.frontend_port, c.backend_port
    FROM companies c
    WHERE c.company_code = company_code_param AND c.is_active = TRUE;
END;
$$ LANGUAGE plpgsql;

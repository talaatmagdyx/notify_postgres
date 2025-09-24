-- PostgreSQL notification system with eng_interactions table
-- This schema creates the table structure and notification triggers

-- Create custom enums
CREATE TYPE engagement_status_enum AS ENUM (
    'new',
    'in_progress', 
    'waiting_for_response',
    'resolved',
    'closed'
);

CREATE TYPE channel_closing_reason AS ENUM (
    'resolved',
    'timeout',
    'user_closed',
    'agent_closed',
    'spam',
    'duplicate'
);

CREATE TYPE direction AS ENUM (
    'inbound',
    'outbound'
);

-- Create the main table with partitioning
CREATE TABLE IF NOT EXISTS eng_interactions (
    id BIGSERIAL NOT NULL,
    channel VARCHAR(50) NOT NULL, -- e.g. "whatsapp","twitter","facebook","email"
    channel_interaction_id TEXT NOT NULL, -- The channel's native ID (DM ID, tweet ID, comment ID, etc.)
    user_identifier TEXT NOT NULL, -- The user's identifier (phone number, email, etc.)
    status engagement_status_enum NOT NULL DEFAULT 'new',
    created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, -- creation timestamp in your system
    updated_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, -- last update time
    original_created_at TIMESTAMP(3) NOT NULL, -- channel's own creation time
    engagement_id UUID NOT NULL DEFAULT gen_random_uuid(), -- this might be duplicated but it is so rare that it is not a problem
    entity_id TEXT NOT NULL, -- this will be used as parent_id(twitter)/client_id(dm) otherwise the default will be the channel_interaction_id
    reference_id TEXT NOT NULL, -- this means root_id(twitter)/agent_id(dm) otherwise the default will be the channel_interaction_id
    is_replied BOOLEAN NOT NULL DEFAULT FALSE, -- indicates if this interaction was replied to
    is_delayed BOOLEAN NOT NULL DEFAULT FALSE, -- indicates if this interaction was delayed for DM AI Agent
    is_spam BOOLEAN NOT NULL DEFAULT FALSE, -- indicates if this interaction is spam
    is_reopened BOOLEAN NOT NULL DEFAULT FALSE, -- indicates if this interaction was reopened
    closing_reason channel_closing_reason DEFAULT NULL, -- indicates the reason for closing the interaction
    last_reply_id TEXT NOT NULL, -- the last reply id of the interaction
    last_reply_created_at TIMESTAMP(3) NOT NULL, -- the last reply created at of the interaction
    last_reply_direction direction NOT NULL, -- the last reply direction of the interaction
    frontend_json JSONB NOT NULL, -- JSONB field for storing frontend data
    text TEXT NOT NULL, -- the text of the interaction
    sort_key BIGINT NOT NULL -- this is the sort key for the interaction
) PARTITION BY LIST (channel);

-- Create partitions for different channels
CREATE TABLE IF NOT EXISTS eng_interactions_whatsapp PARTITION OF eng_interactions
    FOR VALUES IN ('whatsapp');

CREATE TABLE IF NOT EXISTS eng_interactions_twitter PARTITION OF eng_interactions
    FOR VALUES IN ('twitter');

CREATE TABLE IF NOT EXISTS eng_interactions_facebook PARTITION OF eng_interactions
    FOR VALUES IN ('facebook');

CREATE TABLE IF NOT EXISTS eng_interactions_email PARTITION OF eng_interactions
    FOR VALUES IN ('email');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_eng_interactions_channel ON eng_interactions (channel);
CREATE INDEX IF NOT EXISTS idx_eng_interactions_user_identifier ON eng_interactions (user_identifier);
CREATE INDEX IF NOT EXISTS idx_eng_interactions_status ON eng_interactions (status);
CREATE INDEX IF NOT EXISTS idx_eng_interactions_created_at ON eng_interactions (created_at);
CREATE INDEX IF NOT EXISTS idx_eng_interactions_engagement_id ON eng_interactions (engagement_id);

-- Create a function to send notifications when interactions are inserted/updated
CREATE OR REPLACE FUNCTION notify_interaction_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Send notification with interaction details
    PERFORM pg_notify(
        'interaction_changes',
        json_build_object(
            'operation', TG_OP,
            'channel', NEW.channel,
            'interaction_id', NEW.id,
            'user_identifier', NEW.user_identifier,
            'status', NEW.status,
            'created_at', NEW.created_at,
            'engagement_id', NEW.engagement_id,
            'text', LEFT(NEW.text, 100) -- First 100 chars of text
        )::text
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for INSERT operations
CREATE TRIGGER trigger_interaction_insert
    AFTER INSERT ON eng_interactions
    FOR EACH ROW
    EXECUTE FUNCTION notify_interaction_change();

-- Create trigger for UPDATE operations
CREATE TRIGGER trigger_interaction_update
    AFTER UPDATE ON eng_interactions
    FOR EACH ROW
    EXECUTE FUNCTION notify_interaction_change();

-- Create a function to send notifications for status changes specifically
CREATE OR REPLACE FUNCTION notify_status_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Only notify if status actually changed
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        PERFORM pg_notify(
            'status_changes',
            json_build_object(
                'interaction_id', NEW.id,
                'channel', NEW.channel,
                'user_identifier', NEW.user_identifier,
                'old_status', OLD.status,
                'new_status', NEW.status,
                'updated_at', NEW.updated_at,
                'engagement_id', NEW.engagement_id
            )::text
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for status changes
CREATE TRIGGER trigger_status_change
    AFTER UPDATE ON eng_interactions
    FOR EACH ROW
    EXECUTE FUNCTION notify_status_change();

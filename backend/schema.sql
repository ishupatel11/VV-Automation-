-- =============================================================================
-- V.V. Automation — Contact Messages Database Schema
-- =============================================================================
-- Run this script once against your MySQL instance to create the table.
--
-- Usage:
--   mysql -u <user> -p <database_name> < schema.sql
--
-- Or paste into your MySQL client / Railway MySQL shell.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS vv_automation
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE vv_automation;

CREATE TABLE IF NOT EXISTS contact_messages (
    -- Primary Key
    id              INT             NOT NULL AUTO_INCREMENT,

    -- Visitor details (sanitized before storage)
    full_name       VARCHAR(150)    NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    subject         VARCHAR(300)    NOT NULL,
    message         TEXT            NOT NULL,

    -- Request metadata (captured server-side)
    ip_address      VARCHAR(45)     NOT NULL DEFAULT '',   -- Supports IPv4 & IPv6
    user_agent      VARCHAR(500)    NOT NULL DEFAULT '',

    -- Timestamps (always stored in UTC)
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Workflow status for the admin
    status          ENUM('new', 'read', 'replied')
                                    NOT NULL DEFAULT 'new',

    -- Constraints
    PRIMARY KEY (id),

    -- Indexes for common queries
    INDEX idx_email      (email),
    INDEX idx_created_at (created_at),
    INDEX idx_status     (status)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Stores every contact form submission from the V.V. Automation website';

-- =============================================================================
-- Verify
-- =============================================================================
DESCRIBE contact_messages;

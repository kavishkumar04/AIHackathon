--Create a Snowflake table to store daily schema snapshots.
CREATE SCHEMA IF NOT EXISTS metadata;
CREATE TABLE IF NOT EXISTS metadata.schema_snapshots (
    snapshot_date DATE,
    snapshot_schema STRING,  -- Store as JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--Create a snowflake table to store gpt explanations of the changes detected.
CREATE TABLE IF NOT EXISTS metadata.changes_logs (
    changes_date DATE,
    base_date DATE,
    new_date DATE,
    gpt_explanation STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

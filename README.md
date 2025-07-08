# AIHackathon

**Problem Statement:**

Changes in source tables often go unnoticed, breaking downstream pipelines, dashboards, or stored procedures. Detecting and fixing these issues manually is slow, reactive, and wastes engineering time.
We needed a way to catch these changes early, understand their impact, and fix them before they cause problems.
This matters because:
1. Business teams might see broken dashboards or missing columns without warning.
2. Engineers waste time tracing where a pipeline broke.

**Process before AI:**
If a column was added, removed, or changed in a source system, we usually found out only after something broke — maybe a stored procedure failed, a dynamic table didn’t update, or a report was missing fields. At that point, we’d have to:
1. Manually inspect the failing object (stored proc, view, dynamic table, etc.)
2. Go look at the source table in Snowflake or the upstream system to compare columns
3. Try to remember or guess what the previous schema looked like
4. Check Git history or ask someone on the team if any schema changes were made
5. Then finally, update the logic or code to fix the break

This whole process could take hours or even days, especially if the person who made the change didn’t communicate it or if the change happened outside our control.

**This was slow and costly as:**
1. No historical snapshots to easily compare schemas
2. Relied on memory or guesswork to figure out what changed
3. Fixes were reactive, only done after something failed
4. Wasted developer time on detective work instead of actual development
5. Business teams were impacted due to delayed or broken reports



**Process After AI:**
1. Instead of waiting for schema issues to break something, we’ve automated the whole process.
2. Every day, a script connects to Snowflake and takes a full snapshot of our source table schemas.
3. It then compares today's schema with yesterday’s to check if any columns were added, removed, or changed.
4. If it finds a change, it uses GPT (AI) to explain what the impact could be — like “this column was removed and might break these reports or procedures.”
5. It also suggests fixes, like how to update your SELECT queries or stored procedures.
6. Finally, it stores all this — the drift, the explanation, and the suggested actions — into a log table in Snowflake.

**How this Value our customer:**
1. Catches data issues before they reach reports.
2. Keeps dashboards and insights accurate and reliable.
3. Fixes schema problems faster with AI help.
4. Reduces delays, confusion, and loss of trust in data.
5. Ensures a smooth, uninterrupted experience for users

**AI Tools Used:** ChatGPT

**Time Saved:** 4 to 6 Hours


# Proposed Solution:

# Create a Snowflake table to store daily schema snapshots.
CREATE SCHEMA IF NOT EXISTS metadata;
CREATE TABLE IF NOT EXISTS metadata.schema_snapshots (
    snapshot_date DATE,
    snapshot_schema STRING,  -- Store as JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Create a snowflake table to store gpt explanations of the changes detected.
CREATE TABLE IF NOT EXISTS metadata.changes_logs (
    changes_date DATE,
    base_date DATE,
    new_date DATE,
    gpt_explanation STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


# Logic to fetch and insert the schema snapshot into that schema_snapshots table.
import snowflake.connector
import json
import datetime

def fetch_and_store_schema_snapshot():
    # Step 1: Connect to Snowflake
    conn = snowflake.connector.connect(
        user='YOUR_USER',
        password='YOUR_PASSWORD',
        account='YOUR_ACCOUNT',
        warehouse='YOUR_WAREHOUSE',
        database='RAW',  # This is your raw layer
        schema='INFORMATION_SCHEMA'
    )
    cursor = conn.cursor()

    # Step 2: Execute the schema extraction SQL directly
    schema_query = """
        SELECT 
            table_schema, 
            table_name, 
            column_name, 
            data_type, 
            ordinal_position
        FROM 
            columns
        WHERE 
            table_schema NOT IN ('INFORMATION_SCHEMA')  -- Optional filter
        ORDER BY 
            table_schema, table_name, ordinal_position;
    """
    cursor.execute(schema_query)
    rows = cursor.fetchall()

    # Step 3: Convert to JSON format
    snapshot = [{
        "schema": r[0],
        "table": r[1],
        "column": r[2],
        "type": r[3],
        "position": r[4]
    } for r in rows]

    snapshot_json = json.dumps(snapshot)
    snapshot_date = datetime.date.today().isoformat()

    # Step 4: Store the snapshot in metadata table
    cursor.execute("USE SCHEMA metadata")
    cursor.execute("""
        INSERT INTO schema_snapshots (snapshot_date, snapshot_schema)
        VALUES (%s, %s)
    """, (snapshot_date, snapshot_json))

    print(f"✅ Schema snapshot for {snapshot_date} saved to metadata.schema_snapshots")

    # Step 5: Cleanup
    cursor.close()
    conn.close()
fetch_and_store_snapshot()

# Logic to fetch the snapshots from the schema_snapshots table for the given date and compare them to detect the drift.
import snowflake.connector
import json
import datetime
from gpt_explainer import explain_drift_with_gpt

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

def detect_changes_from_snowflake(date1, date2):
    conn = snowflake.connector.connect(
        user='YOUR_USER',
        password='YOUR_PASSWORD',
        account='YOUR_ACCOUNT',
        warehouse='YOUR_WH',
        database='RAW',
        schema='METADATA'
    )
    cursor = conn.cursor()

    query = """
        SELECT snapshot_date, snapshot_schema
        FROM schema_snapshots
        WHERE snapshot_date IN (%s, %s)
        ORDER BY snapshot_date
    """
    cursor.execute(query, (date1, date2))
    snapshots = cursor.fetchall()

    if len(snapshots) != 2:
        raise Exception("Could not retrieve both snapshots. Check date inputs.")

    snapshot_1 = json.loads(snapshots[0][1])
    snapshot_2 = json.loads(snapshots[1][1])

    keys_1 = {(r['schema'], r['table'], r['column']) for r in snapshot_1}
    keys_2 = {(r['schema'], r['table'], r['column']) for r in snapshot_2}

    added = keys_2 - keys_1
    removed = keys_1 - keys_2

    if added or removed:
        print("✅ Changes Detected:")
        if added:
            print("🟢 Added Columns:")
            for item in added:
                print("  +", item)

        if removed:
            print("🔴 Removed Columns:")
            for item in removed:
                print("  -", item)
        explanation = explain_changes_with_gpt(added, removed)
        print("\n🧠 GPT-4 Summary & Fix Suggestions:")
        print(explanation)
        insert_sql = """
        INSERT INTO changes_logs (
            changes_date,
            base_date,
            new_date,
            gpt_explanation
        )
        VALUES (%s, %s, %s, %s, %s, %s) """

        cursor.execute(insert_sql, (
        	today.isoformat(),
        	yesterday.isoformat(),
        	today.isoformat(),
        	explanation
        ))

    else:
        print("✅ No changes detected.")

    cursor.close()
    conn.close()
detect_changes_from_snowflake(yesterday, today)



# gpt_explainer.py: GPT based module to explain and suggest fixes for the detected changes.
import openai
import os

Set your API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

def explain_changes_with_gpt(added, removed):
    prompt = f"""
You are a Snowflake expert.

Schema drift was detected between two daily snapshots. Below are the changes:

🟢 Added Columns:
{format_drift_list(added)}

🔴 Removed Columns:
{format_drift_list(removed)}

Please:
1. Summarize what these changes mean.
2. Explain the potential impact on downstream objects like dynamic tables or stored procedures.
3. Suggest SQL fixes (e.g., ALTER TABLE, updated SELECTs, stored proc edits).

Return a clear explanation and sample SQL as needed.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.3
    )

    return response['choices'][0]['message']['content']

def format_drift_list(drift_set):
    return "\n".join(f"- {schema}.{table}.{column}" for schema, table, column in drift_set)

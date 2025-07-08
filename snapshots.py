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

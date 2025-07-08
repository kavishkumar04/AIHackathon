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

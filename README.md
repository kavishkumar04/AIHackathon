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

1. Create a database named "metadata" and a Snowflake table name "schema_snapshots" to store daily schema snapshots([createstatements.sql](https://github.com/kavishkumar04/AIHackathon/blob/main/createstatements.sql)).
2. Create a snowflake table named "changes_logs" to store gpt explanations of the changes detected([createstatements.sql](https://github.com/kavishkumar04/AIHackathon/blob/main/createstatements.sql)).
3. Fetch and insert the schema snapshot into that schema_snapshots table daily([snapshots.py](https://github.com/kavishkumar04/AIHackathon/blob/main/snapshots.py)).
4. Fetch the snapshots from the schema_snapshots table for the given date and compare them to detect the changes and call the GPT based module to generate explanation for the changes and store them in changes_logs table([detect_changes.py](https://github.com/kavishkumar04/AIHackathon/blob/main/detect_changes.py)).
5. GPT based module to explain and suggest fixes for the detected changes([gpt_explainer.py](https://github.com/kavishkumar04/AIHackathon/blob/main/gpt_explainer.py)).

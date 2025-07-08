import openai
import os

# Set your API key securely
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

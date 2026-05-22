"""
sql_agent.py — Converts plain English to SQL using OpenAI and runs it.
"""
from __future__ import annotations
import pandas as pd
import sqlite3
import os
from openai import OpenAI


def load_data_to_sqlite(csv_path: str, table_name: str = "sales") -> sqlite3.Connection:
    """Load CSV into an in-memory SQLite database."""
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(":memory:")
    df.to_sql(table_name, conn, index=False, if_exists="replace")
    return conn, df


def get_schema(conn: sqlite3.Connection, table_name: str = "sales") -> str:
    """Get table schema as string."""
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    cols = cursor.fetchall()
    schema = f"Table: {table_name}\nColumns:\n"
    for col in cols:
        schema += f"  - {col[1]} ({col[2]})\n"
    return schema


def ask(question: str, conn: sqlite3.Connection, table_name: str = "sales") -> dict:
    """Convert a plain English question to SQL and run it."""
    
    # If no API key, use demo mode
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-openai-api-key-here":
        return _demo_mode(question, conn, table_name)

    schema = get_schema(conn, table_name)
    client = OpenAI(api_key=api_key)

    prompt = f"""You are a SQL expert. Convert the user's question to a SQLite SQL query.

{schema}

Rules:
- Return ONLY the SQL query, nothing else
- No markdown, no explanation
- Use only columns that exist in the schema
- Always use the table name: {table_name}

Question: {question}
SQL:"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0
        )
        sql = response.choices[0].message.content.strip()
        result_df = pd.read_sql_query(sql, conn)
        return {
            "question": question,
            "sql": sql,
            "result": result_df,
            "error": None,
            "mode": "ai"
        }
    except Exception as e:
        return {
            "question": question,
            "sql": "",
            "result": pd.DataFrame(),
            "error": str(e),
            "mode": "ai"
        }


def _demo_mode(question: str, conn: sqlite3.Connection, table_name: str) -> dict:
    """Demo mode — runs preset queries without OpenAI API key."""
    q = question.lower()

    if "total revenue" in q or "revenue" in q:
        sql = f"SELECT store, ROUND(SUM(revenue),2) as total_revenue FROM {table_name} GROUP BY store ORDER BY total_revenue DESC"
    elif "top" in q and "product" in q:
        sql = f"SELECT product, SUM(quantity) as total_sold FROM {table_name} GROUP BY product ORDER BY total_sold DESC LIMIT 5"
    elif "category" in q:
        sql = f"SELECT category, COUNT(*) as count, ROUND(SUM(revenue),2) as revenue FROM {table_name} GROUP BY category"
    elif "region" in q:
        sql = f"SELECT region, ROUND(SUM(revenue),2) as revenue FROM {table_name} GROUP BY region ORDER BY revenue DESC"
    elif "average" in q or "avg" in q:
        sql = f"SELECT product, ROUND(AVG(price),2) as avg_price FROM {table_name} GROUP BY product"
    else:
        sql = f"SELECT * FROM {table_name} LIMIT 10"

    try:
        result_df = pd.read_sql_query(sql, conn)
        return {
            "question": question,
            "sql": sql,
            "result": result_df,
            "error": None,
            "mode": "demo"
        }
    except Exception as e:
        return {
            "question": question,
            "sql": sql,
            "result": pd.DataFrame(),
            "error": str(e),
            "mode": "demo"
        }

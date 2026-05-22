"""
explain_agent.py — Explains data quality issues in plain English using OpenAI.
"""
from __future__ import annotations
import os
from openai import OpenAI


def explain_issues(results: list[dict]) -> str:
    """Take quality check results and explain them in plain English."""

    failed = [r for r in results if not r["passed"]]

    if not failed:
        return "✅ All data quality checks passed. Your data looks clean and ready for analysis."

    # If no API key, use rule-based explanation
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-openai-api-key-here":
        return _rule_based_explanation(failed)

    client = OpenAI(api_key=api_key)

    issues_text = "\n".join([
        f"- Rule: {r['rule']} | Column: {r['column']} | Issue: {r['detail']} | Severity: {r['severity']}"
        for r in failed
    ])

    prompt = f"""You are a data quality expert. Explain these data issues in simple, 
clear business language. Give a brief summary and suggest fixes.

Issues found:
{issues_text}

Write a clear explanation in 3-5 sentences max. Be specific about what's wrong and why it matters."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return _rule_based_explanation(failed)


def _rule_based_explanation(failed: list[dict]) -> str:
    """Generate explanation without OpenAI."""
    high = [r for r in failed if r["severity"] == "high"]
    medium = [r for r in failed if r["severity"] == "medium"]

    lines = []
    lines.append(f"⚠️ Found {len(failed)} data quality issue(s):\n")

    if high:
        lines.append(f"🔴 HIGH severity ({len(high)} issue(s)):")
        for r in high:
            lines.append(f"   • {r['message']} — {r['detail']}")

    if medium:
        lines.append(f"\n🟡 MEDIUM severity ({len(medium)} issue(s)):")
        for r in medium:
            lines.append(f"   • {r['message']} — {r['detail']}")

    lines.append("\n💡 Recommendation: Fix high severity issues before using this data for analysis.")
    return "\n".join(lines)

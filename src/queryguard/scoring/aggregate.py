"""
aggregate.py — Aggregates quality check results into an overall score.
"""
from __future__ import annotations


def calculate_score(results: list[dict]) -> dict:
    """
    Calculate overall data quality score from check results.
    Returns a score from 0-100 and a grade.
    """
    if not results:
        return {"score": 0, "grade": "F", "summary": "No checks ran"}

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    # Weight by severity
    severity_weights = {"high": 3, "medium": 2, "low": 1}
    total_weight = sum(severity_weights.get(r["severity"], 1) for r in results)
    passed_weight = sum(
        severity_weights.get(r["severity"], 1)
        for r in results if r["passed"]
    )

    score = round((passed_weight / total_weight) * 100, 1) if total_weight > 0 else 0

    # Grade
    if score >= 90:
        grade = "A"
        status = "Excellent"
    elif score >= 75:
        grade = "B"
        status = "Good"
    elif score >= 60:
        grade = "C"
        status = "Needs Attention"
    elif score >= 40:
        grade = "D"
        status = "Poor"
    else:
        grade = "F"
        status = "Critical"

    return {
        "score": score,
        "grade": grade,
        "status": status,
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "high_failures": sum(1 for r in results if not r["passed"] and r["severity"] == "high"),
        "medium_failures": sum(1 for r in results if not r["passed"] and r["severity"] == "medium"),
    }

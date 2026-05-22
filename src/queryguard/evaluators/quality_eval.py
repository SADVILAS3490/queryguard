"""
quality_eval.py — Runs YAML rules against a pandas DataFrame.
"""
from __future__ import annotations
import pandas as pd
import yaml
from pathlib import Path


def load_rules(yaml_path: str) -> dict:
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


def run_quality_checks(df: pd.DataFrame, rules_path: str) -> list[dict]:
    rules = load_rules(rules_path)
    results = []

    for rule in rules["rules"]:
        check = rule["check"]
        name = rule["name"]
        severity = rule["severity"]
        message = rule["message"]

        # No nulls check
        if check == "no_nulls":
            col = rule["column"]
            null_count = df[col].isnull().sum()
            passed = null_count == 0
            results.append({
                "rule": name,
                "check": check,
                "column": col,
                "passed": passed,
                "severity": severity,
                "message": message,
                "detail": f"{null_count} null values found" if not passed else "OK"
            })

        # Positive values check
        elif check == "positive_values":
            col = rule["column"]
            bad = df[col].dropna()
            bad_count = (bad <= 0).sum()
            passed = bad_count == 0
            results.append({
                "rule": name,
                "check": check,
                "column": col,
                "passed": passed,
                "severity": severity,
                "message": message,
                "detail": f"{bad_count} non-positive values found" if not passed else "OK"
            })

        # Allowed values check
        elif check == "allowed_values":
            col = rule["column"]
            allowed = set(rule["values"])
            bad_vals = df[~df[col].isin(allowed)][col].unique()
            passed = len(bad_vals) == 0
            results.append({
                "rule": name,
                "check": check,
                "column": col,
                "passed": passed,
                "severity": severity,
                "message": message,
                "detail": f"Invalid values: {list(bad_vals)}" if not passed else "OK"
            })

        # No duplicates check
        elif check == "no_duplicates":
            dup_count = df.duplicated().sum()
            passed = dup_count == 0
            results.append({
                "rule": name,
                "check": check,
                "column": "all",
                "passed": passed,
                "severity": severity,
                "message": message,
                "detail": f"{dup_count} duplicate rows found" if not passed else "OK"
            })

    return results

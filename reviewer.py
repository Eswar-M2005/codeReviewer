import argparse
import json
import os
import sys
import csv
import ast

from modules.module1 import read_python_file, detect_issues_ast
from modules.module2_ollama import build_results                 # Offline fallback
from modules.module2_ollama import build_results_with_ai # AI version
from modules.module3 import aggregate_module3_results
from modules.config_loader import load_config


SEVERITY_ORDER = {
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3
}


# -----------------------------------
# Utility Functions
# -----------------------------------

def should_exclude(file_path, exclude_paths):
    return any(ex in file_path for ex in exclude_paths)


def sort_results(results):
    return sorted(
        results,
        key=lambda r: (-SEVERITY_ORDER.get(r["severity"], 1), r["issue"])
    )


def export_csv(results, file_path):
    base = os.path.splitext(file_path)[0]
    output = f"{base}_report.csv"

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Issue", "Severity", "Feedback"])

        for r in results:
            writer.writerow([
                r.get("issue", ""),
                r.get("severity", ""),
                r.get("feedback", "")
            ])

    print(f"\n📁 Report saved to {output}")


# -----------------------------------
# SCAN (Metrics Only)
# -----------------------------------

def scan(file_path, config):
    if should_exclude(file_path, config["exclude_paths"]):
        print("File excluded by config.")
        return {}

    try:
        code = read_python_file(file_path)
        tree = ast.parse(code)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    issues = detect_issues_ast(code)

    num_functions = sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree))
    num_classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
    num_loops = sum(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree))
    num_conditionals = sum(isinstance(n, ast.If) for n in ast.walk(tree))

    return {
        "file": file_path,
        "functions": num_functions,
        "classes": num_classes,
        "loops": num_loops,
        "conditionals": num_conditionals,
        "total_issues": len(issues)
    }


# -----------------------------------
# REVIEW (AI + Fallback)
# -----------------------------------

def review(file_path, config):
    try:
        code = read_python_file(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    issues = detect_issues_ast(code)

    if not issues:
        print("\nNo issues detected.")
        return

    print("\n=== CODE REVIEW ===")

    # Try AI first
    try:
        results = build_results_with_ai(issues, code)
    except Exception:
        print("⚠️ AI failed. Falling back to offline mode.")
        results = build_results(issues)

    # Ensure unified key format
    for r in results:
        if "ai_feedback" in r:
            r["feedback"] = r.pop("ai_feedback")

    results = sort_results(results)

    for r in results:
        print("\nIssue:", r.get("issue"))
        print("Severity:", r.get("severity"))
        print("Feedback:")
        print(r.get("feedback"))


# -----------------------------------
# REPORT (AI + CSV)
# -----------------------------------

def report(file_path, config):
    if should_exclude(file_path, config["exclude_paths"]):
        print("File excluded by config.")
        return

    try:
        code = read_python_file(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    issues = detect_issues_ast(code)

    # Try AI first
    try:
        results = build_results_with_ai(issues, code)
    except Exception:
        print("⚠️ AI failed. Using offline results.")
        results = build_results(issues)

    # Normalize key
    for r in results:
        if "ai_feedback" in r:
            r["feedback"] = r.pop("ai_feedback")

    results = sort_results(results)

    if not results:
        print("No issues found.")
        return

    summary = aggregate_module3_results(results, file_path)

    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=4))

    export_csv(results, file_path)


# -----------------------------------
# APPLY & DIFF (Future)
# -----------------------------------

def apply(file_path, config):
    print("Auto-fix feature coming soon 🚀")


def diff(file_path, config):
    print("Diff comparison feature coming soon 🔥")


# -----------------------------------
# CLI Entry
# -----------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Professional Python Code Reviewer"
    )

    parser.add_argument(
        "command",
        choices=["scan", "review", "report", "apply", "diff"]
    )

    parser.add_argument("file", help="Python file to analyze")

    args = parser.parse_args()
    config = load_config()

    if args.command == "scan":
        metrics = scan(args.file, config)
        print("\n=== SCAN SUMMARY ===")
        print(json.dumps(metrics, indent=4))

    elif args.command == "review":
        review(args.file, config)

    elif args.command == "report":
        report(args.file, config)

    elif args.command == "apply":
        apply(args.file, config)

    elif args.command == "diff":
        diff(args.file, config)


if __name__ == "__main__":
    main()

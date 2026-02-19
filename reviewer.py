import argparse
import json
import os
import sys
import csv
import ast

from modules.module1 import read_python_file, detect_issues_ast
from modules.module2_ollama import build_results, build_results_with_ai
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
    return any(excluded in file_path for excluded in exclude_paths)


def normalize_results(results):
    for result in results:
        if "ai_feedback" in result:
            result["feedback"] = result.pop("ai_feedback")
    return results


def sort_results(results):
    return sorted(
        results,
        key=lambda result: (
            -SEVERITY_ORDER.get(result.get("severity", "INFO"), 1),
            result.get("issue", "")
        )
    )


def export_csv(results, file_path):
    output_file = f"{os.path.splitext(file_path)[0]}_report.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Issue", "Severity", "Feedback"])

        for result in results:
            writer.writerow([
                result.get("issue", ""),
                result.get("severity", ""),
                result.get("feedback", "")
            ])

    print(f"\nReport saved to {output_file}")


# -----------------------------------
# SCAN
# -----------------------------------

def scan_file(file_path, config):
    if should_exclude(file_path, config["exclude_paths"]):
        return 0

    try:
        code = read_python_file(file_path)
        tree = ast.parse(code)
    except (SyntaxError, FileNotFoundError) as error:
        print(f"Error processing {file_path}: {error}")
        return 1

    issues = detect_issues_ast(code)

    metrics = {
        "file": file_path,
        "functions": sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree)),
        "classes": sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree)),
        "loops": sum(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree)),
        "conditionals": sum(isinstance(node, ast.If) for node in ast.walk(tree)),
        "total_issues": len(issues)
    }

    print("\nSCAN SUMMARY")
    print(json.dumps(metrics, indent=4))

    return len(issues)


# -----------------------------------
# REVIEW
# -----------------------------------

def review_file(file_path):
    try:
        code = read_python_file(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    issues = detect_issues_ast(code)

    if not issues:
        print("No issues detected.")
        return

    try:
        results = build_results_with_ai(issues, code)
    except Exception:
        results = build_results(issues)

    results = normalize_results(results)
    results = sort_results(results)

    print(f"\nCODE REVIEW: {file_path}")

    for result in results:
        print("\nIssue:", result.get("issue"))
        print("Severity:", result.get("severity"))
        print("Feedback:", result.get("feedback"))


# -----------------------------------
# REPORT
# -----------------------------------

def report_file(file_path):
    try:
        code = read_python_file(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    issues = detect_issues_ast(code)

    try:
        results = build_results_with_ai(issues, code)
    except Exception:
        results = build_results(issues)

    results = normalize_results(results)
    results = sort_results(results)

    if not results:
        print("No issues found.")
        return

    summary = aggregate_module3_results(results, file_path)

    print("\nSUMMARY")
    print(json.dumps(summary, indent=4))

    export_csv(results, file_path)


# -----------------------------------
# MAIN
# -----------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Professional Python Code Reviewer"
    )

    parser.add_argument(
        "command",
        choices=["scan", "review", "report"]
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="Python files to analyze"
    )

    args = parser.parse_args()
    config = load_config()

    if args.command == "scan":
        has_issues = False

        for file_path in args.files:
            issue_count = scan_file(file_path, config)
            if issue_count > 0:
                has_issues = True

        if has_issues:
            print("\nQuality gate failed. Commit blocked.")
            sys.exit(1)

        print("\nNo issues detected.")
        sys.exit(0)

    if args.command == "review":
        for file_path in args.files:
            review_file(file_path)

    if args.command == "report":
        for file_path in args.files:
            report_file(file_path)


if __name__ == "__main__":
    main()

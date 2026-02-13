import json
from backend.ollama_client import OllamaClient


def classify_severity(issue):
    if issue in ["unused_variable", "bare_except"]:
        return "WARNING"
    elif issue in ["syntax_error"]:
        return "ERROR"
    return "INFO"

def build_results(issues):
    """
    Build structured results for detected issues
    """

    results = []

    for issue in issues:
        result = {
            "issue": issue,
            "severity": classify_severity(issue),
        }

        results.append(result)

    return results
def build_results_with_ai(issues, code):

    client = OllamaClient()
    results = []

    if not client.is_server_running():
        return [{
            "issue": issue,
            "severity": classify_severity(issue),
            "ai_feedback": "Ollama server not running."
        } for issue in issues]

    for issue in issues:

        prompt = f"""
You are a professional Python code reviewer.

Analyze the following issue in the code.

Issue: {issue}

Code:
{code}

Respond ONLY in this JSON format:

{{
  "issue": "{issue}",
  "severity": "INFO | WARNING | ERROR",
  "feedback": "clear explanation and fix suggestion"
}}

Do NOT include anything else.
"""

        response = client.generate(prompt)

        # Try parsing AI JSON safely
        try:
            ai_data = json.loads(response)

            results.append({
                "issue": ai_data.get("issue", issue),
                "severity": ai_data.get("severity", classify_severity(issue)),
                "feedback": ai_data.get("feedback", "No feedback provided.")
            })

        except Exception:
            # If AI doesn't return valid JSON
            results.append({
                "issue": issue,
                "severity": classify_severity(issue),
                "feedback": response
            })

    return results

def calculate_quality_score(results):
    score = 100
    for item in results:
        if item["severity"] == "INFO":
            score -= 2
        elif item["severity"] == "WARNING":
            score -= 5
        elif item["severity"] == "CRITICAL":
            score -= 10
    return max(score, 0)


def calculate_maintainability_index(results):
    return max(100 - len(results) * 5, 0)


def classify_maintainability(mi):
    if mi >= 85:
        return "Excellent"
    elif mi >= 65:
        return "Good"
    return "Bad"


def aggregate_module3_results(results, filename):
    quality_score = calculate_quality_score(results)
    mi = calculate_maintainability_index(results)
    mi_level = classify_maintainability(mi)

    return {
        "file": filename,
        "total_issues": len(results),
        "quality_score": quality_score,
        "maintainability_index": mi,
        "maintainability_level": mi_level
    }

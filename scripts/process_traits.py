import json

def map_severity(rating):
    if rating == 2:
        return "Low"
    elif rating == 1:
        return "Medium"
    return None

def build_issues_from_single_response(response_str):
    try:
        issues = []
        data = json.loads(response_str.strip("`json\n"))
        for trait in data:
            if not data[trait]:
                continue
            rating = data[trait].get("rating")
            justification = data[trait].get("justification")

            if rating is not None and rating < 3:
                issue = {
                    "Category Name": "Maintainability",
                    "Short Description": f"{trait.capitalize()} issue",
                    "Long Description": justification,
                    "Severity/Impact level": map_severity(rating)
                }
                issues.append(issue)
        return issues
    except json.JSONDecodeError:
        print(f"⚠️ Could not parse LLM response. Run evaluate.py to see response.")
        return None
import json

def map_severity(rating):
    if rating == 2:
        return "Low"
    elif rating == 1:
        return "Medium"
    return None

def parse_response(response_str, trait):
    try:
        data = json.loads(response_str.strip("`json\n"))
        if data.get("trait") != trait:
            data["trait"] = trait  # fallback correction if trait is missing
        return data
    except json.JSONDecodeError:
        print(f"⚠️ Could not parse LLM response for trait '{trait}'.")
        return None

def build_issues_from_responses(responses):
    issues = []
    for resp in responses:
        if not resp:
            continue
        rating = resp.get("rating")
        justification = resp.get("justification")
        trait = resp.get("trait")

        if rating is not None and rating < 3:
            issue = {
                "Category Name": "Maintainability",
                "Short Description": f"{trait.capitalize()} issue",
                "Long Description": justification,
                "Severity/Impact level": map_severity(rating)
            }
            issues.append(issue)
    return issues
import json
from pydantic import ValidationError

from models.datatypes import Issue, CodeEval
from utils.logger import logger

def map_severity(rating: int) -> str | None:
    if rating == 2:
        return "Low"
    elif rating == 1:
        return "Medium"
    return None

def build_issues_from_single_response(response_str: str) -> list[Issue] | None:
    try:
        issues = []
        data = json.loads(response_str.strip("`json\n"))
        code_eval = CodeEval(**data)  # Instantiate CodeEval from the JSON data
        
        # Loop through each metric in CodeEval
        for metric_name, eval_metric in code_eval.__dict__.items():
            rating = eval_metric.rating
            justification = eval_metric.justification

            if rating is not None and rating < 3:  # Only consider ratings less than 3
                issue = Issue(
                    category_name="Maintainability",
                    short_description=f"{metric_name.capitalize()} issue",
                    long_description=justification,
                    severity_impact_level=map_severity(rating)
                )
                issues.append(issue)
        return issues
    except ValidationError as e:
        logger.error("Validation failed:", e)
        return None
    except json.JSONDecodeError:
        logger.error(f"⚠️ Could not parse LLM response. Run evaluate.py to see response.")
        return None

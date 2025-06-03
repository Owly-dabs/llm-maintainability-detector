# Import functions from other files
from scripts import evaluate, process_traits as pt

import json

def main():
    traits = [
        "readability",
        "modularity",
        "simplicity",
        "documentation",
        "style_consistency"
    ]
    code_file = "depr_example_code4.py"
    language = "python"
    model = "gpt-4o"

    with open(f"examples/{code_file}") as f:
        code = f.read()

    raw_responses = []

    for trait in traits:
        print(f"Evaluating {trait}...")
        result_str = evaluate.evaluate_code(trait, language, code, model)
        print(f"\n--- {trait.capitalize()} Evaluation ---\n{result_str}\n")
        parsed = pt.parse_response(result_str, trait)
        raw_responses.append(parsed)

    issues = pt.build_issues_from_responses(raw_responses)

    with open(f"example_outputs/{code_file}.json", "w") as out:
        json.dump(issues, out, indent=2)
        print(f"\n✅ Saved {len(issues)} issue(s) to issues_output.json")


if __name__=="__main__":
    main()
    # Example usage
    # traits = [
    #     "readability",
    #     "modularity",
    #     "simplicity",
    #     "documentation",
    #     "style_consistency"
    # ]
    # code_file = "examples/example_code3.py"
    # language = "python"
    # model = "gpt-4o"  # Change to your desired model

    # # Read code from file
    # with open(code_file) as f:
    #     code = f.read()

    # # Evaluate the code
    # for trait in traits:
    #     print(f"Evaluating {trait}...")
    #     result = evaluate.evaluate_code(trait, language, code, model)

    #     # Print the result
    #     print(f"\n--- {trait.capitalize()} Evaluation ---\n{result}")


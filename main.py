# Import functions from other files
from scripts import evaluate, process_traits as pt

import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Evaluate code traits.")
    parser.add_argument("code_file", help="The code file to evaluate")
    args = parser.parse_args()

    CODE_FILE = args.code_file
    
    with open(f"{CODE_FILE}") as f:
        code = f.read()
    
    language = evaluate.detect_language_from_filename(CODE_FILE)
        
    traits_response = evaluate.evaluate_all_traits(
        language=language, 
        code=code,
        model="gpt-4o"
    )
    
    issues = pt.build_issues_from_single_response(traits_response)
    
    filename = CODE_FILE.split("/")[-1].split(".")[0]

    with open(f"example_outputs/{filename}.json", "w") as out:
        json.dump(issues, out, indent=2)
        print(f"\n✅ Saved {len(issues)} issue(s) to example_output/{filename}.json")


if __name__=="__main__":
    main()
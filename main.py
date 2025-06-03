# Import functions from other files
from scripts import evaluate, process_traits as pt

import json

def main():
    CODE_FILE = "example_code2.py"
    
    with open(f"examples/{CODE_FILE}") as f:
        code = f.read()
        
    traits_response = evaluate.evaluate_all_traits(
        language="python", # TODO: make this dynamic
        code=code,
        model="gpt-4o"
    )
    
    issues = pt.build_issues_from_single_response(traits_response)

    with open(f"example_outputs/{CODE_FILE}.json", "w") as out:
        json.dump(issues, out, indent=2)
        print(f"\n✅ Saved {len(issues)} issue(s) to issues_output.json")


if __name__=="__main__":
    main()
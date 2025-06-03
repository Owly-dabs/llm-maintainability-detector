from openai import OpenAI
import os
import sys 
# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
from scripts.llm_setup import set_openAI  # Import the function to set up OpenAI client

client = set_openAI(local=False)

def load_prompt_template(path="prompts/single_prompt.txt"):
    with open(path, "r") as f:
        return f.read()

def evaluate_all_traits(language, code, model="gpt-4o"): 
    prompt_template = load_prompt_template()
    prompt = prompt_template.format(language=language, code=code)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a code maintainability evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content 

# CLI support
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate code maintainability across all traits in one LLM call")
    parser.add_argument("code_file", help="Path to code file to evaluate")
    parser.add_argument("--language", default="python", help="Programming language of the code")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model to use")
    parser.add_argument("--output", default=None, help="Optional path to save output JSON")
    args = parser.parse_args()

    with open(args.code_file) as f:
        code = f.read()

    try:
        result_json = evaluate_all_traits(args.language, code, args.model)
        print("\n✅ Evaluation Result:")
        print(result_json)

        if args.output:
            with open(args.output, "w") as out_file:
                out_file.write(result_json)
            print(f"\n📝 Output saved to {args.output}")
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")

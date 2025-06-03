import json
from openai import OpenAI
import sys 
from scripts.llm_setup import set_openAI  # Import the function to set up OpenAI client

client = set_openAI(local=False)
import argparse

# Load prompts
def load_prompts(path="prompts/maintainability_prompts.json"):
    with open(path) as f:
        return json.load(f)

# Generate system and user messages
def generate_messages(trait, language, code, prompts):
    prompt_info = prompts.get(trait, {"description": "", "prompt_template": ""})
    system_msg = prompt_info["description"]
    user_msg = prompt_info["prompt_template"].format(
        trait=trait, language=language, code=code
    )
    return system_msg, user_msg

# Send to OpenAI
def evaluate_code(trait, language, code, model="gpt-4"):
    prompts = load_prompts()
    system_msg, user_msg = generate_messages(trait, language, code, prompts)

    response = client.chat.completions.create(model=model,
    messages=[
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ],
    temperature=0)
    return response.choices[0].message.content

# CLI support
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate code maintainability")
    parser.add_argument("trait", choices=["readability", "modularity", "simplicity", "documentation", "style_consistency"])
    parser.add_argument("code_file", help="Path to code file to evaluate")
    parser.add_argument("--language", default="python", help="Programming language of the code")
    parser.add_argument("--model", default="gpt-4", help="OpenAI model to use")
    args = parser.parse_args()

    with open(args.code_file) as f:
        code = f.read()

    result = evaluate_code(args.trait, args.language, code, args.model)
    print(f"\n--- {args.trait.capitalize()} Evaluation ---\n{result}")

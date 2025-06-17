from openai import OpenAI
from string import Template
import os
import sys 
from models.datatypes import Chunk
# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
from scripts.llm_setup import set_openAI  # Import the function to set up OpenAI client

client = set_openAI(local=False)

def detect_language_from_filename(filename):
    ext = os.path.splitext(filename)[1].lower()
    return {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".rb": "ruby",
        ".go": "go",
        ".rs": "rust",
        ".cbl": "cobol",
        ".cob": "cobol",
        ".vb": "vb.net",
        ".bas": "vb.net"
    }.get(ext, "unknown")

def load_prompt_template(path="prompts/single_prompt.txt"):
    with open(path, "r") as f:
        return f.read()

def evaluate_all_traits(language, code, prompt_template:str, model="gpt-4o"): 
    #prompt = prompt_template.format(language=language, code=code)
    prompt = Template(prompt_template).substitute(language=language, code=code)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a code maintainability evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content 

def summarize_evaluation_history(evaluation_history, prompt_template, model="gpt-4o"):
    """
    Summarize the evaluation history and return a single JSON object of 5 traits 
    and their respective ratings and justifications.
    """
    # prompt = prompt_template.format(evaluation_history=evaluation_history)
    prompt = Template(prompt_template).substitute(evaluation_history=evaluation_history)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a code maintainability evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()

def evaluate_chunks(language: str, code_chunks: list[Chunk], prompt_template: str, model: str = "gpt-4o") -> str:
    """
    Evaluate multiple code chunks for maintainability traits using LLM.

    Args:
        language (str): Programming language of the code.
        code_chunks (List[Chunk]): List of code chunks to evaluate.
        prompt_template (str): Prompt template for individual chunk evaluation.
        model (str): LLM model name (default: "gpt-4o").

    Returns:
        str: Summarized evaluation across all chunks.
    """
    evaluation_history = ""  # No evaluation history on the first chunk

    for chunk in code_chunks:
        code = chunk.content.strip()  # Access attribute directly from Chunk
        prompt = Template(prompt_template).substitute(
            language=language,
            code=code,
            evaluation_history=evaluation_history
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a code maintainability evaluator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            chunk_evaluation = response.choices[0].message.content.strip()
            evaluation_history += f"\n\nChunk {chunk.id}:\n{chunk_evaluation}"
        except Exception as e:
            print(f"❌ Error evaluating chunk {chunk.id}: {e}")
            continue

    return summarize_evaluation_history(
        evaluation_history,
        prompt_template=load_prompt_template("prompts/summarize_prompt.txt"),
        model=model
    )

# CLI support
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate code maintainability across all traits in one LLM call")
    parser.add_argument("code_file", help="Path to code file to evaluate")
    parser.add_argument("--language", default="python", help="Programming language of the code")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model to use")
    parser.add_argument("--output", default=None, help="Optional path to save output JSON")
    parser.add_argument("--chunk", action="store_true", help="Evaluate code in chunks instead of all at once")
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

from openai import OpenAI
from string import Template
import os
import sys 
from models.datatypes import Chunk
# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
from scripts.llm_setup import set_openAI  # Import the function to set up OpenAI client
from utils.logger import logger

client = set_openAI(local=False)

def load_prompt_template(path="prompts/single_prompt.txt"):
    with open(path, "r") as f:
        return f.read()

def run_chat_completion(prompt: str, model: str = "gpt-4o", context: str = "unknown", system_msg: str = "You are a code maintainability evaluator.") -> str | None:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"❌ [{context}] Chat completion error: {e}")
        return None


def evaluate_all_traits(language: str, code: str, prompt_template: str, model="gpt-4o") -> str | None: 
    """
    Evaluate a single string of code for maintainability traits using LLM.
    """
    prompt = Template(prompt_template).substitute(language=language, code=code)
    return run_chat_completion(prompt, model=model, context="evaluate_all_traits")


def summarize_evaluation_history(evaluation_history: str, prompt_template: str, model="gpt-4o") -> str | None:
    """
    Summarize the evaluation history using LLM.
    """
    prompt = Template(prompt_template).substitute(evaluation_history=evaluation_history)
    return run_chat_completion(prompt, model=model, context="summarize_evaluation_history")


def evaluate_chunks(language: str, code_chunks: list[Chunk], prompt_template: str, model: str = "gpt-4o") -> str | None:
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
    evaluation_history = ""

    for chunk in code_chunks:
        prompt = Template(prompt_template).substitute(
            language=language,
            code=chunk.content.strip(),
            evaluation_history=evaluation_history
        )
        result = run_chat_completion(prompt, model=model, context=f"evaluate_chunks - Chunk {chunk.id}")
        if result:
            evaluation_history += f"\n\nChunk {chunk.id}:\n{result}"
        else:
            logger.warning(f"⚠️ Skipping chunk {chunk.id} due to failed evaluation.")

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
        logger.info(f"\n✅ Evaluation Result:\n{result_json}\n")

        if args.output:
            with open(args.output, "w") as out_file:
                out_file.write(result_json)
            logger.info(f"\n📝 Output saved to {args.output}")
    except Exception as e:
        logger.error(f"\n❌ Error during evaluation: {e}")

# Import functions from other files
from scripts import evaluate, process_traits as pt, chunk
from utils.logger import logger
from models.datatypes import Issue

import json
import argparse

def get_code_from_file(code_file: str) -> str:
    """Read code from a file."""
    with open(code_file, 'r') as f:
        return f.read()
    
def get_issues_adaptive_chunking(code_file: str) -> list[Issue]:
    """Get issues from a code file by evaluating its traits with adaptive chunking."""
    code = get_code_from_file(code_file)

    should_chunk = chunk.should_chunk(code)
    if should_chunk:
        logger.info("Large file detected. Splitting code into chunks...")
        return get_issues_with_chunks(code_file)
    else:
        logger.info("Evaluating code as a single prompt...")
        return get_issues_single_prompt(code_file)

#TODO: logging instead of printing, it should be the first thing u do. Config logging first
#TODO: Figure out uv and use pyproject.toml for dependencies -- find out what a lock file is and hwo to use it

def get_issues_single_prompt(code_file: str) -> list[Issue]:
    """Get issues from a code file by evaluating its traits."""
    code = get_code_from_file(code_file)
    language = evaluate.detect_language_from_filename(code_file)
        
    traits_response = evaluate.evaluate_all_traits(
        language=language, 
        code=code,
        prompt_template=evaluate.load_prompt_template(),
        model="gpt-4o"
    )

    logger.debug(f"Traits response: {traits_response}")
    
    return pt.build_issues_from_single_response(traits_response)
    
def get_issues_with_chunks(code_file: str) -> list[Issue]:
    """Get issues from a list of code chunks by evaluating their traits."""
    code = get_code_from_file(code_file)
    language = evaluate.detect_language_from_filename(code_file)

    code_chunks = chunk.chunk_code_by_structure(code)

    traits_response = evaluate.evaluate_chunks(
        language=language, 
        code_chunks=code_chunks,
        prompt_template=evaluate.load_prompt_template("prompts/chunk_prompt.txt"),
        model="gpt-4o"
    )

    logger.debug(f"Traits response: {traits_response}")
   
    return pt.build_issues_from_single_response(traits_response)

def main():
    # logger.setLevel("DEBUG") # Comment for production use
    
    parser = argparse.ArgumentParser(description="Evaluate code traits.")
    parser.add_argument("code_file", help="The code file to evaluate")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--chunk", action="store_true", help="Force chunking (override adaptive detection)")
    group.add_argument("--no-chunk", action="store_true", help="Force no chunking (override adaptive detection)")

    args = parser.parse_args()
    CODE_FILE = args.code_file

    if args.chunk:
        logger.info("⚙️ Forced chunking mode enabled...")
        issues = get_issues_with_chunks(CODE_FILE)
    elif args.no_chunk:
        logger.info("⚙️ Forced single-prompt mode enabled...")
        issues = get_issues_single_prompt(CODE_FILE)
    else:
        issues = get_issues_adaptive_chunking(CODE_FILE)

    # Output issues to json file
    filename = CODE_FILE.split("/")[-1].split(".")[0]
    output_path = f"example_outputs/{filename}.json"
    with open(output_path, "w") as out:
        issues_dicts = [issue.model_dump() for issue in issues]
        json.dump(issues_dicts, out, indent=2)
        logger.info(f"✅ Saved {len(issues)} issue(s) to {output_path}")

def main_test():
    CODE_FILE = "examples/example_code5.py"
    issues = get_issues_with_chunks(CODE_FILE)
    
    filename = CODE_FILE.split("/")[-1].split(".")[0]
    output_path = f"example_outputs/{filename}.json"
    with open(output_path, "w") as out:
        json.dump(issues, out, indent=2)
        logger.info(f"✅ Saved {len(issues)} issue(s) to {output_path}")

if __name__ == "__main__":
    main()
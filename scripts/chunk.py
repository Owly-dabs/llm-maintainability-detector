import os
from typing import List, Dict

CHUNKING_LINE_THRESHOLD = 400
CHUNK_MAX_LINES = 140
CHUNK_MIN_LINES = 60

def should_chunk(code: str) -> bool:
    """Return True if code exceeds the chunking threshold."""
    return len(code.splitlines()) >= CHUNKING_LINE_THRESHOLD

def is_split_point(line: str) -> bool:
    """Heuristic rules for splitting based on code structure."""
    trimmed = line.strip()
    return (
        trimmed.startswith("def ") or
        trimmed.startswith("class ") or
        trimmed.startswith("#") or
        trimmed.startswith("//") or
        trimmed.startswith("/*") or
        trimmed == ""
    )

def chunk_code_by_structure(code: str) -> List[Dict]:
    """
    Chunk code using simple structural heuristics (functions, classes, comments, blank lines).
    Ensures each chunk is between CHUNK_MIN_LINES and CHUNK_MAX_LINES.

    Returns:
        List[Dict]: Each dictionary contains 'id', 'lines', and 'content'.
    """
    lines = code.splitlines()
    chunks = []
    current_chunk = []
    start_line = 0

    for idx, line in enumerate(lines):
        current_chunk.append(line)
        if len(current_chunk) >= CHUNK_MAX_LINES or is_split_point(line):
            if len(current_chunk) >= CHUNK_MIN_LINES:
                end_line = idx + 1
                chunks.append({
                    "id": len(chunks),
                    "lines": f"{start_line + 1}-{end_line}",
                    "content": "\n".join(current_chunk)
                })
                current_chunk = []
                start_line = idx + 1

    if current_chunk:
        end_line = len(lines)
        if chunks and len(current_chunk) < CHUNK_MIN_LINES:
            # Merge with previous chunk if it's small
            chunks[-1]["content"] += "\n" + "\n".join(current_chunk)
            chunks[-1]["lines"] = f"{chunks[-1]['lines'].split('-')[0]}-{end_line}"
        else:
            chunks.append({
                "id": len(chunks),
                "lines": f"{start_line + 1}-{end_line}",
                "content": "\n".join(current_chunk)
            })

    return chunks

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Chunk Python code based on structure.")
    parser.add_argument("code_file", type=str, help="Path to the Python file to be chunked.")
    parser.add_argument("--output", default=None, help="Optional path to save chunked output")
    args = parser.parse_args()

    with open(args.code_file) as f:
        code = f.read()

    if should_chunk(code):
        print("📦 Chunking code...")
        chunks = chunk_code_by_structure(code)
        for chunk in chunks:
            print(f"\n--- Chunk {chunk['id'] + 1} ({chunk['lines']}) ---\n")
            print(chunk['content'][:500])
            print("\n... (truncated for display)")
        
        if args.output:
            with open(args.output, "w") as out_file:
                for chunk in chunks:
                    out_file.write(f"--- Chunk {chunk['id'] + 1} ({chunk['lines']}) ---\n")
                    out_file.write(chunk['content'] + "\n\n")
            print(f"\n📝 Output saved to {args.output}")
    else:
        print("✅ Code is short enough for full evaluation.")


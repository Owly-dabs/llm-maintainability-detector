import sys, os
# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.datatypes import Chunk
from utils.logger import logger

CHUNKING_LINE_THRESHOLD = 400
CHUNK_MAX_LINES = 140
CHUNK_MIN_LINES = 60

def should_chunk(code: str) -> bool:
    """Return True if code exceeds the chunking threshold."""
    return len(code.splitlines()) >= CHUNKING_LINE_THRESHOLD

def is_split_point_python(line: str, next_line: str | None = None) -> bool:
    stripped = line.strip()
    return (
        stripped.startswith(("def ", "class ", "@")) or
        (stripped == "" and next_line and not next_line.startswith((" ", "\t"))) # Check this: Doesn't seem to work
    )

def is_split_point_curly(line: str, next_line: str | None = None) -> bool:
    stripped = line.strip()
    return (
        stripped.endswith("{") or
        stripped.startswith(("function", "class")) or
        stripped == ""
    )

def is_split_point_vbnet(line: str, next_line: str | None = None) -> bool:
    stripped = line.strip().lower()
    return (
        stripped.startswith(("sub ", "function ", "class ", "module ")) or
        stripped.startswith(("end sub", "end function", "end class", "end module")) or
        stripped == "" or
        stripped.startswith("'")
    )

def is_split_point_cobol(line: str, next_line: str | None = None) -> bool:
    stripped = line.strip().upper()
    return (
        stripped.endswith("DIVISION.") or
        stripped.endswith("SECTION.") or
        stripped.startswith("PARAGRAPH") or
        stripped.startswith("PERFORM") or
        stripped.startswith("END-PERFORM") or
        stripped == ""
    )
 
LANGUAGE_HEURISTICS = {
    "python": is_split_point_python,
    "javascript": is_split_point_curly,
    "typescript": is_split_point_curly,
    "c": is_split_point_curly,
    "cpp": is_split_point_curly,
    "java": is_split_point_curly,
    "vbnet": is_split_point_vbnet,
    "cobol": is_split_point_cobol,
}   

def detect_language_from_filename(filename: str) -> str:
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

#TODO: identify language from file extension or content
#TODO: add support for curly braces languages
#TODO: add support for indentation (char 0 is not a whitespace character in Python) (more repeatable way for other languages)
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


def chunk_code_by_structure(code: str, language: str) -> list[Chunk]:
    """
    Chunk code using structural heuristics appropriate for the given language.
    Supports Python, curly-brace, VB.NET, and COBOL syntax.

    Args:
        code (str): The source code to chunk.
        language (str): Programming language to determine chunking heuristics.

    Returns:
        list[Chunk]: List of code chunks with line ranges and content.
    """
    lines = code.splitlines()
    chunks: list[Chunk] = []
    current_chunk = []
    start_line = 0

    split_func = LANGUAGE_HEURISTICS.get(language.lower())
    if not split_func:
        raise ValueError(f"Unsupported language for chunking: {language}")

    for idx, line in enumerate(lines):
        next_line = lines[idx + 1] if idx + 1 < len(lines) else None

        if len(current_chunk) >= CHUNK_MAX_LINES or split_func(line, next_line):
            if len(current_chunk) >= CHUNK_MIN_LINES:
                end_line = idx + 1
                chunk = Chunk(
                    id=len(chunks),
                    lines=f"{start_line + 1}-{end_line}",
                    content="\n".join(current_chunk)
                )
                chunks.append(chunk)
                current_chunk = []
                start_line = idx + 1

        current_chunk.append(line)

    # Final chunk or merge with previous if too small
    if current_chunk:
        end_line = len(lines)
        if chunks and len(current_chunk) < CHUNK_MIN_LINES:
            prev_chunk = chunks[-1]
            prev_chunk.content += "\n" + "\n".join(current_chunk)
            prev_chunk.lines = f"{prev_chunk.lines.split('-')[0]}-{end_line}"
        else:
            chunk = Chunk(
                id=len(chunks),
                lines=f"{start_line + 1}-{end_line}",
                content="\n".join(current_chunk)
            )
            chunks.append(chunk)

    return chunks

def chunk_file(file_content: str, output_file: None | str) -> str:
    pass

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Chunk code based on structure.")
    parser.add_argument("code_file", type=str, help="Path to the file to be chunked.")
    parser.add_argument("--output", default=None, help="Optional path to save chunked output")
    args = parser.parse_args()

    # chunk_file(args.code_file, args.output)
    with open(args.code_file) as f:
        code = f.read()
        language = detect_language_from_filename(args.code_file)
        if should_chunk(code):
            logger.info("📦 Chunking code...")
            chunks = chunk_code_by_structure(code, language)
            for chunk in chunks:
                logger.info(f"\n--- Chunk {chunk.id + 1} ({chunk.lines}) ---\n{chunk.content[:500]}\n... (truncated for display)")
            
            if args.output:
                with open(args.output, "w") as out_file:
                    for chunk in chunks:
                        out_file.write(f"--- Chunk {chunk.id + 1} ({chunk.lines}) ---\n")
                        out_file.write(chunk.content + "\n\n")
                logger.info(f"\n📝 Output saved to {args.output}")
        else:
            logger.info("✅ Code is short enough for full evaluation.")


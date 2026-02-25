import re
from google.genai import types


# Function declaration for Gemini function calling
analyze_code_declaration = types.FunctionDeclaration(
    name="analyze_code",
    description=(
        "Analyze a code snippet and return detailed stats including "
        "total lines, blank lines, comment lines, import count, "
        "function names, class names, main guard detection, "
        "longest function info, and complexity hints."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "code": types.Schema(
                type=types.Type.STRING,
                description="The code snippet to analyze",
            ),
        },
        required=["code"],
    ),
)


def _find_longest_function(lines: list[str]) -> dict:
    """Find the longest function by counting lines from its 'def' to the next
    top-level statement (or end of file). Uses indentation to detect the block."""
    best_name = None
    best_length = 0

    i = 0
    while i < len(lines):
        match = re.match(r"^(\s*)def\s+(\w+)", lines[i])
        if match:
            indent_level = len(match.group(1))
            func_name = match.group(2)
            start = i
            i += 1
            # Walk through the body: any line that is blank or indented deeper
            while i < len(lines):
                stripped = lines[i].rstrip()
                if stripped == "":
                    i += 1
                    continue
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if current_indent > indent_level:
                    i += 1
                else:
                    break
            length = i - start
            if length > best_length:
                best_length = length
                best_name = func_name
        else:
            i += 1

    if best_name:
        return {"name": best_name, "lines": best_length}
    return {"name": None, "lines": 0}


def _get_complexity_hints(lines: list[str]) -> list[str]:
    """Return simple complexity hints based on the code."""
    hints = []

    # Check max indentation depth
    max_depth = 0
    for line in lines:
        stripped = line.rstrip()
        if stripped and not stripped.startswith("#"):
            indent = len(line) - len(line.lstrip())
            # Assume 4-space indentation
            depth = indent // 4
            max_depth = max(max_depth, depth)

    if max_depth >= 5:
        hints.append(f"Deeply nested code detected (max depth: {max_depth} levels)")
    elif max_depth >= 3:
        hints.append(f"Moderate nesting detected (max depth: {max_depth} levels)")

    # Check for long lines
    long_lines = sum(1 for line in lines if len(line.rstrip()) > 100)
    if long_lines > 0:
        hints.append(f"{long_lines} line(s) exceed 100 characters")

    # Check for global variables (simple heuristic: top-level assignments that
    # are not imports, not function/class defs, and not comments)
    for line in lines:
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith(("#", "import ", "from ", "def ", "class ", "if ", "@"))
            and "=" in stripped
            and not line[0].isspace()
        ):
            hints.append("Possible global variable(s) detected")
            break

    if not hints:
        hints.append("Code looks clean — no complexity issues found")

    return hints


def analyze_code(code: str) -> dict:
    """Analyze the given code and return detailed stats."""
    lines = code.strip().split("\n")
    total_lines = len(lines)

    blank_lines = sum(1 for line in lines if line.strip() == "")
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))

    # Count imports
    import_count = sum(
        1
        for line in lines
        if line.strip().startswith("import ") or line.strip().startswith("from ")
    )

    # Extract function and class names
    function_names = re.findall(r"^\s*def\s+(\w+)", code, re.MULTILINE)
    class_names = re.findall(r"^\s*class\s+(\w+)", code, re.MULTILINE)

    # Check for main guard
    has_main_guard = 'if __name__' in code and '"__main__"' in code or "'__main__'" in code

    # Longest function
    longest_function = _find_longest_function(lines)

    # Complexity hints
    complexity_hints = _get_complexity_hints(lines)

    return {
        "total_lines": total_lines,
        "blank_lines": blank_lines,
        "comment_lines": comment_lines,
        "import_count": import_count,
        "function_names": function_names,
        "class_names": class_names,
        "has_main_guard": has_main_guard,
        "longest_function": longest_function,
        "complexity_hints": complexity_hints,
    }
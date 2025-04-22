import re
import json

def divide_blocks(js_code: str):
    lines = js_code.strip().splitlines()
    blocks = []
    current_block = []
    block_id = 1
    brace_depth = 0

    def flush_block():
        nonlocal current_block, block_id
        if not current_block:
            return

        trimmed = [l.strip() for l in current_block]
        is_only_brace = len(trimmed) == 1 and trimmed[0] == "}"

        if not is_only_brace:
            blocks.append({
                "id": block_id,
                "code": "\n".join(current_block).strip(),
                "successors": []  # Not handled for now
            })
            block_id += 1

        current_block = []

    for i, line in enumerate(lines):
        trimmed = line.strip()
        if not trimmed:
            continue

        # Update brace depth
        brace_depth += len(re.findall(r"{", line))
        brace_depth -= len(re.findall(r"}", line))

        current_block.append(line)

        is_control = re.match(r"^(if|else|for|while|switch|function)\b", trimmed)
        is_ender = re.match(r"^(return|break|continue|throw)\b", trimmed)
        ends_with_semicolon = trimmed.endswith(";")
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        should_flush = (
            (is_control and brace_depth == 1 and len(current_block) == 1)
            or is_ender
            or ends_with_semicolon
            or (brace_depth == 0 and not next_line)
        )

        if should_flush:
            flush_block()

    # Final flush
    flush_block()

    return blocks


# For debug/test
if __name__ == "__main__":
    import sys

    input_code = sys.stdin.read()
    blocks = divide_blocks(input_code)
    print(json.dumps(blocks, indent=2))

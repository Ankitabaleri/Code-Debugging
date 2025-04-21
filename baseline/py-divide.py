import json
import subprocess

def divide_buggy_code(js_code: str):
    """
    Divides buggy JS code into approximate control-flow blocks using a Node.js script.
    """
    process = subprocess.Popen(
        ['node', 'divide.js'],  # purely heuristic-based script
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate(input=js_code.encode())

    stdout_str = stdout.decode().strip()
    stderr_str = stderr.decode().strip()

    if process.returncode != 0:
        print("[Node.js STDERR]", stderr_str)
        return None, stderr_str
    elif not stdout_str:
        print("[Node.js STDOUT is empty]")
        print("[Node.js STDERR]", stderr_str)
        return None, "No output from Node.js"
    else:
        try:
            return json.loads(stdout_str), None
        except json.JSONDecodeError as e:
            print("[Node.js STDOUT]", stdout_str)
            print("[JSON Decode Error]", str(e))
            return None, f"JSON parse error: {e}"


# Example usage for a file with buggy JS code
file_path = "../mbpp_js_cleaned_3.jsonl"

with open(file_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"[Line {idx}] Skipped due to JSON error: {e}")
            continue

        buggy_code = data.get("buggy_code")
        if not buggy_code:
            print(f"[Line {idx}] No buggy_code found.")
            continue

        blocks, error = divide_buggy_code(buggy_code)

        if error:
            print(f"[Line {idx}] Error: {error}")
        else:
            print(f"[Line {idx}] Divided Blocks:")
            for block in blocks:
                print(f"Block ID: {block['id']}")
                print(block['code'])
                print("=" * 40)
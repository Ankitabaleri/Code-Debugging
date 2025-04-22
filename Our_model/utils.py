import json
import os


# --------------------
# JSONL file utilities
# --------------------

def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, data, append=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "a" if append else "w"
    with open(path, mode, encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_jsonl_gz(path):
    import gzip
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# --------------------
# Debugging utilities
# --------------------

def make_printv(verbose):
    def printv(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)
    return printv


def count_solved(path):
    data = read_jsonl(path)
    count = 0
    for item in data:
        if item.get("fixed_code") and "solution" not in item:  # Customize if you also set solution
            count += 1
    return count


# --------------------
# Constants
# --------------------

IMPORT_HEADER = ""  # not used in JS but kept for compatibility

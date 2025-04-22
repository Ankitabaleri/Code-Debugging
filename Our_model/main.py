# main.py

import os
import argparse
from utils import read_jsonl, read_jsonl_gz
from ldb_debugger import run_ldb


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_name", type=str, default="output", help="Run name (used for saving logs)")
    parser.add_argument("--dataset_path", type=str, default="/Users/ankita/Documents/NLP/project/Code-Debugging/Our_model/data.jsonl", help="Path to dataset (jsonl or jsonl.gz)")
    parser.add_argument("--root_dir", type=str, default="root", help="Directory to save results")
    parser.add_argument("--model", type=str, default="bigcode/starcoder", help="Name of model to use")
    parser.add_argument("--port", type=str, default="8000", help="Port for vLLM model like StarCoder")
    parser.add_argument("--level", type=str, default="block", help="Trace granularity level (block, line, function)")
    parser.add_argument("--verbose", action="store_true", help="Print debug messages")
    parser.add_argument("--max_iters", type=int, default=5, help="Maximum number of model iterations to fix bugs")
    return parser.parse_args()


def main():
    args = get_args()

    # Create output directory
    os.makedirs(args.root_dir, exist_ok=True)
    log_dir = os.path.join(args.root_dir, args.run_name)
    os.makedirs(log_dir, exist_ok=True)

    # Load dataset
    print(f"[+] Loading dataset from {args.dataset_path}")
    if args.dataset_path.endswith(".jsonl"):
        dataset = read_jsonl(args.dataset_path)
    else:
        raise ValueError("Unsupported dataset format (must be .jsonl or .jsonl.gz)")

    print(f"[+] Loaded {len(dataset)} items from dataset.")

    log_path = os.path.join(log_dir, f"ldb_debugger_log.jsonl")

    # Run the LDB debugger
    run_ldb(
        dataset=dataset,
        model_name=args.model,
        port=args.port,
        log_path=log_path,
        trace_level=args.level,
        verbose=args.verbose,
        max_iters=args.max_iters
        
    )

    print(f"[✓] Finished. Results written to: {log_path}")


if __name__ == "__main__":
    main()

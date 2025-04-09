import json
import os
import torch
import subprocess
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

# ------------ Setup Logging ----------------
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', 
                    handlers=[logging.FileHandler('debug_log.log', mode='w'), logging.StreamHandler()])

# ------------ Load model once ----------------
print("Loading Starcoder model locally...")
model_name = "bigcode/starcoder"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = model.half().to("cuda" if torch.cuda.is_available() else "cpu")
model.eval()

# ------------ Helper to generate completion with logprobs ----------------
def generate_completion_with_uncertainty(prompt, max_new_tokens=300):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=0.2,
            output_scores=True,
            return_dict_in_generate=True
        )
    sequences = outputs.sequences
    scores = outputs.scores
    completion = tokenizer.decode(sequences[0], skip_special_tokens=True)

    # Calculate average token log probability
    avg_logprob = None
    if scores:
        token_logprobs = torch.stack([torch.log_softmax(score, dim=-1).max(dim=-1).values for score in scores])
        avg_logprob = token_logprobs.mean().item()

    return completion, avg_logprob

# ------------ Helper to run JavaScript tests ----------------
def run_js_with_tests(js_function_code, test_list):
    file_name = "temp_test.js"

    combined_code = js_function_code + "\n" + "\n".join(test_list)

    with open(file_name, "w") as f:
        f.write(combined_code)

    try:
        result = subprocess.run(["node", file_name], capture_output=True, text=True, timeout=5)

        if result.stderr:
            logging.error(f"Test failed with error:\n{result.stderr}")
            return False
        else:
            logging.info("All selected tests passed!")
            return True

    except subprocess.TimeoutExpired:
        logging.error("Execution timed out!")
        return False

    except Exception as e:
        logging.error(f"Error during JS execution: {e}")
        return False

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# ------------ Helper to split code into blocks ----------------
'''def split_into_blocks(js_code):
    blocks = []
    current_block = []
    open_braces = 0
    for line in js_code.splitlines():
        stripped = line.strip()
        if stripped == "":
            continue
        current_block.append(line)
        open_braces += line.count("{")
        open_braces -= line.count("}")
        if open_braces == 0 and current_block:
            blocks.append("\n".join(current_block))
            current_block = []
    if current_block:
        blocks.append("\n".join(current_block))
    return blocks'''

# ------------ Load dataset ----------------

dataset_path = "mbpp_js_cleaned_3.jsonl"  # your single merged file

examples = [json.loads(line) for line in open(dataset_path)]

# ------------ Run over examples ----------------

output_dir = "../output_data/basic/your_dataset/starcoder/"
os.makedirs(output_dir, exist_ok=True)

results = []

UNCERTAINTY_THRESHOLD = -2.0  # Adjust based on experiments
MAX_ITERS = 10

correct_count = 0
code_exact_count = 0

for i, example in enumerate(tqdm(examples)):
    buggy_code = example['buggy_code']
    correct_code = example['code']
    test_list = example['test_list']

    logging.info(f"\n--- Running test #{i+1} ---")

    passed = False
    is_code_exact = False

    for attempt in range(MAX_ITERS):
        logging.info(f"Attempt {attempt+1}/{MAX_ITERS}")

        # Split buggy code into blocks
        code_blocks = split_into_blocks(buggy_code)

        fixed_blocks = []
        for idx, block in enumerate(code_blocks):
            logging.info(f"Evaluating block #{idx+1}")

            _, avg_logprob = generate_completion_with_uncertainty(block)

            if avg_logprob is not None and avg_logprob < UNCERTAINTY_THRESHOLD:
                logging.info(f"Block #{idx+1} is uncertain (avg_logprob={avg_logprob:.4f}), regenerating.")
                fixed_block, _ = generate_completion_with_uncertainty(block)
            else:
                logging.info(f"Block #{idx+1} is confident (avg_logprob={avg_logprob:.4f}), keeping original.")
                fixed_block = block

            fixed_blocks.append(fixed_block)

        # Merge fixed blocks back
        final_fixed_code = "\n".join(fixed_blocks)

        # Run tests
        passed = run_js_with_tests(final_fixed_code, test_list)

        # Compare generated code with ground truth
        is_code_exact = (final_fixed_code.strip() == correct_code.strip())

        if passed or is_code_exact:
            logging.info(f"Success on attempt {attempt+1}")
            break

    if passed:
        correct_count += 1
    if is_code_exact:
        code_exact_count += 1

    result = {
        "source_file": example.get("source_file", "unknown"),
        "prompt_text": example.get("text", ""),
        "buggy_code": buggy_code,
        "fixed_code": final_fixed_code,
        "passed_tests": passed,
        "code_exact_match": is_code_exact
    }
    results.append(result)

# ------------ Save results ----------------

output_path = os.path.join(output_dir, "debug_results.jsonl")
with open(output_path, "w") as f:
    for item in results:
        f.write(json.dumps(item) + "\n")

# ------------ Print final accuracy ----------------

total = len(examples)
print(f"\n================ Final Evaluation ================" )
print(f"Pass@1 Test Accuracy: {correct_count}/{total} ({100*correct_count/total:.2f}%)")
print(f"Exact Code Match: {code_exact_count}/{total} ({100*code_exact_count/total:.2f}%)")
print(f"===================================================")

logging.info(f"Pass@1 Test Accuracy: {correct_count}/{total} ({100*correct_count/total:.2f}%)")
logging.info(f"Exact Code Match: {code_exact_count}/{total} ({100*code_exact_count/total:.2f}%)")

print(f"Done! Saved results to {output_path}")

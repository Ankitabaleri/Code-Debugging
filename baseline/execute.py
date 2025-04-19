import json
import subprocess
import os
import math
import logging
from model import StarcoderAPIClient


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', 
                    handlers=[logging.FileHandler('debug_log.log', mode='w'), logging.StreamHandler()])

def run_js_with_tests(js_function_code: str, test_list: list[str]) -> bool:
    file_name = "temp_script.js"

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

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


file_path = "../mbpp_js_cleaned_3.jsonl"
correct = 0
total = 0

with open(file_path, "r") as file:
    common_prompt = "This is a buggy javascript code. Fix this and give the right javascript code. Add necessary imports. Only give the Javascript code and not any text and testcases."
    results = []
    os.makedirs("output_baseline", exist_ok=True)
    count = 0
    for i, line in enumerate(file):
        total += 1
        count+=1
        try:
            item = json.loads(line)
            buggy_code = item.get("buggy_code", "")
            test_list = item.get("test_list", [])
            prompt = item.get("text", "")
            client = StarcoderAPIClient()
    
            # Define your code prompt
            #prompt_code = '/*'+common_prompt + '\n\n' + prompt +'*/\n' + buggy_code
            prompt_code = """// File: fix_bug.js
// Task: This is a buggy javascript code. Fix this and give the right javascript code. Add necessary imports. Only give the Javascript code and not any text and testcases.
// Description: {}

{}

// Fixed version:""".format(prompt.strip(), buggy_code.strip())
            logging.info(prompt_code)
            generated_code = client.generate_completion(prompt_code)
            logging.info(generated_code)

            # Taking around 50% of testcase as hidden
            total_tests = len(test_list)
            start_index = math.floor(total_tests * 0.5)
            hidden_tests = test_list[start_index:]

            passed = False

            logging.info(f"\n--- Running test #{i+1} ---")
            if run_js_with_tests(generated_code, hidden_tests):
                correct += 1
                passed = True

            result = {
                    "source_file": i,
                    "prompt_text": prompt,
                    "buggy_code": buggy_code,
                    "fixed_code": generated_code,
                    "is_solved": passed,
                }
            results.append(result)
            
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON at line {i+1}")
    output_path = os.path.join("output_baseline", "debug_results.jsonl")
    with open(output_path, "w") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")

logging.info(f"Accuracy: {correct/total:.2f}")

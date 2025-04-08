import json
import subprocess
import os
import math
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', 
                    handlers=[logging.FileHandler('test_log.log', mode='w'), logging.StreamHandler()])

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
    for i, line in enumerate(file):
        total += 1
        try:
            item = json.loads(line)
            buggy_code = item.get("buggy_code", "")
            test_list = item.get("test_list", [])

            # Taking around 70% of testcase as hidden
            total_tests = len(test_list)
            start_index = math.floor(total_tests * 0.3)
            hidden_tests = test_list[start_index:]

            logging.info(f"\n--- Running test #{i+1} ---")
            if run_js_with_tests(buggy_code, hidden_tests):
                correct += 1
            break
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON at line {i+1}")

logging.info(f"Accuracy: {correct/total:.2f}")

import subprocess
import os
import logging

def run_js_with_tests(js_function_code: str, test_list: list[str]) -> bool:
    file_name = "temp_script.js"

    for i in range(0, len(test_list)):
        combined_code = js_function_code + "\n".join(test_list[i])
        with open(file_name, "w") as f:
            f.write(combined_code)

        try:
            result = subprocess.run(["node", file_name], capture_output=True, text=True, timeout=5)

            if result.stderr:
                logging.error(f"Test failed with error:\n{result.stderr}")
                return False, test_list[i]
            else:
                logging.info("All selected tests passed!")
                return True, None

        except subprocess.TimeoutExpired:
            logging.error("Execution timed out!")
            return False, test_list[i]

        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
    return True, None

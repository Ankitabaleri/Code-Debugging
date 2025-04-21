import json
import time
from traces import trace_js_execution
from divide import divide_blocks
from model import Message, ModelBase
from utils import write_jsonl


def parse_model_feedback(explanation_text):
    parsed = []
    for line in explanation_text.strip().split("\n"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            parsed.append(json.loads(line))
        except:
            continue
    return parsed


def run_ldb(dataset, model_name, log_path, max_iters=1, **kwargs):
    from generators import model_factory
    model = model_factory(model_name, kwargs.get("port", ""))

    for i, item in enumerate(dataset):
        print(f"\n===== Example {i + 1} / {len(dataset)} =====")
        buggy_code = item.get("buggy_code") or item["code"]
        tests = item["test_list"]
        test_input = tests[0].replace("console.assert(", "").split("===")[0].strip()
        entry_point = item.get("entry_point", "classify_integer")

        print("[+] Splitting code into CFG blocks...")
        blocks = divide_blocks(buggy_code)

        for attempt in range(max_iters):
            print(f"[+] Attempt {attempt + 1} of {max_iters}")

            print("[+] Getting trace for the entry test...")
            entry_call_str = f"{entry_point}({test_input})"
            trace_blocks = trace_js_execution("\n\n".join(block['code'] for block in blocks), entry_call=test_input)

            if isinstance(trace_blocks, str) and trace_blocks.startswith("*"):
                print(f"[-] Trace error: {trace_blocks}")
                break

            messages = [
                Message(role="system", content="You are a debugging assistant. Analyze each block for correctness."),
            ]

            user_msg = "### Debug Start\n## Execution Trace with CFG Blocks\n"
            for i, block in enumerate(trace_blocks):
                user_msg += f"[BLOCK-{i}]\n" + "\n".join(block) + "\n"

            user_msg += ("\nFor each block, respond with a JSON object like this:\n"
                         '{"block": "BLOCK-1", "correct": true, "explanation": "..."}')

            messages.append(Message(role="user", content=user_msg))

            print("[+] Sending to StarCoder...")
            start = time.time()
            try:
                explanation = model.generate_chat(messages=messages, temperature=0, stop=["[debug end]"])
            except Exception as e:
                print(f"[-] Model call failed: {e}")
                break
            print(f"[✓] Response received in {time.time() - start:.2f} seconds")

            feedback = parse_model_feedback(explanation)

            fixed_any = False
            for fb in feedback:
                if not fb.get("correct", True):
                    block_id = int(fb["block"].replace("BLOCK-", ""))
                    faulty_code = blocks[block_id]['code']

                    fix_prompt = (f"This code block is incorrect:\n```js\n{faulty_code}\n````")
                    fix_prompt += f"\nExplanation: {fb['explanation']}\nPlease fix this code block and return the corrected JavaScript."

                    fix_msg = [Message(role="user", content=fix_prompt)]
                    try:
                        fixed = model.generate_chat(messages=fix_msg)
                        blocks[block_id]['code'] = fixed.strip()
                        fixed_any = True
                    except Exception as e:
                        print(f"[-] Fix generation failed: {e}")

            if not fixed_any:
                print("[✓] No more fixes needed. Stopping early.")
                break

        fixed_code = "\n\n".join(block['code'] for block in blocks)
        item['fixed_code'] = fixed_code
        write_jsonl(log_path, [item], append=True)

        print("[+] Debugging complete. Fixed code written.")

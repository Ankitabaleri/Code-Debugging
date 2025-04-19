import re

def trace_js_execution(js_code: str, entry_call: str = None) -> list:
    """
    Takes raw JS code (as string), instruments it, runs it, and returns trace output lines.
    If no function call is present, an entry_call string like 'myFunc("123")' can be appended.
    """

    def instrument_js_with_trace_logs(js_code: str, starting_lineno: int = 1) -> str:
        lines = js_code.strip().split('\n')
        instrumented = []
        lineno = starting_lineno

        for line in lines:
            stripped = line.strip()
            indent = ' ' * (len(line) - len(stripped))

            if stripped.startswith('return '):
                ret_expr = stripped[len("return "):].rstrip(';')
                instrumented.append(f'{indent}_ret = {ret_expr};')
                instrumented.append(f'{indent}console.log("({lineno}):      return {ret_expr};");')
                instrumented.append(f'{indent}return _ret;')
            else:
                instrumented.append(line)

            if (
                not stripped or 
                stripped in ('{', '}') or
                stripped.startswith('//') or 
                stripped.startswith('/*') or 
                stripped.startswith('*') or 
                stripped.startswith('*/') or
                stripped == '/' or 
                re.match(r'^function\s+\w+\s*\(.*\)\s*\{?$', stripped)
            ):
                lineno += 1
                continue

            escaped = stripped.replace('"', '\\"')
            log = f'{indent}console.log("({lineno}):      {escaped}");'
            instrumented.append(log)
            lineno += 1

        return '\n'.join(instrumented)

    def fix_misplaced_js_comments(js_code: str) -> str:
        js_code = re.sub(r"\n/\s*\n", "\n/*\n", js_code)
        pattern = r"(function\s+\w+\s*\([^\)]*\))\s*\n(/\*[\s\S]*?\*/)\s*\n(\{)"
        return re.sub(pattern, r"\2\n\1\n\3", js_code)

    def get_trace_output(js_code: str) -> str:
        import subprocess, random, os

        fixed_code = fix_misplaced_js_comments(js_code)
        tmp_name = f".tmp.js.{random.randint(0, 10000)}"
        with open(tmp_name, "w") as f:
            f.write(fixed_code)

        try:
            result = subprocess.run(
                ["node", tmp_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                check=True
            )
            output = result.stdout.decode('utf-8')
        except subprocess.TimeoutExpired:
            output = "*timeout*"
        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.decode('utf-8')
            if "SyntaxError" in stderr_output:
                output = "*syntax error*"
            else:
                output = f"*execution fail*\n{stderr_output}"
        except Exception as e:
            output = f"*execution fail (unknown)*\n{str(e)}"
        finally:
            os.remove(tmp_name)

        return output

    def get_trace_line(trace_output: str):
        lines = trace_output.strip().splitlines()
        trace = []
        for line in lines:
            match = re.match(r"\((\d+)\):\s+(.*)", line)
            if match:
                lineno = int(match.group(1))
                code = match.group(2)
                if not code.strip().startswith(('//', '/*', '*')):
                    trace.append((lineno, code))
        return trace

    # Add entry call if not already present and requested
    if entry_call and not re.search(re.escape(entry_call.split("(")[0]), js_code):
        js_code += f"\n{entry_call}"

    instrumented_code = instrument_js_with_trace_logs(js_code)
    raw_output = get_trace_output(instrumented_code)

    return get_trace_line(raw_output)

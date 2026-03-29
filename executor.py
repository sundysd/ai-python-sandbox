# executor.py
import multiprocessing
from validator import is_safe
from logger import log_info, log_error
import io
import sys

# Safe builtins for sandbox
SAFE_BUILTINS = {
    "print": print,
    "sum": sum,
    "range": range,
    "len": len,
    "min": min,
    "max": max,
    "abs": abs,
}

class TimeoutException(Exception):
    pass

def _run_code(code, return_dict):
    try:
        safe_globals = {"__builtins__": SAFE_BUILTINS}
        buffer = io.StringIO()
        sys.stdout = buffer
        exec(code, safe_globals)
        sys.stdout = sys.__stdout__
        return_dict["success"] = True
        return_dict["result"] = buffer.getvalue() or "✅ Success"
    except Exception as e:
        sys.stdout = sys.__stdout__
        return_dict["success"] = False
        return_dict["result"] = str(e)

def execute_code(code, timeout=5):
    """
    Execute Python code safely:
    - AST check
    - Safe builtins
    - Timeout
    - Process isolation
    """
    if not is_safe(code):
        return False, "❌ Unsafe code detected!"

    log_info(code)

    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    # Run user code in a separate process
    p = multiprocessing.Process(target=_run_code, args=(code, return_dict))
    p.start()
    p.join(timeout)

    if p.is_alive():
        # Timeout: kill process
        p.terminate()
        p.join()
        log_error("Execution timed out")
        return False, "❌ Timeout: execution took too long"

    # Return result
    success = return_dict.get("success", False)
    result = return_dict.get("result", "❌ Unknown error")

    if not success:
        log_error(result)

    return success, result

# executor.py
if __name__ == "__main__":
    # Only run test code here, never execute sandbox code at import
    pass
import ast

# Example: safe code checker
FORBIDDEN_NODES = (
    ast.Import,      # import statements
    ast.ImportFrom,
)

FORBIDDEN_FUNCS = ("open", "eval", "exec", "compile", "exit", "quit", "subprocess", "os", "sys", "fork", "popen")
FORBIDDEN_NAMES = ("__import__",)

def is_safe(code: str) -> tuple[bool, str]:
    """
    Check if code is safe.
    Returns (True, "Code is safe") or (False, reason)
    """
    try:
        tree = ast.parse(code, mode='exec')
    except Exception as e:
        return False, f"Syntax Error: {e}"

    for node in ast.walk(tree):
        if isinstance(node, FORBIDDEN_NODES):
            return False, f"Use of forbidden node: {type(node).__name__}"

        if isinstance(node, ast.Call):
            # get function name and attribute chain
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    func_name = f"{node.func.value.id}.{node.func.attr}"
                else:
                    func_name = node.func.attr

            if func_name:
                for forbidden in FORBIDDEN_FUNCS:
                    if func_name == forbidden or func_name.startswith(f"{forbidden}."):
                        return False, f"Use of forbidden function: {func_name}"

        if isinstance(node, ast.Name):
            if node.id in FORBIDDEN_NAMES:
                return False, f"Use of forbidden name: {node.id}"

    return True, "Code is safe"
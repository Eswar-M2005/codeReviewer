import ast

def read_python_file(py_file):
    with open(py_file, "r", encoding="utf-8") as f:
        return f.read()

def detect_issues_ast(code):
    issues = []
    tree = ast.parse(code)

    # For unused variable detection
    assigned_vars = set()
    used_vars = set()

    # Track imports
    imported_names = set()
    used_imports = set()

    for node in ast.walk(tree):

        # ===============================
        # UNUSED VARIABLE
        # ===============================
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned_vars.add(target.id)

        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_vars.add(node.id)

        # ===============================
        # UNUSED IMPORT
        # ===============================
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name.split('.')[0])

        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.name)

        # ===============================
        # TOO MANY ARGUMENTS
        # ===============================
        if isinstance(node, ast.FunctionDef):
            if len(node.args.args) > 5:
                issues.append("too_many_arguments")

        # ===============================
        # LONG FUNCTION
        # ===============================
        if isinstance(node, ast.FunctionDef):
            if len(node.body) > 20:
                issues.append("long_function")

        # ===============================
        # BARE EXCEPT
        # ===============================
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append("bare_except")

        # ===============================
        # USE OF EVAL OR EXEC
        # ===============================
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "eval":
                    issues.append("use_of_eval")
                if node.func.id == "exec":
                    issues.append("use_of_exec")

        # ===============================
        # HARDCODED PASSWORD
        # ===============================
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if "password" in target.id.lower():
                        if isinstance(node.value, ast.Constant):
                            issues.append("hardcoded_password")

        # ===============================
        # MAGIC NUMBER
        # ===============================
        if isinstance(node, ast.Constant):
            if isinstance(node.value, int):
                if node.value not in (0, 1):
                    issues.append("magic_number")

        # ===============================
        # NESTED LOOP
        # ===============================
        if isinstance(node, ast.For):
            for child in node.body:
                if isinstance(child, ast.For):
                    issues.append("nested_loop")

    # Detect unused variables
    unused_vars = assigned_vars - used_vars
    if unused_vars:
        issues.append("unused_variable")

    # Detect unused imports
    unused_imports = imported_names - used_vars
    if unused_imports:
        issues.append("unused_import")

    # Remove duplicates
    return list(set(issues))

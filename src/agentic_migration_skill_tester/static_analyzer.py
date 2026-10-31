import ast
from typing import Dict, List, Optional, Any

class StaticAnalysisIssue:
    def __init__(self, file: str, lineno: Optional[int], message: str):
        self.file = file
        self.lineno = lineno
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            'file': self.file,
            'lineno': self.lineno,
            'message': self.message
        }

    def __repr__(self):
        return f"StaticAnalysisIssue(file={self.file!r}, lineno={self.lineno!r}, message={self.message!r})"

class StaticAnalyzerResult:
    def __init__(self):
        self.issues: List[StaticAnalysisIssue] = []

    def add_issue(self, issue: StaticAnalysisIssue):
        self.issues.append(issue)

    def has_issues(self) -> bool:
        return bool(self.issues)

    def summary(self) -> List[Dict[str, Any]]:
        return [issue.to_dict() for issue in self.issues]

class StaticAnalyzer:
    """
    Performs static analysis on in-memory Python files to detect potential code breakages.
    Checks for syntax errors and undefined names (simple analysis).
    """
    def __init__(self, files: Dict[str, str]):
        self.files = files  # file path -> content

    def analyze(self) -> StaticAnalyzerResult:
        result = StaticAnalyzerResult()
        for path, content in self.files.items():
            if not path.endswith('.py'):
                continue  # Only analyze Python files
            # Syntax check
            try:
                tree = ast.parse(content, filename=path)
            except SyntaxError as e:
                result.add_issue(
                    StaticAnalysisIssue(
                        file=path,
                        lineno=e.lineno,
                        message=f"SyntaxError: {e.msg}"
                    )
                )
                continue
            # Check for undefined names (simple, not full type checking)
            undefined_names = self._find_undefined_names(tree)
            for name, lineno in undefined_names:
                result.add_issue(
                    StaticAnalysisIssue(
                        file=path,
                        lineno=lineno,
                        message=f"Potential undefined name: '{name}'"
                    )
                )
        return result

    def _find_undefined_names(self, tree: ast.AST) -> List[tuple]:
        """
        Returns a list of (name, lineno) for names used but not defined in the module scope.
        This is a simple heuristic, not a full static analysis.
        """
        defined = set()
        used = []  # (name, lineno)

        class NameVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                defined.add(node.name)
                for arg in node.args.args:
                    defined.add(arg.arg)
                self.generic_visit(node)
            def visit_AsyncFunctionDef(self, node):
                defined.add(node.name)
                for arg in node.args.args:
                    defined.add(arg.arg)
                self.generic_visit(node)
            def visit_ClassDef(self, node):
                defined.add(node.name)
                self.generic_visit(node)
            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined.add(target.id)
                self.generic_visit(node)
            def visit_AnnAssign(self, node):
                if isinstance(node.target, ast.Name):
                    defined.add(node.target.id)
                self.generic_visit(node)
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    used.append((node.id, node.lineno))
                self.generic_visit(node)
        NameVisitor().visit(tree)
        # Remove builtins from used
        import builtins
        builtin_names = set(dir(builtins))
        undefined = [(name, lineno) for name, lineno in used if name not in defined and name not in builtin_names]
        return undefined

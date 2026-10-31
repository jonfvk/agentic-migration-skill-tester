from typing import Dict, Any, List

class IssueReport:
    """
    Aggregates and formats detected issues or risks from migration validation.
    """
    def __init__(
        self,
        step_checker_result: Dict[str, List[str]],
        dependency_validation_result: Dict[str, List[str]],
        static_analysis_issues: List[Dict[str, Any]]
    ):
        self.step_checker_result = step_checker_result
        self.dependency_validation_result = dependency_validation_result
        self.static_analysis_issues = static_analysis_issues

    def has_issues(self) -> bool:
        return (
            any(self.step_checker_result.get('missing_steps')) or
            any(self.step_checker_result.get('conflicting_steps')) or
            any(self.dependency_validation_result.get('missing_dependencies')) or
            any(self.dependency_validation_result.get('version_conflicts')) or
            any(self.dependency_validation_result.get('invalid_versions')) or
            bool(self.static_analysis_issues)
        )

    def summary(self) -> Dict[str, Any]:
        return {
            'step_issues': {
                'missing_steps': self.step_checker_result.get('missing_steps', []),
                'conflicting_steps': self.step_checker_result.get('conflicting_steps', [])
            },
            'dependency_issues': {
                'missing_dependencies': self.dependency_validation_result.get('missing_dependencies', []),
                'version_conflicts': self.dependency_validation_result.get('version_conflicts', []),
                'invalid_versions': self.dependency_validation_result.get('invalid_versions', [])
            },
            'static_analysis_issues': self.static_analysis_issues
        }

    def format_report(self) -> str:
        lines = []
        # Step issues
        step_issues = self.step_checker_result
        if step_issues.get('missing_steps'):
            lines.append('Missing Steps:')
            for issue in step_issues['missing_steps']:
                lines.append(f'  - {issue}')
        if step_issues.get('conflicting_steps'):
            lines.append('Conflicting Steps:')
            for issue in step_issues['conflicting_steps']:
                lines.append(f'  - {issue}')
        # Dependency issues
        dep_issues = self.dependency_validation_result
        if dep_issues.get('missing_dependencies'):
            lines.append('Missing Dependencies:')
            for issue in dep_issues['missing_dependencies']:
                lines.append(f'  - {issue}')
        if dep_issues.get('version_conflicts'):
            lines.append('Version Conflicts:')
            for issue in dep_issues['version_conflicts']:
                lines.append(f'  - {issue}')
        if dep_issues.get('invalid_versions'):
            lines.append('Invalid Versions:')
            for issue in dep_issues['invalid_versions']:
                lines.append(f'  - {issue}')
        # Static analysis issues
        if self.static_analysis_issues:
            lines.append('Static Analysis Issues:')
            for issue in self.static_analysis_issues:
                file = issue.get('file', '<unknown>')
                lineno = issue.get('lineno')
                msg = issue.get('message', '')
                if lineno is not None:
                    lines.append(f'  - {file}:{lineno}: {msg}')
                else:
                    lines.append(f'  - {file}: {msg}')
        if not lines:
            lines.append('No issues or risks detected.')
        return '\n'.join(lines)

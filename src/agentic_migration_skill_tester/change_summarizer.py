from typing import List, Dict, Any, Set
from .migration_parser import MigrationStep

class ChangeSummary:
    """
    Holds a summary of simulated changes after migration steps are applied.
    """
    def __init__(self):
        self.added_files: Set[str] = set()
        self.modified_files: Set[str] = set()
        self.deleted_files: Set[str] = set()
        self.updated_dependencies: Dict[str, str] = {}
        self.details: List[Dict[str, Any]] = []  # Step-by-step summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            'added_files': sorted(self.added_files),
            'modified_files': sorted(self.modified_files),
            'deleted_files': sorted(self.deleted_files),
            'updated_dependencies': dict(self.updated_dependencies),
            'details': self.details
        }

class ChangeSummarizer:
    """
    Summarizes the simulated changes from a list of migration steps.
    """
    def __init__(self, steps: List[MigrationStep]):
        self.steps = steps

    def summarize(self) -> ChangeSummary:
        summary = ChangeSummary()
        file_state: Set[str] = set()  # Track simulated file presence
        for idx, step in enumerate(self.steps):
            step_info = {
                'step_number': idx + 1,
                'action': step.action,
                'target': step.target,
                'details': step.details
            }
            if step.action == 'add':
                summary.added_files.add(step.target)
                file_state.add(step.target)
                step_info['description'] = f"Added file '{step.target}'"
            elif step.action == 'modify':
                summary.modified_files.add(step.target)
                step_info['description'] = f"Modified file '{step.target}'"
            elif step.action == 'delete':
                summary.deleted_files.add(step.target)
                file_state.discard(step.target)
                step_info['description'] = f"Deleted file '{step.target}'"
            elif step.action == 'update_dependency':
                summary.updated_dependencies[step.target] = step.details or ""
                step_info['description'] = f"Updated dependency '{step.target}' to version '{step.details}'"
            else:
                step_info['description'] = f"Unknown action '{step.action}' on '{step.target}'"
            summary.details.append(step_info)
        return summary

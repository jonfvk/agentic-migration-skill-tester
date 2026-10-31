from typing import List, Dict, Set, Tuple
from .migration_parser import MigrationStep

class StepConflictError(Exception):
    pass

class StepMissingError(Exception):
    pass

class StepCheckerResult:
    def __init__(self):
        self.missing_steps: List[str] = []  # Descriptions of missing steps
        self.conflicting_steps: List[str] = []  # Descriptions of conflicts

    def has_issues(self) -> bool:
        return bool(self.missing_steps or self.conflicting_steps)

    def summary(self) -> Dict[str, List[str]]:
        return {
            'missing_steps': self.missing_steps,
            'conflicting_steps': self.conflicting_steps
        }

class StepChecker:
    """
    Checks migration steps for missing or conflicting actions.
    - Missing: e.g., modifying or deleting a file that is never added or present.
    - Conflicting: e.g., adding the same file twice, deleting a file twice, modifying after deletion, etc.
    """
    def __init__(self, initial_files: Set[str], steps: List[MigrationStep]):
        self.initial_files = set(initial_files)
        self.steps = steps

    def check(self) -> StepCheckerResult:
        result = StepCheckerResult()
        file_state = set(self.initial_files)  # Simulated file presence
        file_ops: Dict[str, List[Tuple[str, int]]] = {}  # file -> list of (action, step_idx)
        # Track for duplicate adds, deletes, modifies after delete, etc.
        for idx, step in enumerate(self.steps):
            if step.action in ('add', 'modify', 'delete'):
                file_ops.setdefault(step.target, []).append((step.action, idx))

        # Check for missing and conflicting steps
        for idx, step in enumerate(self.steps):
            if step.action == 'add':
                if step.target in file_state:
                    result.conflicting_steps.append(
                        f"Step {idx+1}: ADD '{step.target}' but file already exists."
                    )
                file_state.add(step.target)
            elif step.action == 'modify':
                if step.target not in file_state:
                    result.missing_steps.append(
                        f"Step {idx+1}: MODIFY '{step.target}' but file does not exist."
                    )
                # If file was deleted earlier in steps
                deletes = [i for a, i in file_ops.get(step.target, []) if a == 'delete' and i < idx]
                if deletes:
                    result.conflicting_steps.append(
                        f"Step {idx+1}: MODIFY '{step.target}' after it was deleted in step {max(deletes)+1}."
                    )
            elif step.action == 'delete':
                if step.target not in file_state:
                    result.missing_steps.append(
                        f"Step {idx+1}: DELETE '{step.target}' but file does not exist."
                    )
                else:
                    # Check for double delete
                    deletes = [i for a, i in file_ops.get(step.target, []) if a == 'delete']
                    if len([i for i in deletes if i < idx]) > 0:
                        result.conflicting_steps.append(
                            f"Step {idx+1}: DELETE '{step.target}' but it was already deleted earlier."
                        )
                    file_state.discard(step.target)
            # update_dependency is not checked for missing/conflicting here
        return result

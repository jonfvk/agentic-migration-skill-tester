import re
from typing import List, Dict, Any, Optional

class MigrationStep:
    """
    Represents a single migration step parsed from the instruction file.
    """
    def __init__(self, action: str, target: str, details: Optional[str] = None):
        self.action = action  # e.g., 'modify', 'add', 'delete', 'update'
        self.target = target  # e.g., file path or dependency name
        self.details = details  # e.g., code snippet, version, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            'action': self.action,
            'target': self.target,
            'details': self.details
        }

    def __repr__(self):
        return f"MigrationStep(action={self.action!r}, target={self.target!r}, details={self.details!r})"

class MigrationInstructionParseError(Exception):
    pass

class MigrationInstructionParser:
    """
    Parses and interprets migration steps from a migration instruction string.
    """
    # Example supported syntax:
    # - MODIFY <file>: <description or code>
    # - ADD <file>: <description or code>
    # - DELETE <file>
    # - UPDATE DEPENDENCY <package>: <version>
    # Steps are separated by blank lines or newlines.

    ACTION_PATTERNS = [
        (re.compile(r'^MODIFY\s+(.+?):\s*(.+)$', re.IGNORECASE), 'modify'),
        (re.compile(r'^ADD\s+(.+?):\s*(.+)$', re.IGNORECASE), 'add'),
        (re.compile(r'^DELETE\s+(.+)$', re.IGNORECASE), 'delete'),
        (re.compile(r'^UPDATE DEPENDENCY\s+(.+?):\s*(.+)$', re.IGNORECASE), 'update_dependency'),
    ]

    def __init__(self, instruction_text: str):
        self.instruction_text = instruction_text
        self.steps: List[MigrationStep] = []

    def parse(self) -> List[MigrationStep]:
        lines = [line.strip() for line in self.instruction_text.splitlines() if line.strip()]
        for line in lines:
            matched = False
            for pattern, action in self.ACTION_PATTERNS:
                m = pattern.match(line)
                if m:
                    if action in ('modify', 'add', 'update_dependency'):
                        target, details = m.group(1), m.group(2)
                        step = MigrationStep(action, target, details)
                    elif action == 'delete':
                        target = m.group(1)
                        step = MigrationStep(action, target)
                    else:
                        continue
                    self.steps.append(step)
                    matched = True
                    break
            if not matched:
                raise MigrationInstructionParseError(f"Unrecognized migration step: '{line}'")
        return self.steps

    @staticmethod
    def parse_instructions(instruction_text: str) -> List[MigrationStep]:
        parser = MigrationInstructionParser(instruction_text)
        return parser.parse()

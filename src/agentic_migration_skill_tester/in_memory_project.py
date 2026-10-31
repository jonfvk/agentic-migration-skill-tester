from typing import Dict, Optional, Any
from .migration_parser import MigrationStep

class InMemoryFile:
    """
    Represents a file in the in-memory project structure.
    """
    def __init__(self, content: str = ""):
        self.content = content

    def modify(self, new_content: str):
        self.content = new_content

class InMemoryProject:
    """
    Simulates a project structure in memory, allowing file and code changes
    to be applied according to migration steps, without affecting disk.
    """
    def __init__(self, initial_files: Optional[Dict[str, str]] = None):
        # initial_files: mapping of file path -> file content
        self.files: Dict[str, InMemoryFile] = {}
        if initial_files:
            for path, content in initial_files.items():
                self.files[path] = InMemoryFile(content)
        self.dependencies: Dict[str, str] = {}  # package -> version

    def apply_step(self, step: MigrationStep):
        if step.action == 'add':
            if step.target in self.files:
                raise ValueError(f"File already exists: {step.target}")
            self.files[step.target] = InMemoryFile(step.details or "")
        elif step.action == 'modify':
            if step.target not in self.files:
                raise ValueError(f"File does not exist: {step.target}")
            self.files[step.target].modify(step.details or "")
        elif step.action == 'delete':
            if step.target not in self.files:
                raise ValueError(f"File does not exist: {step.target}")
            del self.files[step.target]
        elif step.action == 'update_dependency':
            # step.target: package name, step.details: version
            self.dependencies[step.target] = step.details or ""
        else:
            raise ValueError(f"Unknown action: {step.action}")

    def simulate(self, steps: 'list[MigrationStep]'):
        """
        Apply a sequence of migration steps in order.
        """
        for step in steps:
            self.apply_step(step)

    def get_file_content(self, path: str) -> Optional[str]:
        file = self.files.get(path)
        return file.content if file else None

    def list_files(self) -> 'list[str]':
        return list(self.files.keys())

    def get_dependency_version(self, package: str) -> Optional[str]:
        return self.dependencies.get(package)

    def snapshot(self) -> Dict[str, Any]:
        """
        Returns a snapshot of the current in-memory project state.
        """
        return {
            'files': {path: file.content for path, file in self.files.items()},
            'dependencies': dict(self.dependencies)
        }

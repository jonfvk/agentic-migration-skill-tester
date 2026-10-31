import os
from typing import Optional

class MigrationInstructionInputError(Exception):
    pass

class MigrationInstructionInput:
    """
    Handles accepting a migration instruction file as input.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._content: Optional[str] = None

    def validate(self) -> None:
        if not isinstance(self.file_path, str):
            raise MigrationInstructionInputError("File path must be a string.")
        if not os.path.isfile(self.file_path):
            raise MigrationInstructionInputError(f"File not found: {self.file_path}")
        if not os.access(self.file_path, os.R_OK):
            raise MigrationInstructionInputError(f"File not readable: {self.file_path}")

    def read(self) -> str:
        self.validate()
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self._content = f.read()
        return self._content

    @property
    def content(self) -> Optional[str]:
        return self._content

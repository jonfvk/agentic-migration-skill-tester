from typing import Dict, List, Tuple, Optional
import re

class DependencyValidationResult:
    def __init__(self):
        self.missing_dependencies: List[str] = []  # Dependencies updated but not present
        self.version_conflicts: List[str] = []      # Version mismatches
        self.invalid_versions: List[str] = []       # Invalid version strings
        self.successful_updates: List[str] = []     # Successfully validated updates

    def has_issues(self) -> bool:
        return bool(self.missing_dependencies or self.version_conflicts or self.invalid_versions)

    def summary(self) -> Dict[str, List[str]]:
        return {
            'missing_dependencies': self.missing_dependencies,
            'version_conflicts': self.version_conflicts,
            'invalid_versions': self.invalid_versions,
            'successful_updates': self.successful_updates
        }

def parse_requirements(requirements_content: str) -> Dict[str, str]:
    """
    Parses a requirements.txt style string into a dict of package -> version.
    Only supports lines like 'package==version' or 'package>=version'.
    Ignores comments and blank lines.
    """
    dep_pattern = re.compile(r'^([A-Za-z0-9_.\-]+)\s*([=><!~]{1,2})\s*([A-Za-z0-9_.\-]+)$')
    deps = {}
    for line in requirements_content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = dep_pattern.match(line)
        if m:
            pkg, op, ver = m.groups()
            if op == '==':
                deps[pkg] = ver
            # For >=, <=, etc., store as '>=ver' (not used for strict validation)
            else:
                deps[pkg] = f"{op}{ver}"
    return deps

def is_valid_version(version: str) -> bool:
    # Accepts versions like '1.2.3', '0.9', '2.0.0rc1', etc.
    return bool(re.match(r'^[A-Za-z0-9_.\-]+$', version))

def validate_dependency_updates(
    updated_dependencies: Dict[str, str],
    requirements: Dict[str, str]
) -> DependencyValidationResult:
    """
    Checks that each dependency update is present in requirements and version is valid.
    Reports missing dependencies, version conflicts, and invalid versions.
    """
    result = DependencyValidationResult()
    for pkg, new_ver in updated_dependencies.items():
        req_ver = requirements.get(pkg)
        if req_ver is None:
            result.missing_dependencies.append(
                f"Dependency '{pkg}' updated but not found in requirements."
            )
            continue
        if not is_valid_version(new_ver):
            result.invalid_versions.append(
                f"Dependency '{pkg}' has invalid version string: '{new_ver}'"
            )
            continue
        # If requirements specify a strict version, check for mismatch
        if req_ver and not req_ver.startswith(('>=', '<=', '>', '<', '!=', '~=')):
            if req_ver != new_ver:
                result.version_conflicts.append(
                    f"Dependency '{pkg}' updated to '{new_ver}' but requirements specify '{req_ver}'."
                )
                continue
        result.successful_updates.append(
            f"Dependency '{pkg}' updated to '{new_ver}' (requirements: '{req_ver}')"
        )
    return result

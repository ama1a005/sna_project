"""Path management utilities for repository navigation and file resolution."""

from pathlib import Path


def find_project_root(anchor_file: str = "pyproject.toml") -> Path:
    """Find the project root by searching upwards for the specified anchor file."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / anchor_file).exists():
            return parent
    # Default fallback to current working directory
    return Path.cwd().resolve()


PROJECT_ROOT = find_project_root()


def resolve_path(path_str: str | Path, base_dir: Path | None = None) -> Path:
    """Resolve a relative or absolute path against a base directory (defaulting to PROJECT_ROOT)."""
    p = Path(path_str)
    if p.is_absolute():
        return p
    base = base_dir if base_dir is not None else PROJECT_ROOT
    return (base / p).resolve()


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path

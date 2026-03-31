from pathlib import Path


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".pdf"}
ANIMATION_EXTS = {".gif", ".mp4", ".webm"}


def docs_dir(repo: Path) -> Path:
    return repo / "docs"


def configs_dir(repo: Path) -> Path:
    return repo / "configs"


def artifacts_dir(repo: Path) -> Path:
    return repo / "artifacts"


def figures_dir(repo: Path) -> Path:
    return artifacts_dir(repo) / "figures"


def animations_dir(repo: Path) -> Path:
    return artifacts_dir(repo) / "animations"


def reports_dir(repo: Path) -> Path:
    return artifacts_dir(repo) / "reports"


def references_dir(repo: Path) -> Path:
    return docs_dir(repo) / "references"


def resolve_generated_output(repo: Path, name: str) -> Path:
    path = Path(name)
    if path.is_absolute() or path.parent != Path("."):
        return path
    ext = path.suffix.lower()
    if ext in ANIMATION_EXTS:
        return animations_dir(repo) / path.name
    if ext in IMAGE_EXTS:
        return figures_dir(repo) / path.name
    return repo / path.name


def find_generated_output(repo: Path, name: str) -> Path:
    preferred = resolve_generated_output(repo, name)
    if preferred.is_file():
        return preferred
    legacy = repo / name
    if legacy.is_file():
        return legacy
    return preferred


def find_script(repo: Path, name: str) -> Path:
    path = Path(name)
    if path.is_absolute() and path.is_file():
        return path
    direct = repo / path
    if direct.is_file():
        return direct
    matches = sorted(repo.glob(f"scripts/**/{path.name}"))
    if matches:
        return matches[0]
    return direct

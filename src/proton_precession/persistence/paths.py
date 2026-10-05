from pathlib import Path


def find_project_root() -> Path:
    current = Path(__file__).resolve()

    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent

    raise FileNotFoundError(
        "Could not find project root. Expected to find pyproject.toml."
    )


PROJECT_ROOT = find_project_root()

DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = DATA_DIR / "configs"
RUNS_DIR = DATA_DIR / "runs"
EXPORTS_DIR = DATA_DIR / "exports"

OUTPUT_DIR = PROJECT_ROOT / "output"
VIDEO_DIR = OUTPUT_DIR / "videos"
GIF_DIR = OUTPUT_DIR / "gifs"
IMAGE_DIR = OUTPUT_DIR / "images"


def ensure_project_directories() -> None:
    """
    Create required project directories if they do not already exist.
    """

    directories = [
        DATA_DIR,
        CONFIG_DIR,
        RUNS_DIR,
        EXPORTS_DIR,
        OUTPUT_DIR,
        VIDEO_DIR,
        GIF_DIR,
        IMAGE_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def config_path(filename: str) -> Path:
    """
    Return a path inside data/configs.
    """

    if not filename.endswith(".json"):
        filename += ".json"

    return CONFIG_DIR / filename


def run_path(filename: str) -> Path:
    """
    Return a path inside data/runs.
    """

    if not filename.endswith(".json"):
        filename += ".json"

    return RUNS_DIR / filename


def video_path(filename: str) -> Path:
    """
    Return a path inside output/videos.
    """

    if not filename.endswith(".mp4"):
        filename += ".mp4"

    return VIDEO_DIR / filename


def gif_path(filename: str) -> Path:
    """
    Return a path inside output/gifs.
    """

    if not filename.endswith(".gif"):
        filename += ".gif"

    return GIF_DIR / filename

def export_path(filename: str) -> Path:
    """
    Return a path inside data/exports.
    """

    if not filename.endswith(".csv"):
        filename += ".csv"

    return EXPORTS_DIR / filename
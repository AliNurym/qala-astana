"""Build and validate the current Qala case 1 submission archive."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "output" / "Qala_Case1_Submission_2026-10-19.zip"
FILES = (
    ".env.example",
    ".gitignore",
    "README.md",
    "SCENARIOS.md",
    "DEMO_SCRIPT.md",
    "T3_AUDIT.md",
    "start.ps1",
    "index.html",
    "app.js",
    "styles.css",
    "server.py",
    "osm_data.py",
    "presentation.html",
    "scripts/package_submission.py",
    "tests/test_recommendations.py",
    "data/places.json",
    "output/Qala_Astana_Case1_Final.pptx",
    "output/Qala_Astana_Case1_Preview.webp",
)


def build_archive() -> Path:
    missing = [relative for relative in FILES if not (ROOT / relative).is_file()]
    if missing:
        raise FileNotFoundError("Missing submission files: " + ", ".join(missing))

    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    temporary = ARCHIVE.with_name(f".{ARCHIVE.stem}.tmp")
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as archive:
            for relative in FILES:
                archive.write(ROOT / relative, arcname=relative)

        with ZipFile(temporary, "r") as archive:
            names = set(archive.namelist())
            expected = set(FILES)
            if names != expected:
                raise ValueError("Archive contents do not match the submission manifest")
            if archive.testzip() is not None:
                raise ValueError("Archive integrity check failed")
            if ".env" in names or any(name.startswith(".env/") for name in names):
                raise ValueError("Local .env must not be included in the submission")

        temporary.replace(ARCHIVE)
    finally:
        temporary.unlink(missing_ok=True)
    return ARCHIVE


if __name__ == "__main__":
    result = build_archive()
    print(f"Created and verified {result.relative_to(ROOT)} ({len(FILES)} files)")

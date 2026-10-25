"""Build and verify code.zip from the explicit submission manifest."""
from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "code" / "SUBMISSION_MANIFEST.md"


def included_paths() -> list[Path]:
    text = MANIFEST.read_text(encoding="utf-8")
    match = re.search(r"```text\s*\n(.*?)\n```", text, re.DOTALL)
    if not match:
        raise ValueError("submission manifest has no fenced inclusion list")
    names = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    if len(names) != len(set(names)):
        raise ValueError("submission manifest contains duplicate paths")
    paths = []
    for name in names:
        relative = Path(name)
        if relative.is_absolute() or relative.parts[0] != "code" or ".." in relative.parts:
            raise ValueError(f"unsafe package path in manifest: {name}")
        path = (ROOT / relative).resolve()
        if not path.is_relative_to((ROOT / "code").resolve()):
            raise ValueError(f"package path escapes the code directory: {name}")
        if not path.is_file():
            raise FileNotFoundError(f"manifest file is missing: {name}")
        paths.append(path)
    return paths


def build(output: Path, max_mb: float) -> None:
    output = output.resolve()
    paths = included_paths()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            archive.write(path, path.relative_to(ROOT).as_posix())

    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        expected = [path.relative_to(ROOT).as_posix() for path in paths]
        if names != expected:
            raise ValueError("archive contents do not match the manifest order and paths")
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError(f"archive CRC check failed for {corrupt}")
    size = output.stat().st_size
    if size > max_mb * 1024 * 1024:
        raise ValueError(f"archive is {size} bytes, above the {max_mb:g} MiB limit")
    print(f"PASS: {output} contains {len(paths)} allowlisted files; {size} bytes; CRC valid.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "code.zip")
    parser.add_argument("--max-mb", type=float, default=50.0)
    args = parser.parse_args()
    if args.max_mb <= 0:
        parser.error("--max-mb must be positive")
    build(args.output, args.max_mb)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build or verify a deterministic SHA-256 manifest for repository artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Iterable


IGNORED_DIRS = {
    ".git",
    ".github_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "reproduction_output",
    "reproduction_stress",
}
IGNORED_SUFFIXES = {".aux", ".fdb_latexmk", ".fls", ".log", ".out", ".pyc", ".synctex.gz"}


def _is_ignored(path: Path, output_relative: Path) -> bool:
    if path == output_relative:
        return True
    if any(part in IGNORED_DIRS for part in path.parts):
        return True
    return any(path.name.endswith(suffix) for suffix in IGNORED_SUFFIXES)


def _git_paths(root: Path) -> list[Path] | None:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return [Path(item.decode("utf-8")) for item in completed.stdout.split(b"\0") if item]


def _walk_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for candidate in root.rglob("*"):
        relative = candidate.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        if candidate.is_file() or candidate.is_symlink():
            paths.append(relative)
    return paths


def selected_paths(root: Path, output: Path) -> list[Path]:
    root = root.resolve()
    output_relative = output.resolve().relative_to(root)
    candidates = _git_paths(root)
    if candidates is None:
        candidates = _walk_paths(root)
    selected: list[Path] = []
    for relative in candidates:
        if _is_ignored(relative, output_relative):
            continue
        absolute = root / relative
        if absolute.is_symlink():
            raise ValueError(f"Refusing to hash symbolic link: {relative.as_posix()}")
        if absolute.is_file():
            selected.append(relative)
    return sorted(set(selected), key=lambda path: path.as_posix())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_entries(root: Path, output: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for relative in selected_paths(root, output):
        absolute = root / relative
        entries.append(
            {
                "path": relative.as_posix(),
                "sha256": _sha256(absolute),
                "bytes": absolute.stat().st_size,
            }
        )
    return entries


def _serialized(entries: Iterable[dict[str, object]]) -> str:
    return json.dumps(list(entries), indent=2, ensure_ascii=False) + "\n"


def parse_args() -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output = (args.output or (root / "SHA256_MANIFEST.json")).resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise SystemExit("Manifest output must be inside the repository root") from exc
    expected = _serialized(build_entries(root, output))
    if args.check:
        if not output.is_file():
            print(f"manifest missing: {output}")
            return 1
        if output.read_text(encoding="utf-8") != expected:
            print(f"manifest out of date: {output}")
            return 1
        print(f"manifest verified: {output}")
        return 0
    output.write_text(expected, encoding="utf-8")
    print(f"manifest written: {output} ({len(json.loads(expected))} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

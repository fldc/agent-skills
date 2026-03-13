#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_KEYS = {
    "version": str,
    "organization": str,
    "date": str,
    "abstract": str,
    "references": list,
}


def validate_skill_dir(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    metadata_path = skill_dir / "metadata.json"

    if not metadata_path.exists():
        return [f"{skill_dir.name}: missing metadata.json"]

    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{skill_dir.name}: invalid JSON in metadata.json ({exc})"]

    if not isinstance(data, dict):
        return [f"{skill_dir.name}: metadata.json must contain a JSON object"]

    for key, expected_type in REQUIRED_KEYS.items():
        if key not in data:
            errors.append(f"{skill_dir.name}: missing key '{key}'")
            continue
        if not isinstance(data[key], expected_type):
            errors.append(
                f"{skill_dir.name}: key '{key}' must be {expected_type.__name__}"
            )

    extra_keys = sorted(set(data) - set(REQUIRED_KEYS))
    if extra_keys:
        errors.append(f"{skill_dir.name}: unexpected keys {extra_keys}")

    abstract = data.get("abstract")
    if isinstance(abstract, str) and len(abstract.strip()) < 80:
        errors.append(f"{skill_dir.name}: abstract is too short")

    references = data.get("references")
    if isinstance(references, list):
        if not references:
            errors.append(f"{skill_dir.name}: references must not be empty")
        for index, reference in enumerate(references, start=1):
            if not isinstance(reference, str) or not reference.startswith("http"):
                errors.append(
                    f"{skill_dir.name}: references[{index}] must be an HTTP URL string"
                )

    return errors


def main() -> int:
    skill_dirs = sorted(
        path.parent for path in ROOT.glob("*/SKILL.md") if path.parent.is_dir()
    )

    if not skill_dirs:
        print("No skills found.", file=sys.stderr)
        return 1

    errors: list[str] = []
    for skill_dir in skill_dirs:
        errors.extend(validate_skill_dir(skill_dir))

    if errors:
        print("Skill metadata validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated metadata for {len(skill_dirs)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

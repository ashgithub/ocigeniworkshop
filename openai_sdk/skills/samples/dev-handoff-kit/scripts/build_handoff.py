"""Build a developer handoff note from structured JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = SKILL_ROOT / "examples" / "local_skills_handoff.json"
HANDOFF_TEMPLATE = SKILL_ROOT / "templates" / "handoff_note.md"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Input file is not valid JSON: {path}\n{exc}") from exc


def require_fields(data: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if not data.get(field)]
    if missing:
        raise SystemExit(f"Missing required fields: {', '.join(missing)}")


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- TBD"
    return "\n".join(f"- {item}" for item in items)


def build_handoff(data: dict[str, Any]) -> str:
    require_fields(
        data,
        ["title", "purpose", "audience", "change_summary", "files", "run_steps", "verification"],
    )

    values = {
        "title": str(data["title"]),
        "purpose": str(data["purpose"]),
        "audience": str(data["audience"]),
        "change_summary": str(data["change_summary"]),
        "files": bullet_list(list(data.get("files", []))),
        "run_steps": bullet_list(list(data.get("run_steps", []))),
        "verification": bullet_list(list(data.get("verification", []))),
        "risks": bullet_list(list(data.get("risks", []))),
        "open_questions": bullet_list(list(data.get("open_questions", []))),
        "follow_up": str(data.get("follow_up") or "TBD"),
    }

    return HANDOFF_TEMPLATE.read_text(encoding="utf-8").format(**values)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a developer handoff note.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to handoff JSON.")
    parser.add_argument("--output", type=Path, help="Optional markdown output path.")
    args = parser.parse_args()

    handoff = build_handoff(load_json(args.input))
    if args.output:
        args.output.write_text(handoff, encoding="utf-8")
        print(f"Wrote handoff note to {args.output}")
    else:
        print(handoff)


if __name__ == "__main__":
    main()

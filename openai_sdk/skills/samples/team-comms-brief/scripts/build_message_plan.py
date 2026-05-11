"""Build Slack and Outlook drafts from a structured workshop update JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = SKILL_ROOT / "examples" / "workshop_update.json"
SLACK_TEMPLATE = SKILL_ROOT / "templates" / "slack_update.md"
OUTLOOK_TEMPLATE = SKILL_ROOT / "templates" / "outlook_email.md"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Input file is not valid JSON: {path}\n{exc}") from exc


def require_fields(data: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if not str(data.get(field, "")).strip()]
    if missing:
        raise SystemExit(f"Missing required fields: {', '.join(missing)}")


def render_template(path: Path, values: dict[str, str]) -> str:
    return path.read_text(encoding="utf-8").format(**values)


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- TBD"
    return "\n".join(f"- {item}" for item in items)


def build_plan(data: dict[str, Any]) -> str:
    require_fields(
        data,
        ["title", "status", "audience", "change_summary", "impact", "ask", "owner"],
    )

    values = {
        "subject": f"Review requested: {data['title']}",
        "status": str(data["status"]),
        "context": f"This update is for {data['audience']}.",
        "change_summary": str(data["change_summary"]),
        "impact": str(data["impact"]),
        "ask": str(data["ask"]),
        "owner": str(data["owner"]),
        "try_it": str(data.get("try_it") or "TBD"),
        "next_steps": bullet_list(list(data.get("next_steps", []))),
        "feedback_path": str(data.get("feedback_path") or "TBD"),
    }

    slack = render_template(SLACK_TEMPLATE, values)
    outlook = render_template(OUTLOOK_TEMPLATE, values)
    risks = bullet_list(list(data.get("risks", [])))

    return f"""# Communication Package: {data['title']}

## Slack Announcement

{slack}

## Outlook Follow-up

{outlook}

## Owner Checklist

- Owner: {data['owner']}
- Audience: {data['audience']}
- Feedback path: {values['feedback_path']}
- Ask: {data['ask']}

## Risks Or Constraints

{risks}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Slack and Outlook communication package.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to message plan JSON.")
    parser.add_argument("--output", type=Path, help="Optional markdown output path.")
    args = parser.parse_args()

    plan = build_plan(load_json(args.input))
    if args.output:
        args.output.write_text(plan, encoding="utf-8")
        print(f"Wrote communication package to {args.output}")
    else:
        print(plan)


if __name__ == "__main__":
    main()

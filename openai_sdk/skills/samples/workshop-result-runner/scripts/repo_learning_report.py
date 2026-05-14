#!/usr/bin/env python3
"""Build a safe local learning report for the OCI AI workshop repo."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


MODULES = {
    "openai_sdk": "OpenAI-compatible SDK, Responses API, Agents SDK, skills, containers, memory, vector stores",
    "langChain": "LangChain examples for LLMs, RAG, tools, agents, MCP, and multimodal flows",
    "oci_genai": "OCI-native examples for LLMs, RAG, function calling, speech, and vision",
    "database": "Oracle Database AI examples for Select AI, NL2SQL, semantic cache, and database RAG",
}

SUGGESTED_COMMANDS = {
    "openai_sdk": "uv run openai_sdk/genai_client/structured_response.py",
    "langChain": "uv run langChain/llm/openai_oci_chat.py",
    "oci_genai": "uv run oci_genai/llm/cohere_chat.py",
    "database": "uv run database/selectai_demo.py",
}


@dataclass
class ModuleReport:
    name: str
    description: str
    readmes: list[str]
    python_count: int
    notebook_count: int
    sample_files: list[str]
    suggested_command: str | None


def find_repo_root(explicit_root: str | None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()

    candidates = [Path.cwd(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        if (candidate / "README.md").exists() and (candidate / "pyproject.toml").exists():
            return candidate.resolve()

    return Path.cwd().resolve()


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def matches_topic(path: Path, topic: str | None) -> bool:
    if not topic:
        return True
    return topic.lower() in path.as_posix().lower()


def list_files(base: Path, patterns: Iterable[str], topic: str | None) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        files.extend(path for path in base.rglob(pattern) if path.is_file() and matches_topic(path, topic))
    return sorted(set(files))


def sample_paths(paths: list[Path], root: Path, limit: int = 5) -> list[str]:
    return [relative(path, root) for path in paths[:limit]]


def build_module_report(root: Path, name: str, description: str, topic: str | None) -> ModuleReport | None:
    base = root / name
    if not base.exists():
        return None

    readmes = list_files(base, ["readme*.md", "README*.md"], topic=None)
    python_files = list_files(base, ["*.py"], topic=topic)
    notebooks = list_files(base, ["*.ipynb"], topic=topic)
    combined = sorted([*python_files, *notebooks])

    if topic and not combined and topic.lower() not in name.lower() and not any(matches_topic(path, topic) for path in readmes):
        return None

    return ModuleReport(
        name=name,
        description=description,
        readmes=sample_paths(readmes, root, limit=4),
        python_count=len(python_files),
        notebook_count=len(notebooks),
        sample_files=sample_paths(combined, root, limit=6),
        suggested_command=SUGGESTED_COMMANDS.get(name),
    )


def discover_sample_skills(root: Path) -> list[str]:
    samples = root / "openai_sdk" / "skills" / "samples"
    if not samples.exists():
        return []
    return sorted(path.name for path in samples.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def build_report(root: Path, topic: str | None) -> dict[str, object]:
    modules = [
        report
        for name, description in MODULES.items()
        if (report := build_module_report(root, name, description, topic)) is not None
    ]

    return {
        "repo": str(root),
        "topic": topic or "all",
        "root_readme": "README.md" if (root / "README.md").exists() else None,
        "environment_check": "uv run AISandboxEnvCheck.py" if (root / "AISandboxEnvCheck.py").exists() else None,
        "sample_skills": discover_sample_skills(root),
        "modules": [module.__dict__ for module in modules],
    }


def markdown_report(report: dict[str, object]) -> str:
    lines = [
        "# Workshop Learning Report",
        "",
        f"Repo: `{report['repo']}`",
        f"Topic: `{report['topic']}`",
        "",
    ]

    if report.get("environment_check"):
        lines.extend(["## First Safe Check", "", f"- `{report['environment_check']}`", ""])

    sample_skills = report.get("sample_skills") or []
    if sample_skills:
        lines.extend(["## Sample Skills", ""])
        lines.extend(f"- `{skill}`" for skill in sample_skills)
        lines.append("")

    lines.extend(["## Modules", ""])
    for module in report["modules"]:  # type: ignore[index]
        lines.extend(
            [
                f"### `{module['name']}`",
                "",
                module["description"],
                "",
                f"- Python scripts found: {module['python_count']}",
                f"- Notebooks found: {module['notebook_count']}",
            ]
        )
        if module["readmes"]:
            lines.append("- Entry docs:")
            lines.extend(f"  - `{path}`" for path in module["readmes"])
        if module["sample_files"]:
            lines.append("- Example files:")
            lines.extend(f"  - `{path}`" for path in module["sample_files"])
        if module["suggested_command"]:
            lines.append(f"- Example command after setup: `{module['suggested_command']}`")
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- The report is file-based and local-only.",
            "- Run cloud, database, or hosted skill examples only after checking `sandbox.yaml`, `.env`, and the relevant README.",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a local learning report for this workshop repo.")
    parser.add_argument("--root", help="Repository root. Defaults to auto-detection.")
    parser.add_argument("--topic", help="Optional topic filter, such as rag, agents, skills, database, or openai_sdk.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = find_repo_root(args.root)
    report = build_report(root=root, topic=args.topic)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(markdown_report(report))


if __name__ == "__main__":
    main()

from pathlib import Path

from dotenv import load_dotenv
from openai import BadRequestError, OpenAI

from openai_sdk.openai_client_provider import OpenAIClientProvider

# Learning goal:
# Try shell local-skill injection, then fallback to plain prompt injection.
#
# How to run:
# uv run python genai_client/skills_use/skill_injection.py
#
# Safe experiments for students:
# 1. Change USER_TASK to target another skill.
# 2. Add new skill folders and include them in LOCAL_SKILLS.
# 3. Print the fallback prompt to inspect what the model sees.

load_dotenv()

MODEL_ID = "openai.gpt-5.4"
BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"
USER_TASK = (
    "Use the humanizer skill. "
    "Write one AI-sounding paragraph about API testing, then humanize it."
)

LOCAL_SKILLS = [
    {
        "name": "humanizer",
        "description": "Make text sound more natural and less AI-like.",
        "path": str((SKILLS_DIR / "humanizer").resolve()),
    },
    {
        "name": "plain-writer",
        "description": "Rewrite dense text in plain language.",
        "path": str((SKILLS_DIR / "plain-writer").resolve()),
    },
    {
        "name": "release-notes",
        "description": "Create clean release notes from technical changes.",
        "path": str((SKILLS_DIR / "release-notes").resolve()),
    },
]


def build_fallback_prompt() -> str:
    prompt = "You have these local skills:\n\n"
    for skill in LOCAL_SKILLS:
        skill_file = Path(skill["path"]) / "SKILL.md"
        prompt += f"## Skill: {skill['name']}\n"
        prompt += f"Description: {skill['description']}\n"
        prompt += skill_file.read_text(encoding="utf-8")
        prompt += "\n\n"
    prompt += f"## Task\n{USER_TASK}"
    return prompt


def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Try native shell local-skills flow.
    try:
        response = client.responses.create(
            model=MODEL_ID,
            tools=[
                {
                    "type": "shell",
                    "environment": {
                        "type": "local",
                        "skills": LOCAL_SKILLS,
                    },
                }
            ],
            input=USER_TASK,
        )

    # Step 3: Fallback for endpoints without shell support.
    except BadRequestError as error:
        error_text = str(error).lower()
        if "unsupported tool type" not in error_text or "shell" not in error_text:
            raise

        fallback_prompt = build_fallback_prompt()
        response = client.responses.create(model=MODEL_ID, input=fallback_prompt)

    # Step 4: Print final output.
    print(response.output_text)


if __name__ == "__main__":
    main()

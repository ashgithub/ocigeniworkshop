import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from openai_sdk.openai_client_provider import OpenAIClientProvider

# Learning goal:
# Let the model pick one local skill via a function tool and execute it.
#
# How to run:
# uv run python genai_client/skills_use/skill_as_function.py
#
# Safe experiments for students:
# 1. Add a new local skill folder with its own SKILL.md.
# 2. Force a specific skill by rewriting USER_INPUT.
# 3. Increase loop count when testing multi-step tool usage.

load_dotenv()

MODEL_ID = "openai.gpt-5.4"
BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"
USER_INPUT = (
    "Use the best local skill for this text and return the improved final result.\n"
    "Text: 'At this point in time, this groundbreaking platform serves as a testament to innovation.'\n"
    "Task: rewrite naturally."
)
MAX_TOOL_TURNS = 6


def load_local_skills(skills_path: Path) -> dict[str, str]:
    loaded_skills: dict[str, str] = {}
    for folder in skills_path.iterdir():
        if folder.is_dir():
            loaded_skills[folder.name] = (folder / "SKILL.md").read_text(encoding="utf-8")
    return loaded_skills


def main() -> None:
    # Step 1: Build configured client and load local skills.
    client: OpenAI = OpenAIClientProvider().oci_openai_client
    skills = load_local_skills(SKILLS_DIR)

    # Step 2: Define one function tool that routes by skill name.
    tool = {
        "type": "function",
        "name": "use_local_skill",
        "description": (
            "Apply one local skill to text. "
            f"Available skills: {', '.join(sorted(skills.keys()))}"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "skill": {
                    "type": "string",
                    "description": f"Skill name. Use one of: {', '.join(sorted(skills.keys()))}",
                },
                "text": {"type": "string", "description": "Input text to transform."},
                "task": {
                    "type": "string",
                    "description": "Specific instruction for the selected skill. Use empty string if not needed.",
                },
            },
            "required": ["skill", "text", "task"],
            "additionalProperties": False,
        },
        "strict": True,
    }

    # Step 3: Start response loop.
    response = client.responses.create(model=MODEL_ID, tools=[tool], input=USER_INPUT)

    for _ in range(MAX_TOOL_TURNS):
        function_outputs = []

        for output_item in response.output:
            if output_item.type != "function_call":
                continue

            try:
                arguments = json.loads(output_item.arguments) if output_item.arguments else {}
            except json.JSONDecodeError:
                arguments = {}

            skill_name = str(arguments.get("skill", ""))
            source_text = str(arguments.get("text", ""))
            task_text = str(arguments.get("task", "")).strip()

            if skill_name not in skills:
                result_text = (
                    f"Unknown skill: {skill_name}. Available skills: {', '.join(sorted(skills.keys()))}"
                )
            elif not source_text:
                result_text = "Missing required field: text"
            else:
                instructions = (
                    "You are applying a local skill. Follow this SKILL.md exactly.\n\n"
                    f"{skills[skill_name]}\n\n"
                    "Return only the final transformed result."
                )
                skill_input = f"Task: {task_text}\n\nInput:\n{source_text}" if task_text else source_text
                skill_response = client.responses.create(
                    model=MODEL_ID,
                    instructions=instructions,
                    input=skill_input,
                )
                result_text = skill_response.output_text

            function_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": output_item.call_id,
                    "output": result_text,
                }
            )

        if not function_outputs:
            break

        response = client.responses.create(
            model=MODEL_ID,
            previous_response_id=response.id,
            input=function_outputs,
        )

    # Step 4: Print final transformed text.
    print(response.output_text)


if __name__ == "__main__":
    main()

import os
import sys
from dotenv import load_dotenv
from envyaml import EnvYAML

# Import helper from parent folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper  

#demo of reasoning with chatgpt-5 using OCI OpenAI-compatible API
load_dotenv()
config = EnvYAML("sandbox.yaml")

LLM_MODEL = "openai.gpt-5"

# Reasoning-focused prompt
messages = [
    (
        "system",
        "You are an expert reasoning assistant. Explain your steps clearly, then provide a brief summary."
    ),
    (
        "human",
        "If there are 21 apples and they are split equally among 3 friends, how many apples does each friend receive?"
    ),
]

# Build client; enable responses API and request a reasoning summary
llm = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=config,
    use_responses_api=True,
    reasoning={"effort": "low", "summary": "auto"},
)

# Invoke and print: answer, reasoning summary, and token counts
res = llm.invoke(messages)

# Answer
print("\n=== Answer ===")
print(getattr(res, "content", res))

# Reasoning summary (if available)
ak = getattr(res, "additional_kwargs", {}) or {}
summary = ak.get("reasoning_summary") or ak.get("summary") or (ak.get("reasoning") or {}).get("summary")
print("\n=== Reasoning Summary ===")
print(summary if summary else "N/A")

# Token counts (if available)
usage = getattr(res,"usage_metadata") or {}
input_tokens = usage.get("input_tokens") or usage.get("input_tokens")
output_tokens = usage.get("output_tokens") or usage.get("output_tokens")
reasoning = usage.get("output_token_details").get("reasoning")
print("\n=== Token Usage ===")
print(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}, reasoning: {reasoning}")


""" What this file does:
Demonstrates image generation through the `image_generation` tool and
saves the first generated image to local disk.

Documentation for reference:
- Image generation guide: https://platform.openai.com/docs/guides/image-generation
- Image and vision: https://developers.openai.com/api/docs/guides/images-vision
- Tools guide: https://platform.openai.com/docs/guides/tools
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution
- #genai-hosted-deployment-users: GA deployment and integration updates

Environment setup:
- Set up the credentials for OCI over the `sandbox.yaml file`
- Make sure to set up a project ID from the console, consult the GenAI platform GA docs for guidance
- Set up the right compartment ID and profile name over the config file

How to run the file:
uv run openai_sdk/genai_client/image_generator.py

Safe experiments:
1. Change `IMAGE_PROMPT` style, subject, and detail level.
3. Try another model and compare visual quality.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Request image generation tool output.
3. Step 3: Decode and persist image bytes. """

import base64
from pathlib import Path

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
IMAGE_PROMPT = "Generate an image of a golden playing with a cat"
OUTPUT_IMAGE_PATH = Path("openai_sdk/output/generated_image.png")

def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Request one generated image.
    response = client.responses.create(
        model=MODEL_ID,
        input=IMAGE_PROMPT,
        tools=[{"type": "image_generation"}],
        store=False,
        stream=False,
    )

    # Step 3: Extract image bytes from tool output.
    generated_images = [
        output_item.result
        for output_item in response.output
        if output_item.type == "image_generation_call"
    ]

    if not generated_images:
        print("No image data returned by the model.")
        return

    # Step 4: Persist generated image to disk.
    print(f"Saving generated image to '{OUTPUT_IMAGE_PATH}'...")
    OUTPUT_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMAGE_PATH.write_bytes(base64.b64decode(generated_images[0]))
    print(f"Saved generated image to {OUTPUT_IMAGE_PATH}")

if __name__ == "__main__":
    main()

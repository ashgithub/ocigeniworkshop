""" What this file does:
Demonstrates image generation through the `image_generation` tool and
saves the first generated image to local disk.

Documentation for reference:
- Image generation guide: https://platform.openai.com/docs/guides/image-generation
- Tools guide: https://platform.openai.com/docs/guides/tools
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users
- #igiu-innovation-lab
- #igiu-ai-learning
- #genai-hosted-deployment-users

Environment setup:
- Create `.env` from `.env.example`
- Ensure endpoint/project/profile values are set for OCI

How to run the file:
uv run python genai_client/image_generator.py

Safe experiments:
1. Change `IMAGE_PROMPT` style, subject, and detail level.
2. Save output to another file path.
3. Try another model and compare visual quality.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Request image generation tool output.
3. Step 3: Decode and persist image bytes. """

import base64
from pathlib import Path

from openai import OpenAI
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
IMAGE_PROMPT = "Generate an image of a dog race golden playing with a samoyen"
OUTPUT_IMAGE_PATH = Path("public/otter.png")


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
    OUTPUT_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMAGE_PATH.write_bytes(base64.b64decode(generated_images[0]))
    print(f"Saved generated image to {OUTPUT_IMAGE_PATH}")


if __name__ == "__main__":
    main()


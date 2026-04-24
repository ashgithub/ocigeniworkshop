""" What this file does:
Demonstrates multimodal requests in Responses API:
1) image + text input and 2) uploaded file + text input.

Documentation for reference:
- Images and vision: https://platform.openai.com/docs/guides/images-vision
- File inputs: https://platform.openai.com/docs/guides/pdf-files
- Responses API: https://platform.openai.com/docs/api-reference/responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users
- #igiu-innovation-lab
- #igiu-ai-learning
- #genai-hosted-deployment-users

Environment setup:
- Create `.env` from `.env.example`
- Ensure endpoint/project/profile values are set for OCI
- Confirm `IMAGE_PATH` and `FILE_PATH` exist before running

How to run the file:
uv run python genai_client/multimodal.py

Safe experiments:
1. Change `IMAGE_PATH` and ask targeted visual questions.
2. Swap `FILE_PATH` to another PDF and compare summaries.
3. Try `detail` low/high to compare vision behavior.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Encode image and submit image+text input.
3. Step 3: Upload file and submit file+text input. """

import base64
from pathlib import Path

from openai import OpenAI
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
IMAGE_PATH = Path("public/test_image.png")
FILE_PATH = Path("public/fema_outage_flyer.pdf")
IMAGE_PROMPT = "What's in this image?"
FILE_PROMPT = "What's discussed in the file?"

def encode_image(image_path: Path) -> str:
    # Helper: Convert local image bytes to base64 data URI content.
    with image_path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Send image + text input.
    base64_image = encode_image(IMAGE_PATH)
    image_response = client.responses.create(
        model=MODEL_ID,
        store=False,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": IMAGE_PROMPT},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{base64_image}",
                        "detail": "high",
                    },
                ],
            }
        ],
    )
    print(image_response.output_text)

    # Step 3: Upload PDF and send file + text input.
    uploaded_file = client.files.create(file=FILE_PATH.open("rb"), purpose="user_data")
    file_response = client.responses.create(
        model=MODEL_ID,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "file_id": uploaded_file.id},
                    {"type": "input_text", "text": FILE_PROMPT},
                ],
            }
        ],
    )
    print(file_response.output_text)


if __name__ == "__main__":
    main()

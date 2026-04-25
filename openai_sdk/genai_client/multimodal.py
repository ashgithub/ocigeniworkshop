""" What this file does:
Demonstrates multimodal requests in Responses API:
1) image + text input and 2) uploaded file + text input.

Documentation for reference:
- Images and vision: https://platform.openai.com/docs/guides/images-vision
- File inputs: https://platform.openai.com/docs/guides/pdf-files
- Responses API: https://developers.openai.com/api/docs/guides/migrate-to-responses
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
uv run python -m openai_sdk.genai_client.multimodal

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

MODEL_ID = "openai.gpt-5.4"
IMAGE_PATH = Path("openai_sdk/output/test_image.png")
FILE_PATH = Path("openai_sdk/output/fema_outage_flyer.pdf")
IMAGE_PROMPT = "What's in this image?"
FILE_PROMPT = "What's discussed in the file?"

def encode_image(image_path: Path) -> str:
    # Helper: Convert local image bytes to base64 data URI content.
    with image_path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def encode_file_data_uri(file_path: Path, mime_type: str) -> str:
    # Helper: Convert local file bytes to base64 data URI for input_file.
    with file_path.open("rb") as file:
        encoded = base64.b64encode(file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"

def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Send image + text input.
    print(f"Running image + text request using image at '{IMAGE_PATH}'...")
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
    print("Image + text response:")
    print(image_response.output_text)

    # Step 3: Send PDF as inline file_data + text input.
    # OCI OpenAI-compatible deployments may not expose /files upload endpoint.
    print(f"Sending inline file data for '{FILE_PATH}' with file + text request...")
    pdf_data_uri = encode_file_data_uri(FILE_PATH, "application/pdf")
    file_response = client.responses.create(
        model=MODEL_ID,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "filename": FILE_PATH.name, "file_data": pdf_data_uri},
                    {"type": "input_text", "text": FILE_PROMPT},
                ],
            }
        ],
    )
    print("File + text response:")
    print(file_response.output_text)

if __name__ == "__main__":
    main()

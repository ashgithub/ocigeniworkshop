"""What this file does:
Demonstrates core file management for vector workflows:
1) Upload a file with `purpose=user_data` (optional)
2) List files
3) Retrieve metadata and content for one file
4) Optionally delete that file

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Files API reference: https://platform.openai.com/docs/api-reference/files
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Set `UPLOAD_FILE_PATH` or env var `VECTOR_SAMPLE_FILE_PATH` to test upload.
- Set `TARGET_FILE_ID` or env var `VECTOR_SAMPLE_FILE_ID` when skipping upload.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/file_management.py

Safe experiments:
1. Start with a small text or CSV file for easier inspection.
2. Keep `DELETE_FILE_AT_END=False` while validating list/retrieve output.
3. Toggle upload on/off to practice both onboarding paths.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Resolve optional runtime inputs.
3. Step 3-6: Run upload/list/retrieve/delete flow.
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

UPLOAD_FILE_PATH = "./openai_sdk/output/fema_outage_flyer.pdf"  # Set local file path here
DELETE_FILE_AT_END = True  # Set False for persistent session files

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve optional file input values.
    file_path = UPLOAD_FILE_PATH
    file_id = None

    # Step 3: Upload (optional).
    if file_path:
        with open(file_path, "rb") as file_handle:
            uploaded_file = client.files.create(file=file_handle, purpose="user_data")
        print(f"uploaded file: {uploaded_file}")
        file_id = uploaded_file.id
    else:
        print(
            "Skipping upload. Set UPLOAD_FILE_PATH constant or create env var VECTOR_SAMPLE_FILE_PATH."
        )

    # Step 4: List files.
    files_list = client.files.list(order="asc", limit=20)
    print("Files listed:\n")
    for file in files_list.data:
        print(f"ID: {file.id}\nName: {file.filename}\nStatus: {file.status}\nPurpose: {file.purpose}\n")

    if not file_id:
        try:
            file_id = files_list.data[0].id
        except Exception:
            print("No files on client list, Upload a file on the previous step")
            return

    # Step 5: Retrieve info/content for one file.
    file_info = client.files.retrieve(file_id=file_id)
    print(f"File metadata found:\n{file_info}")

    # TODO: fix the ath error: openai.BadRequestError: Error code: 400 - {'error': {'code': 'bad_request', 'message': 'Not allowed to download files of purpose: user_data', 'param': None, 'type': 'invalid_request_error', 'valid': True}}
    # content_page = client.files.content(file_id=file_id)
    # print(f"Content page:\n{content_page}")

    print("Calling model to read the latest file uploaded\n")
    response = client.responses.create(
        model="openai.gpt-5.2",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": file.id,
                    },
                    {
                        "type": "input_text",
                        "text": "What's discussed in the file?",
                    },
                ]
            }
        ]
    )
    print(f"Model response:\n{response.output_text}")

    # Step 6: Delete (optional).
    if DELETE_FILE_AT_END:
        delete_result = client.files.delete(file_id=file_id)
        print(f"Delete job result:\n{delete_result}")
    else:
        print("Skipping delete. Set DELETE_FILE_AT_END=True to delete the file.")

if __name__ == "__main__":
    main()

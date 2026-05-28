""" What this file does:
Demonstrates the Files API steps that prepare documents for vector workflows:
1) Choose a local sample file.
2) Upload the file with `purpose=user_data`.
3) List files available to the configured project.
4) Retrieve metadata for one file.
5) Ask a model to read an uploaded file directly.
6) Optionally delete the uploaded file object.

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Files API reference: https://platform.openai.com/docs/api-reference/files
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution for this repo
- #genai-hosted-deployment-users: GA deployment and integration updates with latest SDK

Environment setup:
- Configure OCI credentials, project, compartment, and profile in `sandbox.yaml`.
- Set `UPLOAD_FILE_PATH` to a readable local file before running the upload flow.
- Set `DELETE_FILE_AT_END=False` while learning if you want to inspect the uploaded file later.

How to run the file:
uv run openai_sdk/genai_client/vector_store/file_management.py

Safe experiments:
1. Start with a small text or CSV file for easier inspection.
2. Keep `DELETE_FILE_AT_END=False` while validating list/retrieve output.
3. Toggle upload on/off to practice both onboarding paths.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Resolve file input values.
3. Step 3: Upload a file to the Files API.
4. Step 4: List project files and pick a file id.
5. Step 5: Retrieve metadata and call the model with the file.
6. Step 6: Optional file cleanup.
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

UPLOAD_FILE_PATH = "./openai_sdk/output/fema_outage_flyer.pdf"  # Set local file path here

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    print("Step 1 - Building OCI OpenAI client.")
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve file input values. Beginners can start by changing only
    # UPLOAD_FILE_PATH and DELETE_FILE_AT_END at the top of this file.
    print("Step 2 - Resolving file input values.")
    file_path = UPLOAD_FILE_PATH
    file_id = None

    # Step 3: Upload the local file. The returned id is what later APIs use.
    if file_path:
        print(f"Step 3 - Uploading local file: {file_path}")
        with open(file_path, "rb") as file_handle:
            uploaded_file = client.files.create(file=file_handle, purpose="user_data")
        print(f"uploaded file: {uploaded_file}")
        file_id = uploaded_file.id
    else:
        print(
            "Skipping upload. Set UPLOAD_FILE_PATH constant to upload a local file."
        )

    # Step 4: List Files API objects so you can confirm what the project can see.
    print("Step 4 - Listing files available to this project.")
    files_list = client.files.list(order="asc", limit=20)
    print("Files listed:\n")
    for file in files_list.data:
        print(f"ID: {file.id}\nName: {file.filename}\nStatus: {file.status}\nPurpose: {file.purpose}\n")

    if not file_id:
        print("No uploaded file id found. Falling back to the first file returned by the list call.")
        try:
            file_id = files_list.data[0].id
        except Exception:
            print("No files on client list, Upload a file on the previous step")
            return

    # Step 5: Retrieve metadata for one file. Metadata confirms the file exists,
    # its purpose, and server-side processing status.
    print(f"Step 5 - Retrieving metadata for file id: {file_id}")
    file_info = client.files.retrieve(file_id=file_id)
    print(f"File metadata found:\n{file_info}")

    # TODO: Revisit direct content download when the service allows downloads
    # for files with purpose `user_data`. The file can still be used by model
    # calls even when raw content download is blocked.
    # content_page = client.files.content(file_id=file_id)
    # print(f"Content page:\n{content_page}")

    # Step 5b: Send the file as model input to show how uploaded content can
    # participate in a normal Responses API request.
    print("Step 5b - Calling model to read the latest file uploaded.\n")
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

    # Step 6: Delete the uploaded file when the sample is configured to clean up.
    print(f"Step 6 - Deleting file id: {file_id}")
    delete_result = client.files.delete(file_id=file_id)
    print(f"Delete job result:\n{delete_result}")

if __name__ == "__main__":
    main()

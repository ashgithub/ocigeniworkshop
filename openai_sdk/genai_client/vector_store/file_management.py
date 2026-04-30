"""File management sample for vector store workflows.

What this file does:
1) Uploads a file with `purpose=user_data`
2) Lists files
3) Optionally retrieves file metadata/content and deletes a file

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/file_management.py

Optional environment variables:
- VECTOR_SAMPLE_FILE_PATH: local file to upload
- VECTOR_SAMPLE_FILE_ID: existing file id for retrieve/content/delete operations
- VECTOR_DELETE_FILE: set to true to delete `VECTOR_SAMPLE_FILE_ID`
"""

from __future__ import annotations

try:
    from .vector_genai_client import as_bool, get_client, get_env, print_section
except ImportError:
    from vector_genai_client import as_bool, get_client, get_env, print_section


def main() -> None:
    client = get_client()

    file_path = get_env("VECTOR_SAMPLE_FILE_PATH")
    file_id = get_env("VECTOR_SAMPLE_FILE_ID")

    if file_path:
        print_section("Upload File")
        with open(file_path, "rb") as file_handle:
            uploaded_file = client.files.create(file=file_handle, purpose="user_data")
        print(uploaded_file)
        file_id = uploaded_file.id
    else:
        print("Skipping upload: set VECTOR_SAMPLE_FILE_PATH to upload a file.")

    print_section("List Files")
    files_list = client.files.list(order="asc", limit=20)
    print(files_list)

    if not file_id:
        print(
            "Skipping retrieve/content/delete: set VECTOR_SAMPLE_FILE_ID "
            "or upload a file in this run."
        )
        return

    print_section("Retrieve File Metadata")
    file_info = client.files.retrieve(file_id=file_id)
    print(file_info)

    print_section("Retrieve File Content")
    content_page = client.files.content(file_id=file_id)
    print(content_page)

    if as_bool("VECTOR_DELETE_FILE", default=False):
        print_section("Delete File")
        delete_result = client.files.delete(file_id=file_id)
        print(delete_result)
    else:
        print("Skipping delete: set VECTOR_DELETE_FILE=true to delete the file.")


if __name__ == "__main__":
    main()

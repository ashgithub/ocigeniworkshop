#!/bin/bash

# URL Validation Script
# This checks all EXTERNAL (non-Oracle) URLs referenced in project .md files.
# Run as: bash validate_urls.sh > url_status_report.txt

set -e

function check_url() {
    url="$1"
    echo -n "$url "
    curl -Ls -o /dev/null -w "%{http_code}\n" "$url"
}

# ----- External URLs by file (de-duplicated, only non-Oracle domains) -----

# rag/readme_rag.md
check_url "https://docs.cohere.com"
check_url "https://docs.cohere.com/v2/docs/rag-citations#citation-modes"
check_url "https://docs.cohere.com/docs/rerank"
check_url "https://docs.langchain.com/oss/python/langchain/splitting"

# function_calling/readme_function.md
check_url "https://docs.cohere.com/docs/command-r"
check_url "https://www.llama.com/"

# langChain/vision/langchain_oci_readme_vision.md
check_url "https://github.com/oracle-samples/oci-openai"
check_url "https://github.com/oracle-devrel/langchain-oci-genai"
check_url "https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models"

# vision/readme_vision.md
check_url "https://github.com/oracle/oci-python-sdk"
check_url "https://www.postman.com/oracledevs/oracle-cloud-infrastructure-rest-apis/collection/061avdq/vision-api"
check_url "https://www.postman.com/oracledevs/oracle-cloud-infrastructure-rest-apis/collection/28z4h20/document-understanding-api"

# langChain/llm/readme_langchain_llm.md
check_url "https://platform.openai.com/docs/api-reference"
check_url "https://platform.openai.com/docs/guides/reasoning"
check_url "https://jupyter.org/"
check_url "https://json-schema.org/"
check_url "https://docs.pydantic.dev/latest/concepts/validators/"
check_url "https://docs.pydantic.dev/latest/concepts/models/"
check_url "https://python.langchain.com/docs/how_to/structured_output/"
check_url "https://python.langchain.com/docs/integrations/providers/oci/"
check_url "https://en.wikipedia.org/wiki/Problem_solving"
check_url "https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events"
check_url "https://kafka.apache.org/"
check_url "https://docs.celeryproject.org/"

# database/readme_database.md
check_url "https://python-oracledb.readthedocs.io/"

# speech/readme_speech.md
check_url "https://docs.cohere.com/docs/chat-api"
check_url "https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events"

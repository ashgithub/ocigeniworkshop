"""
What this file does:
Analyzes documents using OCI Document Understanding for OCR capability: classification of documents, and extraction of text, tables, and key/value pairs.

Documentation to reference:
- OCI Document Understanding: https://docs.oracle.com/en-us/iaas/Content/document-understanding/using/home.htm
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/ai_document
- Postman collection: https://www.postman.com/oracledevs/oracle-cloud-infrastructure-rest-apis/collection/28z4h20/document-understanding-api

Relevant slack channels:
- #oci_ai_document_service_users: for OCI Document Understanding API questions
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and bucket details.
- .env: Load environment variables if needed.

How to run the file:
uv run vision/oci_document_understanding.py [--file path/to/document]

Comments to important sections of file:
- Step 1: Load and validate configuration.
- Step 2: Extract configuration values.
- Step 3: Upload file to Object Storage.
- Step 4: Create Document Understanding client.
- Step 5: Define analysis features.
- Step 6: Set up input and output locations.
- Step 7: Create processor job details.
- Step 8: Submit job and wait for completion.
- Step 9: Retrieve and parse results.
- Step 10: Parse and display key results.
"""

from dotenv import load_dotenv
from envyaml import EnvYAML
import argparse
from pathlib import Path
from oci.object_storage import ObjectStorageClient
import oci
import os
import json





#####
# Make sure your sandbox.yaml and .env files are set up for your environment.
# You might have to specify the full path depending on your current working directory (cwd).
# .env should define vars like MY_PREFIX, DB_PASSWORD (even if defaults in yaml).
#####

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()
DEFAULT_DOCUMENT_PATH = Path("./vision/receipt.png")

def load_config(config_path):
    """Load configuration from a YAML file with environment variable substitution."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def upload(oci_cfg, bucket_cfg, file_path):
    """Upload the file to OCI Object Storage using the bucket config."""
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found.")
        return False
    
    object_storage_client = ObjectStorageClient(oci_cfg)
    print(f"Uploading file {file_path} ...")
    object_storage_client.put_object(
        bucket_cfg["namespace"], 
        bucket_cfg["bucketName"], 
        f"{bucket_cfg['prefix']}/{file_path.name}", 
        open(file_path, 'rb')
    )
    print("Upload completed!")
    return True

def get_input_location(bucket_cfg, file_path):
    object_location = oci.ai_document.models.ObjectLocation()
    object_location.namespace_name = bucket_cfg["namespace"]
    object_location.bucket_name = bucket_cfg["bucketName"]
    object_location.object_name = f"{bucket_cfg['prefix']}/{file_path.name}"

    return object_location

def get_output_location(bucket_cfg): 
    object_location = oci.ai_document.models.OutputLocation()
    object_location.namespace_name = bucket_cfg["namespace"] 
    object_location.bucket_name = bucket_cfg["bucketName"]  
    object_location.prefix = f"{bucket_cfg['prefix']}"

    return object_location

# Create a processor_job for text_extraction feature
def create_processor(features, prefix, compartmentid, bucket_cfg, file_path):
    display_name = f"{prefix}-test"
    job_details = oci.ai_document.models.CreateProcessorJobDetails(
                                                    display_name=display_name,
                                                    compartment_id=compartmentid,
                                                    input_location=oci.ai_document.models.ObjectStorageLocations(object_locations=[get_input_location(bucket_cfg, file_path)]),
                                                    output_location= get_output_location(bucket_cfg),
                                                    processor_config=oci.ai_document.models.GeneralProcessorConfig(features=features))
    return job_details
    
def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)


def parse_response(json_data):
    """Parse and print key extracted information from Document Understanding response."""
    # Print detected type and language (top-level)
    doc_type = json_data.get('detectedDocumentTypes', [{}])[0].get('documentType', 'N/A')
    lang = json_data.get('detectedLanguages', [{}])[0].get('language', 'N/A')
    print(f"Detected Document Type: {doc_type}")
    print(f"Detected Language: {lang}")

    # Traverse all pages and extract documentFields
    pages = json_data.get('pages', [])
    if not pages:
        print("No pages found in response.")
        return

    for page_idx, page in enumerate(pages, start=1):
        print(f"\n--- Page {page_idx} ---")
        fields = page.get('documentFields', [])
        if not fields:
            print("No document fields extracted on this page.")
            continue

        for field in fields:
            if field['fieldType'] == 'KEY_VALUE':
                label = field['fieldLabel']['name']
                value = field['fieldValue']
                if value['valueType'] == 'STRING':
                    print(f"{label}: {value['text']}")
                elif value['valueType'] == 'NUMBER':
                    print(f"{label}: {value['value']}")
                elif value['valueType'] == 'DATE':
                    print(f"{label}: {value['text']} ({value['value']})")
            elif field['fieldType'] == 'LINE_ITEM_GROUP':
                print(f"{field['fieldLabel']['name']}:")
                items = value.get('items', [])
                for item in items:
                    name = next((f['fieldValue']['text'] for f in item['fieldValue']['items'] if f['fieldLabel']['name'] == 'Name'), 'N/A')
                    quantity = next((f['fieldValue']['value'] for f in item['fieldValue']['items'] if f['fieldLabel']['name'] == 'Quantity'), 'N/A')
                    unit_price = next((f['fieldValue']['value'] for f in item['fieldValue']['items'] if f['fieldLabel']['name'] == 'UnitPrice'), 'N/A')
                    amount = next((f['fieldValue']['value'] for f in item['fieldValue']['items'] if f['fieldLabel']['name'] == 'Amount'), 'N/A')
                    print(f"  - {name}: Qty {quantity} @ ${unit_price} = ${amount}")
            else:
                print(f"Unsupported field type: {field['fieldType']}")
    
    
def main(file_path=DEFAULT_DOCUMENT_PATH):
    """Main function to run OCI Document Understanding on the given file."""
    # Load config
    scfg = load_config(SANDBOX_CONFIG_FILE)

    # Step 1: Load and validate configuration
    if scfg is None or 'oci' not in scfg or 'bucket' not in scfg:
        print("Error: Invalid configuration.")
        return
    
    # Validate required sections
    if 'configFile' not in scfg['oci'] or 'profile' not in scfg['oci'] or 'compartment' not in scfg['oci']:
        print("Error: Missing required OCI configuration.")
        return

    if 'namespace' not in scfg['bucket'] or 'bucketName' not in scfg['bucket']:
        print("Error: Missing required bucket configuration.")
        return

    # Validate required sections
    if 'oci' not in scfg or 'bucket' not in scfg:
        print("Error: Missing 'oci' or 'bucket' section in config.")
        return

    # Step 2: Extract configuration values

    oci_cfg = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]), scfg["oci"]["profile"])
    bucket_cfg = scfg["bucket"]
    namespace = bucket_cfg["namespace"]
    bucket_name = bucket_cfg["bucketName"]
    prefix = bucket_cfg['prefix']
    compartment_id = scfg["oci"]["compartment"]

    # Step 3: Upload file to Object Storage
    if not upload(oci_cfg, bucket_cfg, file_path):
        return

    # Step 4: Create Document Understanding client
    dus_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(
        oci.ai_document.AIServiceDocumentClient(config=oci_cfg)
    )

    # Step 5: Define analysis features
    features = [
        oci.ai_document.models.DocumentClassificationFeature(),
        oci.ai_document.models.DocumentLanguageClassificationFeature(),
        oci.ai_document.models.DocumentKeyValueExtractionFeature(),
        oci.ai_document.models.DocumentTableExtractionFeature(),
        oci.ai_document.models.DocumentTextExtractionFeature()
    ]

    processor_job = None
    try:
        # Step 6: Set up input and output locations
        # Step 7: Create processor job details
        # Step 8: Submit job and wait for completion
        processor = dus_client.create_processor_job_and_wait_for_state(
            create_processor_job_details=create_processor(features, prefix, compartment_id, bucket_cfg, file_path),
            wait_for_states=[oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_SUCCEEDED],
            waiter_kwargs={"wait_callback": create_processor_job_callback}
        )

        if processor and processor is not oci.util.Sentinel:
            data = getattr(processor, 'data', None)
            request_id = getattr(processor, 'request_id', None)
            if (data is not None and data is not oci.util.Sentinel and
                hasattr(data, 'lifecycle_state') and
                data.lifecycle_state == oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_SUCCEEDED):
                processor_job = data
                print(f"Processor job succeeded with lifecycle state: {processor_job.lifecycle_state} and request ID: {request_id}.")
            else:
                print("Processor job did not succeed.")
        else:
            print("Processor job creation failed or timed out.")
    except Exception as e:
        print(f"Error creating/running processor job: {e}")

    if processor_job is None:
        return

    # Step 9: Retrieve and parse results
    print(f"Getting results JSON from output location {processor_job.id}")
    object_storage_client = oci.object_storage.ObjectStorageClient(config=oci_cfg)
    if processor_job is not None and hasattr(processor_job, 'id'):
        response = object_storage_client.get_object(
            namespace_name=namespace,
            bucket_name=bucket_name,
            object_name=f"{prefix}/{processor_job.id}/{namespace}_{bucket_name}/results/{prefix}/{file_path.name}.json"
        )

        if response is not None and hasattr(response, 'status') and response.status == 200:
            if hasattr(response, 'data') and hasattr(response.data, 'content'):
                json_data = json.loads(response.data.content.decode('utf-8'))

                # Step 10: Parse and display key results
                parse_response(json_data)
            else:
                print("Error: Invalid response data.")
        else:
            print(f"Failed to get results: HTTP {getattr(response, 'status', 'Unknown')}")
    else:
        print("Error: Invalid processor job.")

# Experimentation: Try with different document types like PDFs, or modify features to focus on specific analysis.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OCI Document Understanding on an image or PDF.")
    parser.add_argument("--file", type=Path, default=DEFAULT_DOCUMENT_PATH, help="Path to the file to analyze (default: ./vision/receipt.png)")
    args = parser.parse_args()
    main(args.file)

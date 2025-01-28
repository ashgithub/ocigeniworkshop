#doc https://docs.oracle.com/en-us/iaas/Content/document-understanding/using/home.htm
#slack: #oci_ai_document_service_users or or #igiu-innovation-lab 
# if you have errors running sample code reach out for help in #igiu-ai-learnin

import oci
import io
import uuid
from oci.object_storage import ObjectStorageClient
import json,os,io 

#####
#Setup
#Change the compartmentid to yhe ocid of your compartment
#Change the profile if needed
#####

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####

SANDBOX_CONFIG_FILE = "sandbox.json"
FILE_TO_ANALYZE ="./vision/reciept.png"

def load_config(config_path):
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
                return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file '{config_path}': {e}")
        return None


def upload(oci_cfg, bucket_cfg):
    object_storage_client = ObjectStorageClient(oci_cfg)
    print(f"Uploading file {FILE_TO_ANALYZE} ...")
    object_storage_client.put_object(bucket_cfg["namespace"], 
                                     bucket_cfg["bucketName"], 
                                     f"{bucket_cfg['prefix']}/{os.path.basename(FILE_TO_ANALYZE)}", 
                                     io.open(FILE_TO_ANALYZE,'rb'))
    print("Upload completed !")


# Setup input location where document being processed is stored.
def get_input_location(bucket_cfg): 
    object_location = oci.ai_document.models.ObjectLocation()
    object_location.namespace_name = bucket_cfg["namespace"] 
    object_location.bucket_name = bucket_cfg["bucketName"]  
    object_location.object_name = f"{bucket_cfg['prefix']}/{os.path.basename(FILE_TO_ANALYZE)}"

    return object_location

def get_output_location(bucket_cfg): 
    object_location = oci.ai_document.models.OutputLocation()
    object_location.namespace_name = bucket_cfg["namespace"] 
    object_location.bucket_name = bucket_cfg["bucketName"]  
    object_location.prefix = f"{bucket_cfg['prefix']}"

    return object_location

# Create a processor_job for text_extraction feature
def create_processor(features, prefix, compartmentid, bucket_cfg):
    display_name = f"{prefix}-test"
    job_details = oci.ai_document.models.CreateProcessorJobDetails(
                                                    display_name=display_name,
                                                    compartment_id=compartmentid,
                                                    input_location=oci.ai_document.models.ObjectStorageLocations(object_locations=[get_input_location(bucket_cfg)]),
                                                    output_location= get_output_location(bucket_cfg),
                                                    processor_config=oci.ai_document.models.GeneralProcessorConfig(features=features))
    return job_details 
    
def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)
    
    
#read the config files 
scfg = load_config(SANDBOX_CONFIG_FILE)
oci_cfg = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])
bucket_cfg = scfg["bucket"]
namespace = bucket_cfg["namespace"]
bucketName =  bucket_cfg["bucketName"]
filename = os.path.basename(FILE_TO_ANALYZE)
prefix = bucket_cfg['prefix']
compartmentId =scfg["oci"]["compartment"] 
    
upload(oci_cfg,bucket_cfg)
dus_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(oci.ai_document.AIServiceDocumentClient(config=oci_cfg))

features = [ oci.ai_document.models.DocumentClassificationFeature(),
            oci.ai_document.models.DocumentLanguageClassificationFeature(), 
            oci.ai_document.models.DocumentKeyValueExtractionFeature(),
            oci.ai_document.models.DocumentTableExtractionFeature(),
            oci.ai_document.models.DocumentTextExtractionFeature()
            ]
processor= dus_client.create_processor_job_and_wait_for_state(
    create_processor_job_details=create_processor(features,prefix,compartmentId,bucket_cfg),
    wait_for_states=[oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_SUCCEEDED],
    waiter_kwargs={"wait_callback": create_processor_job_callback})

    
print(f"processor call succeeded with status: {[processor.status]} and request_id: {processor.request_id}.")
processor_job: oci.ai_document.models.ProcessorJob = processor.data

print(f"Getting result json from the output_location {processor_job.id}")

object_storage_client = oci.object_storage.ObjectStorageClient(config=oci_cfg)
get_object_response = object_storage_client.get_object(namespace_name=namespace,
                                                       bucket_name=bucketName,
                                                       object_name=f"{prefix}/{processor_job.id}/{namespace}_{bucketName}/results/{prefix}/{filename}.json")

print(str(get_object_response.data.content.decode()))

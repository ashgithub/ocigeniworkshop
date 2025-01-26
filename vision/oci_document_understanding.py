#doc https://docs.oracle.com/en-us/iaas/Content/document-understanding/using/home.htm
#slack: #document-understanding


import oci
import io
import uuid
import sys
from oci.object_storage import ObjectStorageClient

#####
#Setup
#Change the compartmentid to yhe ocid of your compartment
#Change the profile if needed
#####

CONFIG_PROFILE = "AISANDBOX"
COMPARTMENT_ID= "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga" 
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"


PREFIX = "AAGARWA" # ********* CHANGE ME ************

config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

#### change per your environment
NAMESPACE = "axaemuxiyife"
BUCKET_NAME = "workshopbucket"
FILE_PATH = "reciept.png"
FILE_NAME ="reciept.png"


#print (" change the  names to your name & uncomment ")
#sys.exit(1)




def upload(file_path):
    object_storage_client = ObjectStorageClient(config)
    print(f"Uploading file {file_path} ...")
    object_storage_client.put_object(NAMESPACE, BUCKET_NAME, f"{PREFIX}/{FILE_NAME}", io.open(file_path,'rb'))
    print("Upload completed !")


# Setup input location where document being processed is stored.
def get_input_location(): 
    object_location = oci.ai_document.models.ObjectLocation()
    object_location.namespace_name = NAMESPACE 
    object_location.bucket_name = BUCKET_NAME  
    object_location.object_name = FILE_NAME

    return object_location

def get_output_location(): 
    object_location = oci.ai_document.models.OutputLocation()
    object_location.namespace_name = NAMESPACE 
    object_location.bucket_name = BUCKET_NAME  
    object_location.prefix = PREFIX

    return object_location

# Create a processor_job for text_extraction feature
def create_processor(features):
    display_name = f"{PREFIX}_job_{uuid.uuid4()}" 
    job_details = oci.ai_document.models.CreateProcessorJobDetails(
                                                    display_name=display_name,
                                                    compartment_id=COMPARTMENT_ID,
                                                    input_location=oci.ai_document.models.ObjectStorageLocations(object_locations=[get_input_location()]),
                                                    output_location= get_output_location(),
                                                    processor_config=oci.ai_document.models.GeneralProcessorConfig(features=features))
    return job_details 
    
def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)
    
    
#upload(FILE_PATH)
dus_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(oci.ai_document.AIServiceDocumentClient(config=config))

features = [ oci.ai_document.models.DocumentClassificationFeature(),
            oci.ai_document.models.DocumentLanguageClassificationFeature(), 
            oci.ai_document.models.DocumentKeyValueExtractionFeature(),
            oci.ai_document.models.DocumentTableExtractionFeature(),
            oci.ai_document.models.DocumentTextExtractionFeature()
            ]
processor= dus_client.create_processor_job_and_wait_for_state(
    create_processor_job_details=create_processor(features),
    wait_for_states=[oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_SUCCEEDED],
    waiter_kwargs={"wait_callback": create_processor_job_callback})

    
print(f"processor call succeeded with status: {[processor.status]} and request_id: {processor.request_id}.")
processor_job: oci.ai_document.models.ProcessorJob = processor.data

print("Getting result json from the output_location")
object_storage_client = oci.object_storage.ObjectStorageClient(config=config)
get_object_response = object_storage_client.get_object(namespace_name=NAMESPACE,
                                                       bucket_name=BUCKET_NAME,
                                                       object_name=f"{PREFIX}/{processor_job.id}/{NAMESPACE}_{BUCKET_NAME}/results/{FILE_NAME}.json")

print(str(get_object_response.data.content.decode()))

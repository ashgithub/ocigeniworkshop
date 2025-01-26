#https://github.com/oracle/oci-python-sdk/tree/22fd62c8dbbd1aaed6b75754ec1ba8a3c16a4e5a/src/oci/ai_speech
#https://docs.oracle.com/en-us/iaas/Content/speech/home.htm
# oci_speech_service_users or #igiu-innovation-lab slack channel

# if you have errors running sample code reach out for help in #igiu-ai-learning


from oci.ai_speech import AIServiceSpeechClient
from oci.ai_speech.models import *
from oci.config import from_file
from oci.signer import load_private_key_from_file
import oci
from oci.object_storage import ObjectStorageClient
import json,os,io,time 


#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"
FILE_TO_ANALYZE ="./speech/voice_sample3.mp3"
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

 
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
    
     
def getSpeechClient(oci_config):
    return AIServiceSpeechClient(config=oci_config,signer= oci.signer.Signer(
        tenancy=oci_config["tenancy"],
        user=oci_config["user"],
        fingerprint=oci_config["fingerprint"],
        private_key_file_location=oci_config["key_file"]
        ),
        service_endpoint=" https://speech.aiservice.us-phoenix-1.oci.oraclecloud.com")

def createTranscriptionJob(compartmentid, ai_client,bucket_cfg):
 
    # Give your job related details in these fields
    sample_display_name = f"{bucket_cfg['prefix']}-test-job"
    sample_compartment_id =compartmentid 
    sample_description = "Testing Oracle Speech Speech to Text"
    sample_object_location = oci.ai_speech.models.ObjectLocation(namespace_name=bucket_cfg["namespace"], bucket_name=bucket_cfg["bucketName"],
                                                                    object_names=[f"{bucket_cfg['prefix']}/{os.path.basename(FILE_TO_ANALYZE)}"])
 
    sample_input_location = oci.ai_speech.models.ObjectListInlineInputLocation(
                                 location_type="OBJECT_LIST_INLINE_INPUT_LOCATION", object_locations=[sample_object_location])
 
    sample_output_location = oci.ai_speech.models.OutputLocation(namespace_name=bucket_cfg["namespace"], bucket_name=bucket_cfg["bucketName"], prefix=bucket_cfg["prefix"])
 
    sample_normalization = oci.ai_speech.models.TranscriptionNormalization(is_punctuation_enabled=True)

    transcription_settings = oci.ai_speech.models.TranscriptionSettings(
        diarization= oci.ai_speech.models.Diarization(is_diarization_enabled=True)  # dosnt specify number_of_speakers as its auto detected
    )
    # For IAD, model type has to be WHISPER_LARGE_V2
    sample_model_details = oci.ai_speech.models.TranscriptionModelDetails(
#        language_code="en-US", #  <--- for ORACLE models
        language_code="en",     # .<--- for whisper model, try with other languages 
#        model_type="ORACLE",
        model_type="WHISPER_MEDIUM",
        domain = "GENERIC",   # only generic domain is supported for now
        transcription_settings =transcription_settings 
        )

 
    # Create Transcription Job with details provided
    transcription_job_details = oci.ai_speech.models.CreateTranscriptionJobDetails(display_name=sample_display_name,
        compartment_id=sample_compartment_id,
        description=sample_description,
        model_details=sample_model_details,
        input_location=sample_input_location,
        additional_transcription_formats=["SRT"],
        normalization=sample_normalization,
        output_location=sample_output_location)
 
    transcription_job = None
    transcribe_job_id = None 
    try:
        transcription_job = ai_client.create_transcription_job(create_transcription_job_details=transcription_job_details)
        transcribe_job_id = transcription_job.data.id
        print(f"Transcription Job ID: {transcribe_job_id}.")
    except Exception as e:
        print(e)
        
    return transcribe_job_id

def poll(ai_client,transcribe_job_id):

    # Poll for job completion
    data = None
    while True:
        transcribtion_job = ai_client.get_transcription_job(transcribe_job_id)
        job_status = transcribtion_job.data.lifecycle_state
        print(f"Current Status: {job_status}", end='\r')
    
        if job_status == "SUCCEEDED":
            print("\nTranscription job completed successfully!")
            data = transcribtion_job.data        
            break
        elif job_status == "FAILED":
            print("\nTranscription job failed.")
            break
        else:
            time.sleep(5)  # Wait 30 seconds before checking again 
    return data 

def retrieveTranscribedFile(oci_cfg, bucket_cfg, output_prefix):
    namespace = bucket_cfg["namespace"]
    bucketName =  bucket_cfg["bucketName"]
    object_storage_client = ObjectStorageClient(oci_cfg)
    # iterate through all files in the prefix 
    list_objects_response = object_storage_client.list_objects(
            namespace_name=namespace,
            bucket_name=bucketName, 
            prefix=output_prefix
        )
    for obj in list_objects_response.data.objects:
        response  = object_storage_client.get_object(namespace, bucketName, obj.name)
        _, file_extension = os.path.splitext(obj.name)
        filename = f"{FILE_TO_ANALYZE}{file_extension}"
        with open(filename,"w") as f:
            f.write(response.data.text)
        print (f"saved {filename}")

        
    
#read the config files 
scfg = load_config(SANDBOX_CONFIG_FILE)
oci_cfg = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])
bucket_cfg = scfg["bucket"]



upload(oci_cfg, bucket_cfg) 
ai_client = getSpeechClient(oci_cfg)
jobid  = createTranscriptionJob(scfg["oci"]["compartment"],ai_client,bucket_cfg)
job_response  = poll(ai_client, jobid)
print(f"getting files from {job_response.output_location.prefix}")
retrieveTranscribedFile(oci_cfg,bucket_cfg,job_response.output_location.prefix)
#https://github.com/oracle/oci-python-sdk/tree/22fd62c8dbbd1aaed6b75754ec1ba8a3c16a4e5a/src/oci/ai_speech
#https://docs.oracle.com/en-us/iaas/Content/speech/home.htm
# oci_speech_service_users or #igiu-innovation-lab slack channel


from oci.ai_speech import AIServiceSpeechClient
from oci.ai_speech.models import *
from oci.config import from_file
from oci.signer import load_private_key_from_file
import oci
from oci.object_storage import ObjectStorageClient
import io


#####
#Setup
#Change the compartmentid to yhe ocid of your compartment
#Change the profile if needed
#####

CONFIG_PROFILE = "AISANDBOX"
COMPARTMENT_ID= "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga" 
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

 
config = from_file('~/.oci/config', CONFIG_PROFILE)

## change per your environment
NAMESPACE = "axaemuxiyife"
BUCKET_NAME = "workshopbucket"
PREFIX = "AAGARWA"
FILE_NAME ="voiceover_audio.mp3"

def upload(file_path):
    object_storage_client = ObjectStorageClient(config)
    print(f"Uploading file {file_path} ...")
    object_storage_client.put_object(NAMESPACE, BUCKET_NAME, f"{PREFIX}/{FILE_NAME}", io.open(file_path,'rb'))
    print("Upload completed !")
    
     
def getSpeechClient():
    return AIServiceSpeechClient(config=config,signer= oci.signer.Signer(
        tenancy=config["tenancy"],
        user=config["user"],
        fingerprint=config["fingerprint"],
        private_key_file_location=config["key_file"]
        ),
        service_endpoint=" https://speech.aiservice.us-phoenix-1.oci.oraclecloud.com")

def createTranscriptionJob():
    ai_client = getSpeechClient()
    # Give your job related details in these fields
    sample_display_name = "TestWhisperJob"
    sample_compartment_id =COMPARTMENT_ID 
    sample_description = "Testing Whisper models using Freeform Tags"
    sample_object_location = oci.ai_speech.models.ObjectLocation(namespace_name=NAMESPACE, bucket_name=BUCKET_NAME,
    object_names=[FILE_NAME])
 
    sample_input_location = oci.ai_speech.models.ObjectListInlineInputLocation(
    location_type="OBJECT_LIST_INLINE_INPUT_LOCATION", object_locations=[sample_object_location])
 
    sample_output_location = oci.ai_speech.models.OutputLocation(namespace_name=NAMESPACE, bucket_name=BUCKET_NAME, prefix=PREFIX)
 
    sample_normalization = oci.ai_speech.models.TranscriptionNormalization(is_punctuation_enabled=True)

    transcription_settings = oci.ai_speech.models.TranscriptionSettings(
        diarization= oci.ai_speech.models.Diarization(is_diarization_enabled=True)  # dosnt specify number_of_speakers as its auto detected
    )
    # For IAD, model type has to be WHISPER_LARGE_V2
    sample_model_details = oci.ai_speech.models.TranscriptionModelDetails(
        language_code="en-US", 
        model_type="ORACLE",
        # model_type="WHISPER_MEDIUM",
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
    try:
        transcription_job = ai_client.create_transcription_job(create_transcription_job_details=transcription_job_details)
    except Exception as e:
        print(e)
    else:
        print(transcription_job.data)

#upload(FILENAME) 
createTranscriptionJob()
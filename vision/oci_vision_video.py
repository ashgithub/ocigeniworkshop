import oci
import io
from oci.ai_vision.models import *
from time import sleep

# make sure to run in an environment with preview sdk

#####
#Setup
#Change the compartmentid to the ocid of your compartment
#Change the profile if needed
#####
CONFIG_PROFILE = "AISANDBOX"
COMPARTMENT_ID= "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga" 
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"


config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

## change per your environment 

NAMESPACE = "axaemuxiyife"
BUCKET_NAME = "workshopbucket"
FILE_PATH = "/Users/ashish/work/code/python/workshop/vision/people_walking.mp4"
FILE_NAME ="mall.mp4"
PREFIX = "asaagarwa" # ********* CHANGE ME ************
ENDPOINT = 'https://vision.aiservice.us-ashburn-1.oci.oraclecloud.com' #service endpoint

# Setup input location where document being processed is stored.
def get_input_location(): 
    object_location = ObjectLocation()
    object_location.namespace_name = NAMESPACE 
    object_location.bucket_name = BUCKET_NAME  
    object_location.object_name = f"{PREFIX}/{FILE_NAME}"

    input_location = ObjectListInlineInputLocation()
    input_location.object_locations = [object_location]
    return input_location

def get_output_location(): 
    object_location = OutputLocation()
    object_location.namespace_name = NAMESPACE 
    object_location.bucket_name = BUCKET_NAME  
    object_location.prefix = PREFIX

    return object_location



#using API key
ai_service_vision_client = oci.ai_vision.AIServiceVisionClient(config=config)

video_object_detection_feature = VideoObjectDetectionFeature()
video_face_detection_feature = VideoFaceDetectionFeature()
video_label_detection_feature = VideoLabelDetectionFeature()
video_text_detection_feature = VideoTextDetectionFeature()
features = [video_text_detection_feature, video_face_detection_feature, video_label_detection_feature, video_object_detection_feature]


create_video_job_details = CreateVideoJobDetails()
create_video_job_details.features = features
create_video_job_details.compartment_id = COMPARTMENT_ID
create_video_job_details.output_location = get_output_location()
create_video_job_details.input_location = get_input_location()

res = ai_service_vision_client.create_video_job(create_video_job_details=create_video_job_details)

job_id = res.data.id
print(f"Job {job_id} is in {res.data.lifecycle_state} state.")

seconds = 0
while res.data.lifecycle_state == "IN_PROGRESS" or res.data.lifecycle_state == "ACCEPTED":
    print(f"Job {job_id} is IN_PROGRESS for {str(seconds)} seconds, progress: {res.data.percent_complete}")
    sleep(5)
    seconds += 5
    res = ai_service_vision_client.get_video_job(video_job_id=job_id)

print(f"Job {job_id} is in {res.data.lifecycle_state} state.")



#session token authentication
#object_storage_client = oci.object_storage.ObjectStorageClient(config, signer=signer)

#using api key
object_storage_client = oci.object_storage.ObjectStorageClient(config)
object_name = f"{PREFIX}/{job_id}/{FILE_NAME}.json"

video_response = object_storage_client.get_object(NAMESPACE, BUCKET_NAME, object_name)

#file = open('output.json', 'w')
#file.write(video_response.data.text)

print (video_response.data.text)
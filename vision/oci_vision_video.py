# if you have errors running sample code reach out for help in #igiu-ai-learning
# other questions #igiu-innovation-lab or #video-analysis-beta

#Note video support is not GA and requires a specific version of oci & video client. reach out to ashish.ag.agarwal@oracle.com

import oci
import io,json,os
from oci.ai_vision.models import *
from oci.object_storage import ObjectStorageClient
from time import sleep

# make sure to run in an environment with preview sdk

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####

SANDBOX_CONFIG_FILE = "sandbox.json"
FILE_TO_ANALYZE ="./vision/mall.mp4"



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
    object_location = ObjectLocation()
    object_location.namespace_name = bucket_cfg["namespace"]  
    object_location.bucket_name =  bucket_cfg["bucketName"]  
    object_location.object_name = f"{bucket_cfg['prefix']}/{os.path.basename(FILE_TO_ANALYZE)}"

    input_location = ObjectListInlineInputLocation()
    input_location.object_locations = [object_location]
    return input_location

def get_output_location(bucket_cfg): 
    object_location = OutputLocation()
    object_location.namespace_name = bucket_cfg["namespace"]   
    object_location.bucket_name =  bucket_cfg["bucketName"]    
    object_location.prefix =  f"{bucket_cfg['prefix']}"

    return object_location


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

ai_service_vision_client = oci.ai_vision.AIServiceVisionClient(config=oci_cfg)


video_object_detection_feature = VideoObjectDetectionFeature()
video_face_detection_feature = VideoFaceDetectionFeature()
video_label_detection_feature = VideoLabelDetectionFeature()
video_text_detection_feature = VideoTextDetectionFeature()
features = [video_text_detection_feature, video_face_detection_feature, video_label_detection_feature, video_object_detection_feature]


create_video_job_details = CreateVideoJobDetails()
create_video_job_details.features = features
create_video_job_details.compartment_id = compartmentId
create_video_job_details.output_location = get_output_location(bucket_cfg)
create_video_job_details.input_location = get_input_location(bucket_cfg)

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




object_storage_client = oci.object_storage.ObjectStorageClient(oci_cfg)
object_name = f"{prefix}/{job_id}/{prefix}/{filename}.json"

video_response = object_storage_client.get_object(namespace, bucketName, object_name)


print (video_response.data.text)
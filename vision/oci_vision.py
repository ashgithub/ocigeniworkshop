#https://github.com/oracle/oci-python-sdk/tree/22fd62c8dbbd1aaed6b75754ec1ba8a3c16a4e5a/src/oci/ai_vision
#https://docs.oracle.com/en-us/iaas/Content/vision/using/home.htm

# if you have errors running sample code reach out for help in #igiu-ai-learning
# other questions #igiu-innovation-lab or #oci_ai_vision_support

import oci,io 
import json,os
from oci.object_storage import ObjectStorageClient


#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####

SANDBOX_CONFIG_FILE = "sandbox.json"
FILE_TO_ANALYZE = "./vision/reciept.png"


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


def get_imag_location(bucket_cfg): 
    image = oci.ai_vision.models.ObjectStorageImageDetails(
                            source = "OBJECT_STORAGE",
                            namespace_name =  bucket_cfg["namespace"]  ,
                            bucket_name=bucket_cfg["bucketName"]  ,
                            object_name=f"{bucket_cfg['prefix']}/{os.path.basename(FILE_TO_ANALYZE)}"
    )

    return image

def get_details(features, compartmentId, bucket_cfg) :
    details = oci.ai_vision.models.AnalyzeImageDetails(
        
        features = features,
        image = get_imag_location(bucket_cfg),
        compartment_id=compartmentId
    )

    return details



#read the config files 
scfg = load_config(SANDBOX_CONFIG_FILE)
oci_cfg = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])
bucket_cfg = scfg["bucket"]
compartmentId =scfg["oci"]["compartment"] 

upload(oci_cfg,bucket_cfg)
vision_client = oci.ai_vision.AIServiceVisionClient(config=oci_cfg)

features = [ 
            oci.ai_vision.models.ImageClassificationFeature(),
            oci.ai_vision.models.ImageObjectDetectionFeature(),
            oci.ai_vision.models.ImageTextDetectionFeature(),
            oci.ai_vision.models.FaceDetectionFeature()
           ]

response = vision_client.analyze_image ( get_details (features, compartmentId, bucket_cfg))

print(response.data)
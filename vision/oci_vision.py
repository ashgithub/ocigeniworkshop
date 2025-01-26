#https://github.com/oracle/oci-python-sdk/tree/22fd62c8dbbd1aaed6b75754ec1ba8a3c16a4e5a/src/oci/ai_vision
#https://docs.oracle.com/en-us/iaas/Content/vision/using/home.htm

import oci
import io
import uuid
from oci.object_storage import ObjectStorageClient

CONFIG_PROFILE = "AISANDBOX"

config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)


#### change per your environment
COMPARTMENT_ID= "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga" 
NAMESPACE = "axaemuxiyife"
BUCKET_NAME = "workshopbucket"
PREFIX = "AAGARWA" # ********* CHANGE ME ************
FILE_NAME ="reciept.png"
FILE_TO_ANALYZE = "/tmp/images/reciept.png"


def upload(file_TO_ANALYZE):
    object_storage_client = ObjectStorageClient(config)
    print(f"Uploading file {file_TO_ANALYZE} ...")
    object_storage_client.put_object(NAMESPACE, BUCKET_NAME, f"{PREFIX}/{FILE_NAME}, io.open(file_TO_ANALYZE,'rb'))
    print("Upload completed !")


def get_imag_location(file_name): 
    image = oci.ai_vision.models.ObjectStorageImageDetails(
                            source = "OBJECT_STORAGE",
                            namespace_name = NAMESPACE,
                            bucket_name=BUCKET_NAME,
                            object_name=file_name
    )

    return image

def get_details(features, file_name) :
    details = oci.ai_vision.models.AnalyzeImageDetails(
        
        features = features,
        image = get_imag_location(file_name),
        compartment_id=COMPARTMENT_ID
    )

    return details


upload(FILE_TO_ANALYZE)
vision_client = oci.ai_vision.AIServiceVisionClient(config=config)

features = [ 
            oci.ai_vision.models.ImageClassificationFeature(),
            oci.ai_vision.models.ImageObjectDetectionFeature(),
            oci.ai_vision.models.ImageTextDetectionFeature(),
            oci.ai_vision.models.FaceDetectionFeature()
           ]

response = vision_client.analyze_image ( get_details (features, FILE_NAME))

print(response.data)
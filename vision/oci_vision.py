# Documentation: https://docs.oracle.com/en-us/iaas/Content/vision/using/home.htm
# GitHub SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/ai_vision
# Slack channels: #oci_ai_vision_support or #igiu-innovation-lab
# If you have errors running sample code, reach out for help in #igiu-ai-learning


from dotenv import load_dotenv
from envyaml import EnvYAML
from pathlib import Path
from oci.object_storage import ObjectStorageClient
import argparse
import oci
import os

#####
# Make sure your sandbox.yaml and .env files are set up for your environment.
# You might have to specify the full path depending on your current working directory (cwd).
# .env should define vars like MY_PREFIX (for bucket prefix).
#####

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()
DEFAULT_FILE = Path("./vision/receipt.png")  


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


def get_image_location(bucket_cfg, file_name):
    """Get ObjectStorageImageDetails for the uploaded image."""
    image = oci.ai_vision.models.ObjectStorageImageDetails(
        source="OBJECT_STORAGE",
        namespace_name=bucket_cfg["namespace"],
        bucket_name=bucket_cfg["bucketName"],
        object_name=f"{bucket_cfg['prefix']}/{file_name}"
    )
    return image
def get_analyze_image_details(features, compartment_id, bucket_cfg, file_name):
    """Prepare AnalyzeImageDetails for OCI Vision analysis."""
    details = oci.ai_vision.models.AnalyzeImageDetails(
        features=features,
        image=get_image_location(bucket_cfg, file_name),
        compartment_id=compartment_id
    )
    return details


def parse_vision_response(response_data):
    """Parse and print key results from OCI Vision analysis."""
    print("\nOCI Vision Analysis Results:")
    
    # Image Classification
    labels = response_data.labels
    if labels:
        print("\nClassifications:")
        for label in labels:
            print(f"  - {label.name}: {label.confidence:.2f}")
    
    # Object Detection
    image_objects = response_data.image_objects
    if image_objects:
        print("\nDetected Objects:")
        for obj in image_objects:
            print(f"  - {obj.name} : {obj.confidence:.2f}")
    
    # Text Detection
    image_text = response_data.image_text
    if image_text:
        print("\nDetected Text Lines:")
        for line in image_text.lines:
            print(f"  - {line.text}: {line.confidence:.2f}")
    
    # Face Detection
    detected_faces = response_data.detected_faces
    if detected_faces:
        print("\nDetected Faces:")
        for face in detected_faces:
            print(f"  - Face confidence: {face.confidence:.2f} : Quality {face.quality_score:.2f}")
    
    if not any([labels, image_objects, image_text, detected_faces]):
        print("No features detected in the image.")

def main(file_path=DEFAULT_FILE):
    """Main function to run OCI Vision analysis on the given image."""
    # Load config
    scfg = load_config(SANDBOX_CONFIG_FILE)
    if scfg is None:
        print("Failed to load config. Exiting.")
        return

    # Validate required sections
    if 'oci' not in scfg or 'bucket' not in scfg:
        print("Error: Missing 'oci' or 'bucket' section in config.")
        return

    oci_cfg = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]), scfg["oci"]["profile"])
    bucket_cfg = scfg["bucket"]
    compartment_id = scfg["oci"]["compartment"]

    # Upload file
    if not upload(oci_cfg, bucket_cfg, file_path):
        return

    # Create Vision client
    vision_client = oci.ai_vision.AIServiceVisionClient(config=oci_cfg)

    # Define features for analysis (classification, object/text/face detection)
    features = [
        oci.ai_vision.models.ImageClassificationFeature(),
        oci.ai_vision.models.ImageObjectDetectionFeature(),
        oci.ai_vision.models.ImageTextDetectionFeature(),
        oci.ai_vision.models.FaceDetectionFeature()
    ]

    try:
        # Analyze image
        response = vision_client.analyze_image(
            get_analyze_image_details(features, compartment_id, bucket_cfg, file_path.name)
        )
        
        if response.status == 200:
            parse_vision_response(response.data)
        else:
            print(f"Analysis failed: HTTP {response.status}")
    except Exception as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OCI Vision analysis on an image.")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="Path to the image to analyze (default: ./vision/receipt.png)")
    args = parser.parse_args()
    main(args.file)

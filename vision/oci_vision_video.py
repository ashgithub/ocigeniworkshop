# Documentation: https://docs.oracle.com/en-us/iaas/Content/vision/using/stored_video_analysis.htm#pretrained_image_analysis_video
# GitHub SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/ai_vision
# Postman collection: https://www.postman.com/oracledevs/oracle-cloud-infrastructure-rest-apis/collection/061avdq/vision-api
# Slack channels: #oci_ai_vision_support or #igiu-innovation-lab
# If you have errors running sample code, reach out for help in #igiu-ai-learning

from dotenv import load_dotenv
from envyaml import EnvYAML
from pathlib import Path
from oci.object_storage import ObjectStorageClient
from oci.ai_vision.models import (
    ObjectLocation,
    ObjectListInlineInputLocation,
    OutputLocation,
    CreateVideoJobDetails,
    VideoObjectDetectionFeature,
    VideoFaceDetectionFeature,
    VideoLabelDetectionFeature,
    VideoTextDetectionFeature
)
from time import sleep
import argparse
import json
import oci
import os

#####
# Make sure your sandbox.yaml and .env files are set up for your environment.
# You might have to specify the full path depending on your current working directory (cwd).
# .env should define vars like MY_PREFIX (for bucket prefix).
#####

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()
FILE_TO_ANALYZE = Path("./vision/mall.mp4")



def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
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


def get_input_location(bucket_cfg, file_name):
    """Build ObjectListInlineInputLocation for a specific file name."""
    object_location = ObjectLocation(
        namespace_name=bucket_cfg["namespace"],
        bucket_name=bucket_cfg["bucketName"],
        object_name=f"{bucket_cfg['prefix']}/{file_name}",
    )
    return ObjectListInlineInputLocation(object_locations=[object_location])

def get_output_location(bucket_cfg):
    object_location = OutputLocation(
        namespace_name=bucket_cfg["namespace"],
        bucket_name=bucket_cfg["bucketName"],
        prefix=bucket_cfg["prefix"],
    )
    return object_location


def parse_video_response(data):
    """Pretty-print OCI Vision VideoJob results (new schema only)."""
    print("\nOCI Video Vision Analysis Results:")

    # ------------------------------------------------------------------ #
    # Labels
    # ------------------------------------------------------------------ #
    video_labels = data.get("videoLabels", [])
    if video_labels:
        print("\nLabels:")
        for lab in video_labels:
            print(f"  {lab.get('name', 'Unknown')}")
            for seg in lab.get("segments", []):
                span = seg.get("videoSegment", {})
                start = span.get("startTimeOffsetMs", "N/A")
                end = span.get("endTimeOffsetMs", "N/A")
                conf = seg.get("confidence", 0)
                print(f"    {start}-{end}ms  conf={conf:.2f}")

    # ------------------------------------------------------------------ #
    # Objects
    # ------------------------------------------------------------------ #
    video_objects = data.get("videoObjects", [])
    if video_objects:
        print("\nObjects:")
        for obj in video_objects:
            label = obj.get("name", "Unknown")
            for seg in obj.get("segments", []):
                span = seg.get("videoSegment", {})
                start = span.get("startTimeOffsetMs", "N/A")
                end = span.get("endTimeOffsetMs", "N/A")
                conf = seg.get("confidence", 0)
                print(f"    {start}-{end}ms  {label}  conf={conf:.2f}")

    # ------------------------------------------------------------------ #
    # Text
    # ------------------------------------------------------------------ #
    video_texts = data.get("videoTexts", [])
    if video_texts:
        print("\nText Lines:")
        for txt in video_texts:
            content = txt.get("text", "")
            for seg in txt.get("segments", []):
                span = seg.get("videoSegment", {})
                start = span.get("startTimeOffsetMs", "N/A")
                end = span.get("endTimeOffsetMs", "N/A")
                conf = seg.get("confidence", 0)
                print(f"    {start}-{end}ms  \"{content}\"  conf={conf:.2f}")

    # ------------------------------------------------------------------ #
    # Faces
    # ------------------------------------------------------------------ #
    video_faces = data.get("videoFaces", [])
    if video_faces:
        print("\nFaces:")
        for face in video_faces:
            for seg in face.get("segments", []):
                span = seg.get("videoSegment", {})
                start = span.get("startTimeOffsetMs", "N/A")
                end = span.get("endTimeOffsetMs", "N/A")
                conf = seg.get("confidence", 0)
                print(f"    {start}-{end}ms  Face  conf={conf:.2f}")

    if not any([video_labels, video_objects, video_texts, video_faces]):
        print("No features detected.")



def main(file_path=FILE_TO_ANALYZE):
    """Main function to run OCI Video Vision analysis on the given video."""
    # Ensure pathlib.Path instance
    file_path = Path(file_path)
    # Load config
    scfg = load_config(SANDBOX_CONFIG_FILE)
    if scfg is None or 'oci' not in scfg or 'bucket' not in scfg:
        print("Error: Invalid configuration.")
        return
    
    # Validate required sections
    if 'configFile' not in scfg['oci'] or 'profile' not in scfg['oci'] or 'compartment' not in scfg['oci']:
        print("Error: Missing required OCI configuration.")
        return

    if 'namespace' not in scfg['bucket'] or 'bucketName' not in scfg['bucket'] or 'prefix' not in scfg['bucket']:
        print("Error: Missing required bucket configuration.")
        return

    # Validate required sections
    if 'oci' not in scfg or 'bucket' not in scfg:
        print("Error: Missing 'oci' or 'bucket' section in config.")
        return

    oci_cfg = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]), scfg["oci"]["profile"])
    bucket_cfg = scfg["bucket"]
    namespace = bucket_cfg["namespace"]
    bucket_name = bucket_cfg["bucketName"]
    prefix = bucket_cfg['prefix']
    compartment_id = scfg["oci"]["compartment"]

    # Upload file
    if not upload(oci_cfg, bucket_cfg, file_path):
        return

    # Create Video Vision client
    ai_service_vision_client = oci.ai_vision.AIServiceVisionClient(config=oci_cfg)

    # Define features for video analysis (label, object, text, face detection over time)
    video_object_detection_feature = VideoObjectDetectionFeature()
    video_face_detection_feature = VideoFaceDetectionFeature()
    video_label_detection_feature = VideoLabelDetectionFeature()
    video_text_detection_feature = VideoTextDetectionFeature()
    features = [video_text_detection_feature, video_face_detection_feature, video_label_detection_feature, video_object_detection_feature]

    try:
        # Create video job
        create_video_job_details = CreateVideoJobDetails()
        create_video_job_details.features = features
        create_video_job_details.compartment_id = compartment_id
        create_video_job_details.output_location = get_output_location(bucket_cfg)
        create_video_job_details.input_location = get_input_location(bucket_cfg, file_path.name)

        res = ai_service_vision_client.create_video_job(create_video_job_details=create_video_job_details)

        if res is not None and hasattr(res, 'data') and hasattr(res.data, 'id') and hasattr(res.data, 'lifecycle_state'):
            job_id = res.data.id
            print(f"Job {job_id} is in {res.data.lifecycle_state} state.")

            # Poll for completion
            seconds = 0
            while res is not None and hasattr(res, 'data') and hasattr(res.data, 'lifecycle_state') and res.data.lifecycle_state in ["IN_PROGRESS", "ACCEPTED"]:
                if hasattr(res.data, 'percent_complete'):
                    print(f"Job {job_id} is IN_PROGRESS for {seconds} seconds, progress: {res.data.percent_complete}%")
                sleep(5)
                seconds += 5
                res = ai_service_vision_client.get_video_job(video_job_id=job_id)

            if res is not None and hasattr(res, 'data') and hasattr(res.data, 'lifecycle_state'):
                if res.data.lifecycle_state == "SUCCEEDED":
                    print(f"Job {job_id} succeeded.")

                    # Get results from Object Storage
                    object_storage_client = oci.object_storage.ObjectStorageClient(oci_cfg)
                    object_name = f"{prefix}/{job_id}/{prefix}/{file_path.name}.json"

                    response = object_storage_client.get_object(namespace, bucket_name, object_name)

                    if response is not None and hasattr(response, 'status') and response.status == 200:
                        if hasattr(response, 'data') and hasattr(response.data, 'content'):
                            json_data = json.loads(response.data.content.decode('utf-8'))
                            parse_video_response(json_data)
                        else:
                            print("Error: Invalid response data.")
                    else:
                        print(f"Failed to get results: HTTP {getattr(response, 'status', 'Unknown')}")
                else:
                    print(f"Job {job_id} failed with state: {getattr(res.data, 'lifecycle_state', 'Unknown')}")
            else:
                print("Error: Invalid response from video job.")
    except Exception as e:
        print(f"Error during video job: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OCI Video Vision analysis on a video file.")
    parser.add_argument("--file", type=Path, default=FILE_TO_ANALYZE, help="Path to the video to analyze (default: ./vision/mall.mp4)")
    args = parser.parse_args()
    main(args.file)

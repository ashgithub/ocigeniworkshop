"""
What this file does:
Analyzes video with OCI Vision's pre-trained models for labels, objects, text, and faces.

Documentation to reference:
- OCI Vision Video Analysis: https://docs.oracle.com/en-us/iaas/Content/vision/using/stored_video_analysis.htm#pretrained_image_analysis_video
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/ai_vision
- Postman collection: https://www.postman.com/oracledevs/oracle-cloud-infrastructure-rest-apis/collection/061avdq/vision-api

Relevant slack channels:
- #oci_ai_vision_support: for OCI Vision API questions
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and bucket details.
- .env: Load environment variables if needed.

How to run the file:
uv run vision/oci_vision_video.py [--file path/to/video]

Comments to important sections of file:
- Step 1: Load and validate configuration.
- Step 2: Extract configuration values.
- Step 3: Upload video to Object Storage.
- Step 4: Create Vision client.
- Step 5: Define video analysis features.
- Step 6: Set up input and output locations.
- Step 7: Create video job details.
- Step 8: Submit video analysis job.
- Step 9: Poll for job completion.
- Step 10: Download and parse results.
"""

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
DEFAULT_VIDEO_PATH = Path("./vision/mall.mp4")



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



def main(file_path=DEFAULT_VIDEO_PATH):
    """Main function to run OCI Video Vision analysis on the given video."""
    # Ensure pathlib.Path instance
    file_path = Path(file_path)
    # Load config
    scfg = load_config(SANDBOX_CONFIG_FILE)

    # Step 1: Load and validate configuration
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

    # Step 2: Extract configuration values
    oci_cfg = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]), scfg["oci"]["profile"])
    bucket_cfg = scfg["bucket"]
    namespace = bucket_cfg["namespace"]
    bucket_name = bucket_cfg["bucketName"]
    prefix = bucket_cfg['prefix']
    compartment_id = scfg["oci"]["compartment"]

    # Step 3: Upload video to Object Storage
    if not upload(oci_cfg, bucket_cfg, file_path):
        return

    # Step 4: Create Vision client
    ai_service_vision_client = oci.ai_vision.AIServiceVisionClient(config=oci_cfg)

    # Step 5: Define video analysis features
    video_object_detection_feature = VideoObjectDetectionFeature()
    video_face_detection_feature = VideoFaceDetectionFeature()
    video_label_detection_feature = VideoLabelDetectionFeature()
    video_text_detection_feature = VideoTextDetectionFeature()
    features = [video_text_detection_feature, video_face_detection_feature, video_label_detection_feature, video_object_detection_feature]

    try:
        # Step 6: Set up input and output locations
        # Step 7: Create video job details
        # Step 8: Submit video analysis job
        create_video_job_details = CreateVideoJobDetails()
        create_video_job_details.features = features
        create_video_job_details.compartment_id = compartment_id
        create_video_job_details.output_location = get_output_location(bucket_cfg)
        create_video_job_details.input_location = get_input_location(bucket_cfg, file_path.name)

        res = ai_service_vision_client.create_video_job(create_video_job_details=create_video_job_details)

        if res is not None and hasattr(res, 'data') and hasattr(res.data, 'id') and hasattr(res.data, 'lifecycle_state'):
            job_id = res.data.id
            print(f"Job {job_id} is in {res.data.lifecycle_state} state.")

            # Step 9: Poll for job completion
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

                    # Step 10: Download and parse results
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

# Experimentation: Try with different videos, or modify features to focus on specific detection types.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OCI Video Vision analysis on a video file.")
    parser.add_argument("--file", type=Path, default=DEFAULT_VIDEO_PATH, help="Path to the video to analyze (default: ./vision/mall.mp4)")
    args = parser.parse_args()
    main(args.file)

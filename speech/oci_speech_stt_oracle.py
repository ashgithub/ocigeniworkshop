"""
oci_speech_stt_refactored.py
───────────────────────────────────────────────────────────────────────────────
Oracle Cloud Infrastructure – Speech-to-Text (STT) helper script.

Docs / Links
• Service docs:    https://docs.oracle.com/en-us/iaas/Content/speech/home.htm
• Python SDK:      https://github.com/oracle/oci-python-sdk/tree/master/src/oci/ai_speech
• Real time:       https://github.com/oracle/oci-ai-speech-realtime-python-sdk
• Support Slack:   #oci_speech_service_users   |  #igiu-innovation-lab
• Troubleshooting: #igiu-ai-learning

This script uploads an audio file to Object Storage, submits a transcription
job, polls until completion, and downloads the result (TXT + optional SRT). This verison uses Oracle model. 

see this for comparision of whisper & oracle models: https://docs.oracle.com/en-us/iaas/Content/speech/using/speech.htm#compare-models

The structure mirrors vision/oci_vision.py for consistency:
    1. Constants & configuration
    2. Small helper functions (upload, job creation, etc.)
    3. main() orchestrator built on argparse
    4. Standard Python entry point
───────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

# ── Standard Library ────────────────────────────────────────────────────────
import argparse
import io
import logging
import os
import time
from pathlib import Path
from typing import Optional

# ── Third-party ─────────────────────────────────────────────────────────────
from dotenv import load_dotenv
from envyaml import EnvYAML

# ── OCI SDK ────────────────────────────────────────────────────────────────
import oci
from oci.ai_speech import AIServiceSpeechClient
from oci.object_storage import ObjectStorageClient
from oci.signer import load_private_key_from_file

# ── Configuration / Constants ──────────────────────────────────────────────
SANDBOX_CONFIG_FILE = "sandbox.yaml"          # Location of your YAML config
DEFAULT_AUDIO_FILE = Path("./speech/voice_sample_english.mp3")
DEFAULT_OUTPUT_FORMATS = ["SRT"]       # Additional formats

# Supported language codes for transcription
SUPPORTED_LANGUAGE_CODES = {
    "en-US": "English - United States",
    "es-ES": "Spanish - Spain",
    "pt-BR": "Portuguese - Brazil",
    "en-GB": "English - Great Britain",
    "en-AU": "English - Australia",
    "en-IN": "English - India",
    "hi-IN": "Hindi - India",
    "fr-FR": "French - France",
    "de-DE": "German - Germany",
    "it-IT": "Italian - Italy",
}

# OCI endpoint override (Phoenix default)
SPEECH_SERVICE_ENDPOINT = (
    "https://speech.aiservice.us-phoenix-1.oci.oraclecloud.com"
)

# -------------------------------------------------------------------------- #
load_dotenv()  # Loads any variables referenced in sandbox.yaml (${VAR})
logger = logging.getLogger("stt")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s"
)


# ── Helper Functions ────────────────────────────────────────────────────────
def load_config(config_path: str | Path) -> Optional[EnvYAML]:
    """
    Load sandbox.yaml with ${ENV_VAR} substitution.

    Args:
        config_path: Path to sandbox YAML.

    Returns:
        EnvYAML object or None if error.
    """
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        logger.error("Configuration file '%s' not found.", config_path)
        return None
    except Exception as exc:  # noqa: BLE001
        logger.error("Error loading config: %s", exc)
        return None


def get_speech_client(oci_cfg: dict) -> AIServiceSpeechClient:
    """
    Build authenticated AIServiceSpeechClient using signer.

    Args:
        oci_cfg: Dict produced by oci.config.from_file()

    Returns:
        AIServiceSpeechClient
    """
    return AIServiceSpeechClient(
        config=oci_cfg,
        signer=oci.signer.Signer(
            tenancy=oci_cfg["tenancy"],
            user=oci_cfg["user"],
            fingerprint=oci_cfg["fingerprint"],
            private_key_file_location=oci_cfg["key_file"],
        ),
        service_endpoint=SPEECH_SERVICE_ENDPOINT,
    )


def upload_audio(
    oci_cfg: dict, bucket_cfg: EnvYAML, file_path: Path, prefix: str
) -> bool:
    """
    Upload the audio file to Object Storage.

    Args:
        oci_cfg: OCI config dict.
        bucket_cfg: Bucket section of sandbox.yaml.
        file_path: Path to local audio.
        prefix: Object-storage prefix/folder.

    Returns:
        True on success.
    """
    if not file_path.exists():
        logger.error("File '%s' not found.", file_path)
        return False

    client = ObjectStorageClient(oci_cfg)
    object_name = f"{prefix}/{file_path.name}"
    logger.info("Uploading %s → oci://%s/%s/%s", file_path, bucket_cfg["namespace"],
                bucket_cfg["bucketName"], object_name)
    with file_path.open("rb") as fh:
        client.put_object(
            bucket_cfg["namespace"], bucket_cfg["bucketName"], object_name, fh
        )
    logger.info("Upload complete.")
    return True


def create_transcription_job(
    speech_client: AIServiceSpeechClient,
    compartment_id: str,
    bucket_cfg: EnvYAML,
    prefix: str,
    file_name: str,
    language_code: str,
    additional_formats: list[str] | None = None,
) -> Optional[str]:
    """
    Submit a transcription job and return its OCID.

    Args:
        speech_client: Authenticated AIServiceSpeechClient.
        compartment_id: Target OCI compartment OCID.
        bucket_cfg: Bucket config section.
        prefix: Object prefix/folder.
        file_name: Name of the uploaded object.
        additional_formats: Extra output formats e.g. ["SRT"]

    Returns:
        Job OCID or None if submission failed.
    """
    object_location = oci.ai_speech.models.ObjectLocation(
        namespace_name=bucket_cfg["namespace"],
        bucket_name=bucket_cfg["bucketName"],
        object_names=[f"{prefix}/{file_name}"],
    )

    input_location = oci.ai_speech.models.ObjectListInlineInputLocation(
        location_type="OBJECT_LIST_INLINE_INPUT_LOCATION",
        object_locations=[object_location],
    )

    output_location = oci.ai_speech.models.OutputLocation(
        namespace_name=bucket_cfg["namespace"],
        bucket_name=bucket_cfg["bucketName"],
        prefix=prefix,
    )

    normalization = oci.ai_speech.models.TranscriptionNormalization(
        is_punctuation_enabled=True
    )

    transcription_settings = oci.ai_speech.models.TranscriptionSettings(
        diarization=oci.ai_speech.models.Diarization(is_diarization_enabled=True)
    )

    model_details = oci.ai_speech.models.TranscriptionModelDetails(
        language_code=language_code,
        model_type="ORACLE",  # or ORACLE when US-IAD region
        domain="GENERIC",
        transcription_settings=transcription_settings,
    )

    job_details = oci.ai_speech.models.CreateTranscriptionJobDetails(
        display_name=f"{prefix}-stt-job",
        compartment_id=compartment_id,
        description="OCI Speech-to-Text Example",
        model_details=model_details,
        input_location=input_location,
        output_location=output_location,
        normalization=normalization,
        additional_transcription_formats=additional_formats or [],
    )

    try:
        response = speech_client.create_transcription_job(
            create_transcription_job_details=job_details
        )
        job_id = response.data.id
        logger.info("Transcription job submitted. OCID=%s", job_id)
        return job_id
    except Exception as exc:  # noqa: BLE001
        logger.error("Job submission failed: %s", exc)
        return None


def wait_for_job(
    speech_client: AIServiceSpeechClient,
    job_id: str,
    poll_seconds: int = 5,
) -> Optional[oci.ai_speech.models.TranscriptionJob]:
    """
    Poll the job until it succeeds or fails.

    Args:
        speech_client: Authenticated client.
        job_id: Transcription job OCID.
        poll_seconds: Interval between polls.

    Returns:
        TranscriptionJob object on success, else None.
    """
    while True:
        job = speech_client.get_transcription_job(job_id).data
        state = job.lifecycle_state
        logger.info("Job %s status: %s", job_id, state)
        if state == "SUCCEEDED":
            return job
        if state == "FAILED":
            logger.error("Job %s failed.", job_id)
            return None
        time.sleep(poll_seconds)


def download_outputs(
    oci_cfg: dict,
    bucket_cfg: EnvYAML,
    output_prefix: str,
    local_base: Path,
) -> None:
    """
    Download result files for the given job into current directory.

    Args:
        oci_cfg: Auth OCI config.
        bucket_cfg: Bucket config section.
        prefix: Bucket prefix (folder).
        local_base: Original audio path (used to name output files).
        job_id: Transcription job OCID.
    """
    client = ObjectStorageClient(oci_cfg)
    list_objects = client.list_objects(
        namespace_name=bucket_cfg["namespace"],
        bucket_name=bucket_cfg["bucketName"],
        prefix=output_prefix,
    )

    for obj in list_objects.data.objects:
        _, ext = os.path.splitext(obj.name)
        local_file = local_base.with_suffix(ext or ".txt")
        logger.info("Downloading %s → %s", obj.name, local_file)
        resp = client.get_object(
            bucket_cfg["namespace"], bucket_cfg["bucketName"], obj.name
        )
        with local_file.open("wb") as fh:
            fh.write(resp.data.content)
        
    logger.info("All outputs downloaded.")


# ── Main Orchestrator ───────────────────────────────────────────────────────
def main() -> None:  # noqa: C901
    """
    Parse CLI arguments, upload file, submit job, and fetch results.
    """
    parser = argparse.ArgumentParser(
        description="OCI Speech-to-Text utility (refactored)."
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_AUDIO_FILE,
        help=f"Audio file to transcribe (default: {DEFAULT_AUDIO_FILE})",
    )
    parser.add_argument(
        "-l", "--language",
        default="en-US",
        choices=SUPPORTED_LANGUAGE_CODES.keys(),
        help="Language code for transcription (default: en-US)",
    )
    parser.add_argument(
        "--formats",
        nargs="*",
        default=DEFAULT_OUTPUT_FORMATS,
        help='Extra transcript formats, e.g. --formats SRT',
    )

    args = parser.parse_args()


    # 1. Load sandbox.yaml
    scfg = load_config(SANDBOX_CONFIG_FILE)
    if scfg is None or "oci" not in scfg or "bucket" not in scfg:
        logger.error("Invalid sandbox configuration.")
        return

    bucket_cfg = scfg["bucket"]
    oci_cfg = oci.config.from_file(
        os.path.expanduser(scfg["oci"]["configFile"]), scfg["oci"]["profile"]
    )
    compartment_id = scfg["oci"]["compartment"]
    prefix = bucket_cfg["prefix"]

    # 2. Upload audio
    if not upload_audio(oci_cfg, bucket_cfg, args.file, prefix):
        return

    # 3. Submit job
    speech_client = get_speech_client(oci_cfg)
    job_id = create_transcription_job(
        speech_client,
        compartment_id,
        bucket_cfg,
        prefix,
        args.file.name,
        args.language,
        args.formats,
    )
    if job_id is None:
        return

    # 4. Wait for completion
    job = wait_for_job(speech_client, job_id)
    if job is None:
        return

    # 5. Download outputs
    download_outputs(oci_cfg, bucket_cfg, job.output_location.prefix, args.file)


# ── Entry Point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    """
    Example usage:

        python speech/oci_speech_stt_refactored.py \
            --file ./speech/voice_sample3.mp3 \
            --formats SRT

    """
    main()

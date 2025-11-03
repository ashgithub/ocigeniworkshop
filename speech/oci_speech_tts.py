"""
oci_speech_tts_whisper.py
───────────────────────────────────────────────────────────────────────────────
Oracle Cloud Infrastructure – Text-to-Speech (TTS) helper script.

Docs / Links
• Service docs:  https://docs.oracle.com/en-us/iaas/Content/speech/using/using-tts.htm
  (lists all supported languages & voices and their language-codes)
• Python SDK:    https://github.com/oracle/oci-python-sdk/tree/master/src/oci/ai_speech
• Slack:         #oci_speech_service_users  |  #igiu-innovation-lab
• Troubleshoot:  #igiu-ai-learning

Overview
--------
1. Read UTF-8 text from a file (defaults to speech/text_sample_english.txt).  
2. Detect the dominant language with OCI AI Language (batch API).  
3. Map that language code to a (voice_id, oci_language_code) pair.  
4. Call OCI TTS and save an MP3 with the same basename as the input file.  
5. All parameters have sensible defaults; run with no flags for a quick demo.

Example
    python speech/oci_speech_tts_whisper.py
    python speech/oci_speech_tts_whisper.py speech/text_sample_spanish.txt
"""
from __future__ import annotations

# ── Standard Library ────────────────────────────────────────────────────────
import argparse
import logging
import os
from pathlib import Path
from typing import Tuple

# ── Third-party ─────────────────────────────────────────────────────────────
from dotenv import load_dotenv
from envyaml import EnvYAML
import oci

# ── OCI SDK Imports ─────────────────────────────────────────────────────────
from oci.ai_speech import AIServiceSpeechClient
from oci.ai_speech.models import (
    SynthesizeSpeechDetails,
    TtsOracleConfiguration,
    TtsOracleSpeechSettings,
    TtsOracleTts2NaturalModelDetails,
)
from oci.ai_language import AIServiceLanguageClient
from oci.ai_language.models import (
    BatchDetectDominantLanguageDetails,
    DominantLanguageDocument,
)

# ── Config & Constants ──────────────────────────────────────────────────────
SANDBOX_CONFIG_FILE = "sandbox.yaml"

SPEECH_ENDPOINT = "https://speech.aiservice.us-phoenix-1.oci.oraclecloud.com"
SAMPLE_RATE = 22_050
OUTPUT_FORMAT = TtsOracleSpeechSettings.OUTPUT_FORMAT_MP3

# Map ISO-639-1 code → (voice_id, oci_language_code)
# Expand this as additional voices become available.
LANGUAGE_TTS_MAP: dict[str, Tuple[str, str]] = {
    "en": ("Stacy", "en-US"),
    "hi": ("Priya", "hi-IN"),
    "es": ("Paco", "es-ES"),
    "fr": ("Chloe", "fr-FR"),
    "de": ("Hans", "de-DE"),
}

# ── Logging / Env ───────────────────────────────────────────────────────────
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger("oci-tts-whisper")


# ── Helper Functions ───────────────────────────────────────────────────────
def load_yaml(path: Path) -> EnvYAML | None:
    try:
        return EnvYAML(path)
    except Exception as exc:  # noqa: BLE001
        log.error("Failed to load YAML %s: %s", path, exc)
        return None


def make_oci_config(scfg: EnvYAML) -> dict:
    return oci.config.from_file(
        os.path.expanduser(scfg["oci"]["configFile"]),
        scfg["oci"]["profile"],
    )


def detect_language(text: str, cfg: dict, compartment: str) -> str:
    """
    Detect dominant language using the batch API.
    Returns ISO-639-1/2 code; 'en' fallback if detection fails.
    """
    client = AIServiceLanguageClient(config=cfg)
    req = BatchDetectDominantLanguageDetails(
        documents=[DominantLanguageDocument(key="1", text=text)],
        compartment_id=compartment,
    )
    res = client.batch_detect_dominant_language(req)

    if (
        getattr(res, "status", None) == 200
        and res.data.documents
        and res.data.documents[0].languages
    ):
        top = res.data.documents[0].languages[0]
        lang_code = top.code.lower()
        log.info("Detected language %s (confidence %.2f)", lang_code, top.score)
        return lang_code

    log.warning("Language detection failed; defaulting to 'en'")
    return "en"


def voice_and_lang_for(code: str) -> Tuple[str, str]:
    """
    Map language code to (voice_id, oci_language_code) tuple.
    Falls back to English voice if code missing.
    """
    base = code.split("-")[0]
    return LANGUAGE_TTS_MAP.get(base, LANGUAGE_TTS_MAP["en"])


def synthesize_mp3(
    text: str,
    voice_id: str,
    oci_lang_code: str,
    outfile: Path,
    cfg: dict,
    compartment: str,
) -> None:
    """Generate speech (standard model) and write MP3."""
    client = AIServiceSpeechClient(
        config=cfg
    )

    details = SynthesizeSpeechDetails(
        text=text,
        is_stream_enabled=False,
        compartment_id=compartment,
        configuration=TtsOracleConfiguration(
            model_details=TtsOracleTts2NaturalModelDetails(
                voice_id=voice_id,
                language_code=oci_lang_code,
            ),
            speech_settings=TtsOracleSpeechSettings(
                text_type=TtsOracleSpeechSettings.TEXT_TYPE_TEXT,
                sample_rate_in_hz=SAMPLE_RATE,
                output_format=OUTPUT_FORMAT,
            ),
        ),
    )

    res = client.synthesize_speech(details)
    if res.status != 200:
        raise RuntimeError(f"TTS failed HTTP {res.status}")

    with outfile.open("wb") as fh:
        for chunk in res.data.iter_content():
            fh.write(chunk)
    log.info("MP3 saved → %s", outfile.resolve())


# ── CLI / Main ──────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Text-file → Language detect → OCI TTS MP3",
        epilog="Supported lang→voice: "
        + ", ".join(f"{k}→{v[0]}" for k, v in LANGUAGE_TTS_MAP.items()),
    )
    parser.add_argument(
        "text_file",
        nargs="?",
        type=Path,
        default=Path("speech/text_sample_english.txt"),
        help="UTF-8 text file (default: speech/text_sample_english.txt)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=SANDBOX_CONFIG_FILE,
        help="sandbox.yaml path",
    )
    args = parser.parse_args()

    if not args.text_file.exists():
        log.error("File not found: %s", args.text_file)
        return
    text = args.text_file.read_text(encoding="utf-8").strip()
    if not text:
        log.error("Input file is empty.")
        return

    scfg = load_yaml(args.config)
    if scfg is None:
        return
    cfg = make_oci_config(scfg)
    compartment = scfg["oci"]["compartment"]

    lang_code = detect_language(text, cfg, compartment)
    voice_id, oci_lang = voice_and_lang_for(lang_code)

    mp3_path = args.text_file.with_suffix(".mp3")
    log.info("Synthesizing with voice '%s' (%s)", voice_id, oci_lang)
    synthesize_mp3(text, voice_id, oci_lang, mp3_path, cfg, compartment)


if __name__ == "__main__":
    main()

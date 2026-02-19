## Welcome to the Speech Module

In this module, you will experiment with Oracle Cloud Infrastructure (OCI) Speech services for **Text-to-Speech (TTS)** and **Speech-to-Text (STT)**.

### What you will try

1. **Text-to-Speech (TTS)** – Explore available voice models, convert text to speech, and experiment with different languages.
2. **Speech-to-Text (STT)** – Use batch transcription with OCI Speech (Oracle model) and Whisper models, compare results.

> **Note**  
> OCI Speech also supports real-time transcription, but that feature is not covered in this module.

---

### Environment Setup

- **sandbox.yaml**: Contains OCI config, compartment, bucket details.
- **.env**: Load environment variables if needed.
- This module uses the `oci` and `bucket` sections.
- For STT, ensure access to Object Storage bucket in PHX tenancy with a unique prefix (e.g., your Oracle ID).

### Working with STT

Audio files must be uploaded to an Object Storage bucket before transcription.

- Use the **PHX** tenancy for your bucket (Chicago is read-only).
- Fill in the `bucket` section of `sandbox.yaml` with your bucket details (`namespace`, `bucketName`, `prefix`).
- Update `DEFAULT_AUDIO_FILE` in scripts to point to local audio files.

### Working with TTS

- Try text files in different languages.
- Experiment with different voices by modifying `LANGUAGE_TTS_MAP` in the code.

---

### Suggested Study Order and File Descriptions

The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **oci_speech_stt_oracle.py**: Demonstrates STT using OCI's Oracle model. Uploads audio to Object Storage, submits transcription job, polls for completion, downloads results (TXT + SRT).
   - Key features: Uses Oracle model for transcription; supports language codes.
   - How to run: `uv run speech/oci_speech_stt_oracle.py --file speech/voice_sample_english.mp3 --language en-US`
   - Docs: [OCI Speech STT](https://docs.oracle.com/en-us/iaas/Content/speech/using/speech.htm)

2. **oci_speech_stt_whisper.py**: Demonstrates STT using Whisper model. Similar to Oracle script but uses auto language detection.
   - Key features: Uses Whisper model; language auto-detected.
   - How to run: `uv run speech/oci_speech_stt_whisper.py --file speech/voice_sample_english.mp3`
   - Docs: [Whisper Model](https://docs.oracle.com/en-us/iaas/Content/speech/using/speech.htm#compare-models)

3. **oci_speech_tts.py**: Demonstrates TTS. Reads text file, detects language, maps to voice, synthesizes MP3.
   - Key features: Language detection via OCI Language API; supports multiple voices/languages.
   - How to run: `uv run speech/oci_speech_tts.py speech/text_sample_english.txt`
   - Docs: [OCI Speech TTS](https://docs.oracle.com/en-us/iaas/Content/speech/using/using-tts.htm)

4. **oci_speech_stt.ipynb**: Jupyter notebook version of STT with Oracle/Whisper models. Interactive cells for transcription.
   - Key features: Mirrors scripts; prints transcripts; experiment with different files/models.
   - How to run: Open in Jupyter and run cells sequentially.
   - Docs: [OCI Speech STT](https://docs.oracle.com/en-us/iaas/Content/speech/using/speech.htm)

5. **oci_speech_tts.ipynb**: Jupyter notebook for TTS. Detects language, synthesizes, plays audio.
   - Key features: Interactive TTS; plays audio directly; experiment with texts/voices.
   - How to run: Open in Jupyter and run cells sequentially.
   - Docs: [OCI Speech TTS](https://docs.oracle.com/en-us/iaas/Content/speech/using/using-tts.htm)

### Sample Files

- **Audio files**: `voice_sample_english.mp3`, `voice_sample_french.mp3`, `voice_sample_hindi.mp3`, `voice_sample_spanish.mp3` – Use for STT testing.
- **Text files**: `text_sample_english.txt`, `text_sample_french.txt`, `text_sample_hindi.txt`, `text_sample_spanish.txt` – Use for TTS testing.
- **Output files**: JSON and SRT files like `voice_sample_english.json`, `voice_sample_english.srt` – Transcription results.

---

### Project Ideas

- Upload a Zoom recording, transcribe with OCI Speech, summarize with GenAI.
- Compare STT results between Oracle and Whisper models on mixed-language audio.
- Create an audio conversation: Generate transcript with GenAI, convert lines to audio with different voices, combine clips.
- Build a TTS chatbot that responds in multiple languages.

---

### Resources and Links

- **Documentation**:
  - [OCI Speech Home](https://docs.oracle.com/en-us/iaas/Content/speech/home.htm)
  - [STT Usage](https://docs.oracle.com/en-us/iaas/Content/speech/using/speech.htm)
  - [TTS Usage](https://docs.oracle.com/en-us/iaas/Content/speech/using/using-tts.htm)
  - [OCI Language API](https://docs.oracle.com/en-us/iaas/api/#/en/language/20221001/)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Project ideas and discussions.
  - **#igiu-ai-learning**: Help with sandbox environment or code issues.
  - **#oci_speech_service_users**: Questions about OCI Speech APIs.

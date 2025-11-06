## Welcome to the Speech Module

In this module you will experiment with Oracle Cloud Infrastructure (OCI) Speech services for **Text-to-Speech (TTS)** and **Speech-to-Text (STT)**.

### What you will try

1. **Text-to-Speech (TTS)** – Explore available voice models and the Speech Synthesis Markup Language (SSML) features supported by OCI.
2. **Speech-to-Text (STT)** – Use the batch transcription capability with both OCI Speech and Whisper models.

> **Note**  
> OCI Speech also supports real-time transcription, but that feature is not covered in this module.

---

### Working with STT

Audio files must be uploaded to an Object Storage bucket before they can be transcribed.

* Use the **PHX** tenancy for your bucket. The **Chicago** tenancy is a read-only replica.  
* Because you are working in a shared sandbox, use a unique **prefix** (analogous to a sub-folder), for example your Oracle ID.  
* Fill in the *bucket* section of **sandbox.config** with the details of your bucket (`NAMESPACE`, `BUCKET_NAME`, `FILE_NAME`, `PREFIX`).  
* Update the `DEFAULT_AUDIO_FILE` variable in the code so that it points to the local file you want to transcribe.

---

### Working with TTS

* Try the files with different languages 
* Experiment with different **SSML** tags to improve the quality of the synthesized speech.

---

### Environment setup

Ensure your **sandbox.yanl** and **.env** file is configured for your environment.  
This module uses the `oci` and `bucket` sections.

---

### Example code

Both Jupyter notebooks and equivalent Python scripts are provided:

| Task | Python Script | Notebook |
|------|---------------|----------|
| Upload an audio recording to Object Storage and transcribe it using oracle whisper models | `oci_speech_stt_oracle.py or oci_speech_stt_whisper ` | `oci_speech_stt.ipynb` |
| Convert text into speech and save the resulting audio file | `oci_speech_tts.py` | `oci_speech_tts.ipynb` |

Several sample audio files are included to get you started.  
Move them to the appropriate directory before running the code, or upload them manually to your bucket.

---

### Project ideas

* Upload a Zoom recording, transcribe it with OCI Speech, then summarize it with GenAI.  
* Transcribe content in different or mixed languages, and compare results between OCI Speech and Whisper models.  
* Create an audio conversation between two people:  
  1. Use GenAI to generate the transcript.  
  2. Use OCI Speech to convert each line to audio, selecting different voices for each speaker.  
  3. Combine the clips into a single audio file.

---

### Helpful links

* Slack **#igiu-innovation-lab** – project ideas  
* Slack **#igiu-ai-learning** – help with code or environment issues  
* Slack **#oci_speech_service_users** – questions about OCI Speech APIs  

Documentation: <https://docs.oracle.com/en-us/iaas/Content/speech/home.htm>

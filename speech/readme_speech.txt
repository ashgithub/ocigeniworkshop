
Welcome to the Speech Module. In this module, we will experiment with the OCI Speech's Text to Speech (TTS) & Speech to Text (STT) capability

Specifically, we will try the following capabilities:
1. Text to Speech: We will look at voice models & Speech markup language(SML) supported by the Aai 
2. Speech to Text: We will look at the the batch transcription capability using oci & wisper model. 

Note: Oracle Speech does support realtime voice transcription capability, but it is not covered in this module.

When using STT, we will be uploading the documents to an object bucket:
    - Please use the PHX tenancy to work with your object bucket. The Chicago tenancy is a read-only replica.
    - As you are working in a shared sandbox, use a unique prefix (prefix is analogous to a subfolder) (e.g., your Oracle ID).
    - Remember to  bucket section of sandbox.config details of your bucket (NAMESPACE, BUCKET_NAME, FILE_NAME, PREFIX)
    - Remember to update the FILE_TO_ANALYZE variable in code to the local file you want to analyze
When using TTS
    - remeber to update the filename variable to the path of teh file where you want the audio file to be stored 
    - Try adding different SAML tags to improve the quality of your response 

Remember to set up your sandbox.json file per your environment. This module  uses the "oci" & "bucket" section

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:

1. oci_speech_stt.py / stt.ipynb: upload audio recording to object bucket & transcribe it 
2. oci_speech_tts.py / tts.ipynb: transcribe a given audio recording 

    There are a few audio files ofr you to get started. Make sure to move them to the appropriate directory before you upload using code, or upload them manually to the correct bucket.

Here are some ideas of projects you can do (See notebook files for details):
    - Upload your video recoding from a zoom call, transcribe (Ai speech) & summarize it (Gen-AI)
    - try ranscription on different langaues, mixed langauges etc. Compafre oracle vs whisper models. 
    - Create a audio conversation between two people
        - Ask ai to generate the transcript (Gen AI)
        - use oci speech to convert reach dialog into audio, use different voice for each person
        - combine them into a single audio file

Here are few links to help you: 

#igiu-innovation-lab for project ideas
#igiu-ai-learning  for any issues with code or environment 
#oci_speech_service_users ofr quiestions on OCI speech APIs

https://docs.oracle.com/en-us/iaas/Content/speech/home.htm

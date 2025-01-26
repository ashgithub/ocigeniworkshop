#https://github.com/oracle/oci-python-sdk/tree/22fd62c8dbbd1aaed6b75754ec1ba8a3c16a4e5a/src/oci/ai_speech
#https://docs.oracle.com/en-us/iaas/Content/speech/home.htm
# oci_speech_service_users or #igiu-innovation-lab slack channel

# if you have errors running sample code reach out for help in #igiu-ai-learning

from oci.ai_speech import AIServiceSpeechClient
from oci.ai_speech.models import *
from oci.config import from_file
from oci.signer import load_private_key_from_file
import oci
import json, os
   
"""
configure these constant variables as per your use case
configurable values begin
"""
#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"
compartmentId= None # read from config 
endpoint = "https://speech.aiservice.us-phoenix-1.oci.oraclecloud.com"
  
# Replace filename with the file name to save the response
#filename = "brian_natural.mp3"
filename = "stacy_standard.mp3"
   
# The input text can be passed in an SSML format as well.
# You can enable SSML by selecting textType as TEXT_TYPE_SSML
# The link below has examples of supported SSML tags
# https://confluence.oci.oraclecorp.com/x/8Jcgvw
textType = TtsOracleSpeechSettings.TEXT_TYPE_TEXT
#textType = TtsOracleSpeechSettings.TEXT_TYPE_SSML
 
    
# the text for which you want to generate speech
#ssml tags: https://docs.oracle.com/en-us/iaas/Content/speech/using/using-tts.htm
text = "A paragraph is a series of sentences that are organized and coherent, and are all related to a single topic. Almost every piece of writing you do that is longer than a few sentences should be organized into paragraphs."
#text = """
#<speak>
#  <sub alias="see oh two over see oh">CO2/CO </sub>  is made up of molecules that each have one carbon atom  double bonded to two oxygen
#</speak>
#"""

# if you choose manutal voice here change the config in line 110 also 
#voiceId = "Brian"  # natural brian, annabell, Bob, Stacy, Cindy, Phil 
voiceId = "Stacy" # std voceis Bob, Stacy, Cindy, Phil
   


# If you want to enable streaming, set this value to true.
# With streaming, response is sent back in chunks.
# This means that you don't have to wait for entire speech to be generated before you can start using it.
isStreamEnabled = True
   
# Supported output formats
# - TtsOracleSpeechSettings.OUTPUT_FORMAT_PCM
# - TtsOracleSpeechSettings.OUTPUT_FORMAT_MP3
# - TtsOracleSpeechSettings.OUTPUT_FORMAT_JSON
# - TtsOracleSpeechSettings.OUTPUT_FORMAT_OGG
outputFormat = TtsOracleSpeechSettings.OUTPUT_FORMAT_MP3
  
   
# This is the sample rate of the generated speech.
sampleRateInHz = 22050
   
#  
# Specify speech mark types to obtain in case of Json output
# This field will be ignored if the output format is not Json
# The output json will contain all the speech mark types mentioned in the below list
speechMarkTypes = [TtsOracleSpeechSettings.SPEECH_MARK_TYPES_WORD, TtsOracleSpeechSettings.SPEECH_MARK_TYPES_SENTENCE]
   
"""
configurable values end
"""


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
       
def main():
    # get client for authentication and authorization
    client = get_client()
       
    # create payload object
    payload = get_payload()
   
    # handle response
    response = client.synthesize_speech(payload)
    if (response.status != 200):
        print(f'Request failed with {response.status}')
    else:
        save_response(response.data)
          
   
def get_client():
    global compartmentId
    #set up the oci gen ai client based on config 
    scfg = load_config(SANDBOX_CONFIG_FILE)
    config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])
    private_key = load_private_key_from_file(config['key_file'])
    compartmentId = scfg["oci"]["compartment"]

    return AIServiceSpeechClient(config=config,signer= oci.signer.Signer(
        tenancy=config["tenancy"],
        user=config["user"],
        fingerprint=config["fingerprint"],
        private_key_file_location=config["key_file"]
        ),
        service_endpoint=endpoint)
    
        
def get_payload():
    return SynthesizeSpeechDetails(
        text = text,
        is_stream_enabled=isStreamEnabled,
        compartment_id = compartmentId,
        configuration = TtsOracleConfiguration(
            model_details = TtsOracleTts1StandardModelDetails (
#            model_details = TtsOracleTts2NaturalModelDetails (    # swap with line above for natural voice 
                voice_id=voiceId
            ),
            speech_settings = TtsOracleSpeechSettings(
                text_type = textType,
                sample_rate_in_hz = sampleRateInHz,
                output_format = outputFormat,
                speech_mark_types = speechMarkTypes
            )
        )
    )
   
def save_response(data):
    if (isStreamEnabled and outputFormat == TtsOracleSpeechSettings.OUTPUT_FORMAT_PCM):
        streaming_save_as_wav(data)
    else:
        with open(filename, 'wb') as f:
            for b in data.iter_content():
                f.write(b)
    print (f"TTS files saved at {filename} in {os.getcwd()}")
   
def streaming_save_as_wav(data: bytes, filename: str = filename, buffer_size: int = 2048):
    HEADER_SIZE = 44
    assert buffer_size > HEADER_SIZE
    buffer, bytes_written = b'', 0
   
    f1 = open(filename, 'wb')
    f2 = open(filename, 'wb')
  
    with open(filename, 'wb') as f1, open(filename, 'wb') as f2:
  
        def update_wav_header():
            nonlocal buffer, f1, f2, bytes_written
              
            if len(buffer) >= buffer_size:
  
                f1.write(buffer)
                bytes_written += len(buffer)
                buffer = b''
  
                f2.seek(4, 0)
                f2.write((bytes_written - 8).to_bytes(4, 'little'))
                f2.seek(40, 0)
                f2.write((bytes_written - HEADER_SIZE).to_bytes(4, 'little'))
  
                f1.flush()
                f2.flush()
   
        for b in data.iter_content():
            buffer += b
            update_wav_header()
        update_wav_header()
   
   
if __name__ == '__main__':
    main()
from openai import OpenAI
from dotenv import load_dotenv
from envyaml import EnvYAML
from oci_openai import OciUserPrincipalAuth
import httpx


SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()
LLM_SERVICE_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1"

# Step 1: Load config and initialize client
def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: Create LLM client using credentials and optional parameters

client = OpenAI(
    base_url=LLM_SERVICE_ENDPOINT,
    api_key="OCI",
    project="ocid1.generativeaiproject.oc1.us-chicago-1.amaaaaaaghwivzaayhqtgla464kakelp3fwi6afhx5ca7l4h4k67rpnsesvq",
    http_client=httpx.Client(auth=OciUserPrincipalAuth(profile_name="INNOLAB-LEARNING")),
    default_headers={
                "opc-compartment-id": "ocid1.compartment.oc1..aaaaaaaaboqoghc43bbqvei5y4pmnzia36wuh7fpcxn6fia7pfyelyg4rj7a"
    }
)

response = client.responses.create(
    #model="openai.gpt-5.2",
    model="google.gemini-2.5-pro",
    input="What is 2x3?"
)


print(response.output_text) 

test_messages = [
        {
            "role": "user",
            "content": "what is paris"
        }
    ]
completion = client.chat.completions.create(
    #model="openai.gpt-5.2",
    model="google.gemini-2.5-pro",
    messages=test_messages
)
print(completion.model_dump_json(indent=2)) 
    
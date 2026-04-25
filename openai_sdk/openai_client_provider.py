""" 
This is a provider to fetch connections using the OCI methods and auth
In normal mode is required to have a valid OpenAI API Key and project id
For using this case, we only require project ID
The other auth methods follow the same OCI patterns to work
"""

import httpx
import logging
from envyaml import EnvYAML

from openai import OpenAI, AsyncOpenAI
from oci_genai_auth import OciUserPrincipalAuth
from agents import set_default_openai_api, set_default_openai_client
from dotenv import load_dotenv
load_dotenv()

DEFAULT_SANDBOX_CONFIG = "sandbox.yaml"
DEFAUL_OPENAI_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1"

class SandBoxConfigKeyNotSetException(Exception):
    """Raised when required config keys are missing."""

class OpenAIClientProvider:
    def __init__(self):
        self.config_path = DEFAULT_SANDBOX_CONFIG
        self.scfg = self.load_config(self.config_path)       
        
        # get the values from env variables
        self.oci_openai_endpoint = DEFAUL_OPENAI_ENDPOINT
        self.oci_openai_api_key = self.scfg['oci']['api_key']
        self.oci_openai_project = self.scfg['oci']['project']
        self.oci_compartment_id = self.scfg['oci']['compartment']
        self.oci_openai_profile = self.scfg['oci']['profile']
        
        #verify that the env is set correctly
        self._verify_required_config()

        # build the clients for responses and agent mode
        self.oci_openai_client = self.build_oci_openai_client()
        self.oci_openai_async_client = self.build_oci_openai_async_client()

    def load_config(self, config_path: str) -> EnvYAML | None:
        """Load configuration from a YAML file."""
        try:
            return EnvYAML(config_path)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            return None

    def _verify_required_config(self) -> None:
        missing: list[str] = []
        if not self.oci_openai_endpoint:
            missing.append("openai.service_endpoint")
        if not self.oci_compartment_id:
            missing.append("oci.compartment")
        if not self.oci_openai_project:
            missing.append("oci.project")

        if missing:
            raise SandBoxConfigKeyNotSetException(
                f"Missing required config keys in '{self.config_path}': {', '.join(missing)}"
            )

    # Helper for adding the necessary headers to make the sandbox connection
    def _default_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.oci_compartment_id:
            headers["opc-compartment-id"] = self.oci_compartment_id
            headers["CompartmentId"] = self.oci_compartment_id
        return headers

    # Client for responses.create use cases
    def build_oci_openai_client(self) -> OpenAI:
        client = OpenAI(
            base_url=self.oci_openai_endpoint,
            api_key=self.oci_openai_api_key,
            project=self.oci_openai_project,
            default_headers=self._default_headers(),
            http_client=httpx.Client(
                auth=OciUserPrincipalAuth(profile_name=self.oci_openai_profile)
            ),
        )

        return client

    # async client for agent set up mode
    def build_oci_openai_async_client(self) -> AsyncOpenAI:
        async_client = AsyncOpenAI(
            base_url=self.oci_openai_endpoint,
            api_key=self.oci_openai_api_key,
            project=self.oci_openai_project,
            default_headers=self._default_headers(),
            http_client=httpx.AsyncClient(
                auth=OciUserPrincipalAuth(profile_name=self.oci_openai_profile)
            ),
        )

        return async_client

    # Logger for debug, call as:
    # OpenAIClientProvider().get_logger 
    def get_logger(self):
        self.logger = logging.getLogger("openai")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())

        return self.logger
    
    # Call this method on the main function for each agent file.
    # Allows connections through OCI instead of native OpenAI clients
    def configure_agents_oci_env(self) -> AsyncOpenAI:
        set_default_openai_client(self.oci_openai_async_client, use_for_tracing=False)
        set_default_openai_api(self.oci_openai_api_key)
        return self.oci_openai_async_client

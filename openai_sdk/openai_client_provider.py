""" 
This is a provider to fetch connections using the OCI methods and auth
In normal mode is required to have a valid OpenAI API Key and project id
For using this case, we only require project ID
The other auth methods follow the same OCI patterns to work
"""

import httpx
import logging
import oracledb
from envyaml import EnvYAML

from openai import OpenAI, AsyncOpenAI
from oci_genai_auth import OciUserPrincipalAuth
from agents import set_default_openai_api, set_default_openai_client
from dotenv import load_dotenv
load_dotenv()

DEFAULT_SANDBOX_CONFIG = "sandbox.yaml"
DEFAUL_OPENAI_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1"
DEFAUL_OPENAI_VECTOR_ENDPOINT = "https://generativeai.us-chicago-1.oci.oraclecloud.com/20231130/openai/v1"
DEFAULT_OPENAI_SKILLS_ENDPOINT = "https://ppe.inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com/20231130/openai/v1"

class SandBoxConfigKeyNotSetException(Exception):
    """Raised when required config keys are missing."""

class OpenAIClientProvider:
    def __init__(self):
        self.config_path = DEFAULT_SANDBOX_CONFIG
        self.scfg = self.load_config(self.config_path)       
        
        # get the values from env variables
        self.oci_openai_endpoint = DEFAUL_OPENAI_ENDPOINT
        self.oci_openai_vector_endpoint = DEFAUL_OPENAI_VECTOR_ENDPOINT
        self.oci_openai_api_key = self.scfg['oci']['api_key']
        self.oci_openai_project = self.scfg['oci']['project']
        self.oci_compartment_id = self.scfg['oci']['compartment']
        self.oci_openai_profile = self.scfg['oci']['profile']
        self.oci_openai_config_file = self.scfg['oci']['configFile']
        self.oci_openai_vector_store_id = self.scfg['oci']['vector_store_id']
        
        #verify that the env is set correctly
        self._verify_required_config()

        # build the clients for responses and agent mode
        self.oci_openai_client = self.build_oci_openai_client()
        self.oci_openai_vector_client = self.build_oci_vector_crud_client()
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

    def get_sandbox_value(self, section: str, key: str, default: str | None = None) -> str | None:
        """Read a value from sandbox.yaml using section/key with an optional default."""
        if not self.scfg:
            return default
        section_data = self.scfg.get(section, {})
        if not isinstance(section_data, dict):
            return default
        value = section_data.get(key, default)
        return value

    # Helper for adding project headers to OpenAI-compatible API calls.
    def _default_headers(self) -> dict[str, str]:
        return {
            "OpenAI-Project": self.oci_openai_project,
            "opc-compartment-id": self.oci_compartment_id,
            "compartment-id": self.oci_compartment_id
        }

    # Client for responses.create use cases
    def build_oci_openai_client(self) -> OpenAI:
        client = OpenAI(
            base_url=self.oci_openai_endpoint,
            api_key=self.oci_openai_api_key,
            project=self.oci_openai_project,
            default_headers=self._default_headers(),
            http_client=httpx.Client(
                auth=OciUserPrincipalAuth(
                    config_file=self.oci_openai_config_file,
                    profile_name=self.oci_openai_profile,
                )
            ),
        )

        return client
    
    def build_oci_vector_crud_client(self) -> OpenAI:
        client = OpenAI(
            base_url=self.oci_openai_vector_endpoint,
            api_key=self.oci_openai_api_key,
            # project=self.oci_openai_project,
            default_headers=self._default_headers(),
            http_client=httpx.Client(
                auth=OciUserPrincipalAuth(
                    config_file=self.oci_openai_config_file,
                    profile_name=self.oci_openai_profile,
                )
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
                auth=OciUserPrincipalAuth(
                    config_file=self.oci_openai_config_file,
                    profile_name=self.oci_openai_profile,
                )
            ),
        )

        return async_client
    
    def connect_db(self) -> oracledb.Connection:
        db_config = self.scfg['db']
        wallet_path = self.scfg['db']['walletPath']

        return oracledb.connect(
            user=db_config["username"],
            password=db_config["password"],
            dsn=db_config["dsn"],
            config_dir=wallet_path,
            wallet_location=wallet_path,
            wallet_password=db_config["walletPass"],
        )

    def build_oci_generative_ai_control_plane_client(self, service_endpoint: str | None = None):
        """
        Build OCI Generative AI control-plane client for vector store connector APIs.
        Returns:
            tuple[oci.generative_ai.GenerativeAiClient, str]
            -> (client, compartment_id)
        """
        import oci

        config, signer = self._load_api_key_config_and_signer()
        compartment_id = self.oci_compartment_id
        region = config.get("region", "us-chicago-1")
        endpoint = service_endpoint or f"https://generativeai.{region}.oci.oraclecloud.com"

        client = oci.generative_ai.GenerativeAiClient(
            config=config,
            signer=signer,
            service_endpoint=endpoint,
        )
        return client, compartment_id

    def _load_api_key_config_and_signer(self):
        """Load OCI config and build an API-key signer from sandbox profile settings."""
        import oci

        profile = self.oci_openai_profile
        config = oci.config.from_file(self.oci_openai_config_file, profile_name=profile)
        required_keys = ["tenancy", "user", "fingerprint", "key_file"]
        missing = [key for key in required_keys if not config.get(key)]
        if missing:
            raise SandBoxConfigKeyNotSetException(
                "API-key OCI auth requires these config values in "
                f"{self.oci_openai_config_file} profile {profile}: {', '.join(missing)}"
            )

        signer = oci.signer.Signer(
            tenancy=config["tenancy"],
            user=config["user"],
            fingerprint=config["fingerprint"],
            private_key_file_location=config["key_file"],
            pass_phrase=config.get("pass_phrase"),
            private_key_content=config.get("key_content"),
        )
        return config, signer

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

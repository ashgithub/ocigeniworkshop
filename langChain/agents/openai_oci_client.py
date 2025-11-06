import httpx
from typing import (
    Iterator,
    Mapping,
)
from openai import DEFAULT_MAX_RETRIES, NOT_GIVEN, OpenAI, AsyncOpenAI,DefaultHttpxClient, DefaultAsyncHttpxClient,Timeout, NotGiven

# https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdk_authentication_methods.htm
import requests
import oci
from oci.config import DEFAULT_LOCATION, DEFAULT_PROFILE

class OciOpenAI(OpenAI):
    """
    A custom OpenAI client implementation for Oracle Cloud Infrastructure (OCI) Generative AI service.

    This class extends the OpenAI client to work with OCI's Generative AI service endpoints,
    handling authentication and request signing specific to OCI.

    Attributes:
        service_endpoint (str): The OCI service endpoint URL
        auth (httpx.Auth): Authentication handler for OCI
        compartment_id (str): OCI compartment ID for resource isolation
        timeout (float | Timeout | None | NotGiven): Request timeout configuration
        max_retries (int): Maximum number of retry attempts for failed requests
        default_headers (Mapping[str, str] | None): Default HTTP headers
        default_query (Mapping[str, object] | None): Default query parameters
    """
    def __init__(
            self,
            *,
            service_endpoint: str,
            auth: httpx.Auth,
            compartment_id: str,
            timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
            max_retries: int = DEFAULT_MAX_RETRIES,
            default_headers: Mapping[str, str] | None = None,
            default_query: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            api_key="<NOTUSED>",
            base_url=f"{service_endpoint}/20231130/actions/v1",
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=DefaultHttpxClient(
                auth=auth,
                headers={
                    "CompartmentId": compartment_id,
                },
            ),
        )

class AsyncOciOpenAI(AsyncOpenAI):
    def __init__(
            self,
            *,
            service_endpoint: str,
            auth: httpx.Auth,
            compartment_id: str,
            timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
            max_retries: int = DEFAULT_MAX_RETRIES,
            default_headers: Mapping[str, str] | None = None,
            default_query: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            api_key="<NOTUSED>",
            base_url=f"{service_endpoint}/20231130/actions/v1",
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=DefaultAsyncHttpxClient(
                auth=auth,
                headers={
                    "CompartmentId": compartment_id,
                },
            ),
        )

class HttpxOCIAuth(httpx.Auth):
    """
    Custom HTTPX authentication class that implements OCI request signing.

    This class handles the authentication flow for HTTPX requests by signing them
    using the OCI Signer, which adds the necessary authentication headers for OCI API calls.

    Attributes:
        signer (oci.signer.Signer): The OCI signer instance used for request signing
    """

    def __init__(self, signer):
        self.signer = signer

    def auth_flow(self, request: httpx.Request) -> Iterator[httpx.Request]:
        req = requests.Request(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            data=request.content,
        )
        prepared_request = req.prepare()

        # Sign the request using the OCI Signer
        self.signer.do_request_sign(prepared_request)

        # Update the original HTTPX request with the signed headers
        request.headers.update(prepared_request.headers)

        yield request


class OCISessionAuth(HttpxOCIAuth):
    """
    OCI authentication implementation using session-based authentication.

    This class implements OCI authentication using a session token and private key
    loaded from the OCI configuration file. It's suitable for interactive user sessions.

    Attributes:
        signer (oci.auth.signers.SecurityTokenSigner): OCI signer using session token
    """
    def __init__(self, config_file=DEFAULT_LOCATION, profile_name=DEFAULT_PROFILE):
        config = oci.config.from_file(config_file, profile_name)
        token = self._load_token(config)
        private_key = self._load_private_key(config)
        self.signer = oci.auth.signers.SecurityTokenSigner(token, private_key)

    def _load_token(self, config) -> str:
        token_file = config['security_token_file']
        with open(token_file, 'r') as f:
            return f.read().strip()

    def _load_private_key(self, config):
        return oci.signer.load_private_key_from_file(config['key_file'])


class OCIResourcePrincipleAuth(HttpxOCIAuth):
    """
    OCI authentication implementation using Resource Principal authentication.

    This class implements OCI authentication using Resource Principal credentials,
    which is suitable for services running within OCI that need to access other OCI services.
    """
    def __init__(self):
        self.signer = oci.auth.signers.get_resource_principals_signer()


class OCIInstancePrincipleAuth(HttpxOCIAuth):
    """
    OCI authentication implementation using Instance Principal authentication.

    This class implements OCI authentication using Instance Principal credentials,
    which is suitable for compute instances that need to access OCI services.
    """
    def __init__(self, **kwargs):
        self.signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner(**kwargs)


class OCIUserPrincipleAuth(HttpxOCIAuth):
    """
    OCI authentication implementation using user principle authentication.

        This class implements OCI authentication using API Key credentials loaded from
    the OCI configuration file. It's suitable for programmatic access to OCI services.

    Attributes:
        signer (oci.signer.Signer): OCI signer configured with API key credentials
    """
    def __init__(self, config_file=DEFAULT_LOCATION, profile_name=DEFAULT_PROFILE):
        config = oci.config.from_file(config_file, profile_name)
        oci.config.validate_config(config)

        self.signer = oci.signer.Signer(
            tenancy=config["tenancy"],
            user=config["user"],
            fingerprint=config["fingerprint"],
            private_key_file_location=config.get("key_file"),
            # pass_phrase is optional and can be None
            pass_phrase=oci.config.get_config_value_or_default(config, "pass_phrase"),
            # private_key_content is optional and can be None
            private_key_content=config.get("key_content")
        )

from langchain_openai.chat_models.base import ChatOpenAI
from pydantic import Field, model_validator
from typing_extensions import Self

class OciOpenAILangChainClient(ChatOpenAI):
    profile: str = Field(
        description="OCI profile name to use for authentication"
    )


    compartment_id: str = Field(
        description="OCI compartment ID where the model is deployed"
    )

    service_endpoint: str = Field(
        description="OCI Gen AI service endpoint to use"
    )

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Initialize OCI clients after validation."""
        if not self.client:
            self.client = OciOpenAI(
                service_endpoint=self.service_endpoint,
                auth=OCIUserPrincipleAuth(profile_name=self.profile),
                compartment_id=self.compartment_id
            ).chat.completions

        if not self.async_client:
            self.async_client = AsyncOciOpenAI(
                service_endpoint=self.service_endpoint,
                auth=OCIUserPrincipleAuth(profile_name=self.profile),
                compartment_id=self.compartment_id
            ).chat.completions
        return self

class OciOpenAILangGraphClient(ChatOpenAI):
    profile: str = Field(
        description="OCI profile name to use for authentication"
    )

    compartment_id: str = Field(
        description="OCI compartment ID where the model is deployed"
    )

    service_endpoint: str = Field(
        description="OCI Gen AI service endpoint to use"
    )
    
    def validate_environment(self) -> Self:
        """Initialize OCI clients after validation."""
        if not self.client:
            self.root_client = OciOpenAI(
                service_endpoint=self.service_endpoint,
                auth=OCIUserPrincipleAuth(profile_name=self.profile),
                compartment_id=self.compartment_id
            )
            self.client = self.root_client.chat.completions

        if not self.async_client:
            self.root_async_client = AsyncOciOpenAI(
                service_endpoint=self.service_endpoint,
                auth=OCIUserPrincipleAuth(profile_name=self.profile),
                compartment_id=self.compartment_id
            )
            self.async_client = self.root_async_client.chat.completions

        return self
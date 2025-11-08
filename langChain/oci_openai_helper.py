from envyaml import EnvYAML
from langchain_openai import ChatOpenAI
from oci_openai import OciUserPrincipalAuth, AsyncOciOpenAI
from pydantic import SecretStr
import httpx


class OCIOpenAIHelper:
    @staticmethod
    def get_client(model_name, config, **kwargs):
        """
        Returns a ChatOpenAI client initialized from OCI config YAML or env vars.

        Args:
            model_name (str): The model, e.g. "xai.grok-4-fast-reasoning"
            config  (EnvYAML):  OCI YAML config (sandbox.yaml or similar)
            **kwargs: Passed through to ChatOpenAI

        Returns:
            ChatOpenAI: Initialized with OCI config, model name and base_url
        """

        # OCI-compatible base URL—hardcoded per requirements
        base_url = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1"

        client = ChatOpenAI(
            model=model_name,
            api_key=SecretStr("OCI"),
            base_url=base_url,
            http_client=httpx.Client(
                auth=OciUserPrincipalAuth(profile_name=config['oci']['profile']),
                headers={"CompartmentId": config['oci']['compartment']}
            ),
            **kwargs
        )
        return client

    @staticmethod
    def get_async_native_client(config, **kwargs):
        """
        Returns a ChatOpenAI client initialized from OCI config YAML or env vars.

        Args:
            model_name (str): The model, e.g. "xai.grok-4-fast-reasoning"
            config  (EnvYAML):  OCI YAML config (sandbox.yaml or similar)
            **kwargs: Passed through to ChatOpenAI

        Returns:
            ChatOpenAI: Initialized with OCI config, model name and base_url
        """

        # OCI-compatible base URL—hardcoded per requirements
        service_endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

        client = AsyncOciOpenAI(
            
            service_endpoint=service_endpoint,
            auth=OciUserPrincipalAuth(profile_name=config['oci']['profile']),
            compartment_id=config['oci']['compartment'],
            **kwargs
        )
        
        return client
    
    
##### test ######
if __name__ == "__main__":
    from dotenv import load_dotenv
    from envyaml import EnvYAML
    load_dotenv()
    SANDBOX_CONFIG_FILE = "sandbox.yaml"

    def load_config(config_path):
        """Load configuration from a YAML file."""
        try:
            with open(config_path, 'r') as f:
                return EnvYAML(config_path)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            return None
        
    messages = [
        (
            "system",
            "You are a helpful assistant that translates English to French. Translate the user sentence.",
        ),
        ("human", "I love programming."),
    ]

    llm = OCIOpenAIHelper.get_client(model_name="openai.gpt-5", config=load_config(SANDBOX_CONFIG_FILE), reasoning={
            "effort": "low",
            "summary": "auto"
        },
        # use_responses_api=True
        # stream_usage=True,
        # temperature=None,
        # max_tokens=None,
        # timeout=None,
        # reasoning_effort="low",
        # max_retries=2,
        # other params...                                  
        )
    #ai_msg = llm.invoke(messages)
    #print(ai_msg)

    # Async example
    import asyncio

    async def test_async_chat():
        test_messages=[
            {
                "role": "user",
                "content": "How do I output all files in a directory using Python?"
            }
        ]
        #async_llm = OCIOpenAIHelper.get_async_native_client(config=load_config(SANDBOX_CONFIG_FILE))
        #ai_async_msg = await async_llm.chat.completions.create(model="xai.grok-4",messages=test_messages)
        llm = OCIOpenAIHelper.get_client(model_name="openai.gpt-5", config=load_config(SANDBOX_CONFIG_FILE),use_responses_api=True) 
        ai_async_msg = await  llm.ainvoke(test_messages)
        print("Async output:", ai_async_msg)

    asyncio.run(test_async_chat())

from envyaml import EnvYAML
from langchain_oci import ChatOCIOpenAI,ChatOCIGenAI
from langchain_openai import ChatOpenAI
from oci_openai import OciOpenAI, AsyncOciOpenAI
from oci_openai import OciUserPrincipalAuth
import httpx
import asyncio
from openai import OpenAI, AsyncOpenAI
from typing import Any, Dict, List
from openai.types.chat import ChatCompletionMessageParam
from langchain_core.messages import HumanMessage

"""
OCIOpenAIHelper: Utility class for initializing OpenAI-compatible clients with OCI Generative AI authentication.

This module provides static methods to create various client types for interacting with OCI's Generative AI services:

- LangChain ChatOCIOpenAI and ChatOpenAI clients for LangChain integrations
- Direct OCI OpenAI (OciOpenAI, AsyncOciOpenAI) clients for low-level API access
- Direct OpenAI (OpenAI, AsyncOpenAI) clients configured for OCI endpoints

All clients are automatically configured with OCI user principal authentication and compartment headers.

Documentation to reference:
- Oracle LangChain OCI Examples: https://github.com/oracle/langchain-oracle/tree/main/libs/oci/examples
- OCI OpenAI SDK Examples: https://github.com/oracle-samples/oci-openai/tree/main/examples
- LangChain OpenAI Responses API: https://docs.langchain.com/oss/python/integrations/chat/openai#responses-api

Env setup:
- sandbox.yaml: OCI configuration file containing profile name and compartment OCID
- Ensure OCI CLI is configured with user principal authentication
"""

class OCIOpenAIHelper:
  
    @staticmethod 
    def get_langchain_ocigenai_client(model_name, config, store=False, **kwargs):
        region = "us-chicago-1"

        client = ChatOCIGenAI(
            
            model_id=model_name,
            service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
            auth_profile=config['oci']['profile'],
            compartment_id= config['oci']['compartment'],
            model_kwargs={
              "modalities": ["text", "audio"],
              "audio": {"voice": "alloy", "format": "wav"},
            },
            
            **kwargs
        )
        return client
     
    
    @staticmethod
    def get_langchain_ociopenai_client(model_name, config, store=False, **kwargs):
        """
        Create a LangChain ChatOCIOpenAI client for OCI Generative AI.

        Initializes a ChatOCIOpenAI client with OCI authentication for use in LangChain chains and agents.

        Args:
            model_name (str): Model identifier, e.g., "openai.gpt-4.1" or "meta.llama-3.1-70b-instruct"
            config (EnvYAML): Configuration object loaded from YAML, must contain 'oci' section with 'profile' and 'compartment' keys
            store (bool, optional): Whether to store conversations. Defaults to False.
            **kwargs: Additional keyword arguments passed to ChatOCIOpenAI constructor (e.g., temperature, max_tokens)

        Returns:
            ChatOCIOpenAI: Configured LangChain-compatible client

        Notes:
            Uses OCI user principal authentication. Ensure OCI CLI is configured.
        """

        # OCI-compatible base URL—hardcoded per requirements
       # base_url = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1"
        region = "us-chicago-1"

        client = ChatOCIOpenAI(
            model=model_name,
            region=region,
            auth=OciUserPrincipalAuth(profile_name=config['oci']['profile']),
            compartment_id= config['oci']['compartment'],
            store=store,
            **kwargs
        )
        return client
    
   

    @staticmethod
    def get_langchain_openai_client(model_name, config, store=False, **kwargs):
        """
        Create a LangChain ChatOpenAI client configured for OCI Generative AI endpoints.

        Initializes a ChatOpenAI client pointing to OCI's OpenAI-compatible API endpoints with authentication.

        Args:
            model_name (str): Model identifier, e.g., "openai.gpt-4.1"
            config (EnvYAML): Configuration object with OCI settings
            **kwargs: Additional arguments for ChatOpenAI (supports use_responses_api=True for responses API)

        Returns:
            ChatOpenAI: LangChain client configured for OCI

        Notes:
            Uses httpx client with OCI authentication. Model is specified per call or via model_name.
        """

        # OCI-compatible base URL—hardcoded per requirements
       # base_url = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1"
        region = "us-chicago-1"

        client = ChatOpenAI(
            base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1",
            #base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1",

            api_key=config['oci']['api_key'],
            model=model_name,
            store = False,
            **kwargs
        )
        return client
    
   
   
    @staticmethod
    def get_sync_ociopenai_client(config, store=False, **kwargs):
        """
        Create a synchronous OCI OpenAI client.

        Returns a direct OciOpenAI client for making API calls without LangChain wrapper.

        Args:
            config (EnvYAML): OCI configuration
            store (bool, optional): Whether to store conversations. Defaults to False.
            **kwargs: Additional arguments for OciOpenAI

        Returns:
            OciOpenAI: Synchronous client for chat completions and responses

        Notes:
            Model is specified per API call, not in client initialization.
        """


        client = OciOpenAI(
            auth=OciUserPrincipalAuth(profile_name=config['oci']['profile']),
            compartment_id=config['oci']['compartment'],
            conversation_store_id= config['oci']['conversation_store'],  # conversation stored to be used
            region="us-chicago-1",
            store=store,
            **kwargs
        )
        return client 

    @staticmethod
    def get_async_ociopenai_client(config, store=False, **kwargs):
        """
        Create an asynchronous OCI OpenAI client.

        Returns a direct AsyncOciOpenAI client for making async API calls without LangChain wrapper.

        Args:
            config (EnvYAML): OCI configuration
            store (bool, optional): Whether to store conversations. Defaults to False.
            **kwargs: Additional arguments for AsyncOciOpenAI

        Returns:
            AsyncOciOpenAI: Asynchronous client for chat completions and responses

        Notes:
            Model is specified per API call, not in client initialization.
        """


        client = AsyncOciOpenAI(
            auth=OciUserPrincipalAuth(profile_name=config['oci']['profile']),
            compartment_id=config['oci']['compartment'],
            conversation_store_id= config['oci']['conversation_store'],  # conversation stored to be used
            region="us-chicago-1",
            store=store,
            **kwargs
        )
        return client 
           
    @staticmethod
    def get_sync_openai_client(config, store=False, **kwargs):
        """
        Create a synchronous OpenAI client configured for OCI endpoints.

        Returns a direct OpenAI client pointing to OCI's OpenAI-compatible API.

        Args:
            config (EnvYAML): OCI configuration
            store (bool, optional): Whether to store conversations. Defaults to False.
            **kwargs: Additional arguments for OpenAI

        Returns:
            OpenAI: Synchronous client for chat completions and responses

        Notes:
            Uses httpx client with OCI authentication. Model specified per API call.
        """
        client = OpenAI(
            base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1",
            api_key="not-used",  # type: ignore
            #store = store, need to specify per request
            http_client=httpx.Client(auth=OciUserPrincipalAuth(profile_name=config['oci']['profile'])),  # or OciResourcePrincipalAuth | OciInstancePrincipalAuth | OciUserPrincipalAuth,
                default_headers={
                "opc-compartment-id": config['oci']['compartment'],  # a compartment of your tenancy that this caller identity has access to 
                "opc-conversation-store-id": config['oci']['conversation_store']  # conversation stored to be used 
                }
            )

        return client 

    @staticmethod
    def get_async_openai_client(config, store=False, **kwargs):
        """
        Create an asynchronous OpenAI client configured for OCI endpoints.

        Returns a direct AsyncOpenAI client pointing to OCI's OpenAI-compatible API.

        Args:
            config (EnvYAML): OCI configuration
            store (bool, optional): Whether to store conversations. Defaults to False.
            **kwargs: Additional arguments for AsyncOpenAI

        Returns:
            AsyncOpenAI: Asynchronous client for chat completions and responses

        Notes:
            Uses httpx AsyncClient with OCI authentication. Model specified per API call.
        """
        client = AsyncOpenAI(
            base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1",
            api_key="not-used",  # type: ignore
        #    store=store,    # need to specify per request
            http_client=httpx.AsyncClient(auth=OciUserPrincipalAuth(profile_name=config['oci']['profile'])),  # or OciResourcePrincipalAuth | OciInstancePrincipalAuth | OciUserPrincipalAuth,
                default_headers={
                "opc-compartment-id": config['oci']['compartment'],  # a compartment of your tenancy that this caller identity has access to 
                "opc-conversation-store-id": config['oci']['conversation_store'] # conversation stored to be used 
                }
            )

        return client  
   
    @staticmethod
    def get_sync_openai_key_client(config, store=False, **kwargs):
        """
        Create a synchronous OpenAI client configured for OCI endpoints.

        Returns a direct OpenAI client pointing to OCI's OpenAI-compatible API.

        Args:
            config (EnvYAML): OCI configuration
            store (bool, optional): Whether to store conversations. Defaults to False.
            **kwargs: Additional arguments for OpenAI

        Returns:
            OpenAI: Synchronous client for chat completions and responses

        Notes:
            Uses httpx client with OCI authentication. Model specified per API call.
        """
        client = OpenAI(
            base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1",
            #base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1",
            api_key=config['oci']['api_key']
            )

        return client 

    @staticmethod
    def get_async_openai_key_client(config, store=False, **kwargs):
        """
        Create a asynchronous OpenAI client configured for OCI endpoints.

        Returns a direct OpenAI client pointing to OCI's OpenAI-compatible API.

        Args:
            config (EnvYAML): OCI configuration
            store (bool, optional): Whether to store conversations. Defaults to False.
            **kwargs: Additional arguments for OpenAI

        Returns:
            OpenAI: Synchronous client for chat completions and responses

        Notes:
            Uses httpx client with OCI authentication. Model specified per API call.
        """
        client = AsyncOpenAI(
            base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1",
            #base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1",
            api_key=config['oci']['api_key']
            )

        return client 
     

##### test ######


def test_langchain_ocigenai_audio(model_name="openai.gpt-audio", question="who are you ? answer in one sentence"):
    print("############################################################")
    print(f"# Testing LangChain OCIGenAi Audio Chat: {model_name}")
    print("############################################################")
    test_messages = [HumanMessage(content=question)]
    sync_llm = OCIOpenAIHelper.get_langchain_ociopenai_client(model_name=model_name,config=load_config(SANDBOX_CONFIG_FILE))
    sync_msg = sync_llm.invoke(test_messages)
    print("sync responses output:", sync_msg.model_dump_json(indent=2))
    

def test_langchain_ocigenai_sync_chat(model_name="google.gemini-2.5-flash-lite", question="who are you ? answer in one sentence"):
    print("############################################################")
    print(f"# Testing LangChain OCIGenAI Sync Chat: {model_name}")
    print("############################################################")
    test_messages = [HumanMessage(content=question)]
    sync_llm = OCIOpenAIHelper.get_langchain_ocigenai_client(model_name=model_name,config=load_config(SANDBOX_CONFIG_FILE),provider="generic")
    sync_msg = sync_llm.invoke(test_messages)
    print("sync responses output:", sync_msg.model_dump_json(indent=2))
    

def test_langchain_ociopenai_sync_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing LangChain OCI OpenAI Sync Chat")
    print("############################################################")
    print("not possible using oci client. as responses is hard coded to be true")
   
def test_langchain_ociopenai_sync_responses(model_name="openai.gpt-4.1",question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing LangChain OCI OpenAI Sync Responses")
    print("############################################################")
    test_messages = [HumanMessage(content=question)]
    sync_llm = OCIOpenAIHelper.get_langchain_ociopenai_client(model_name=model_name,config=load_config(SANDBOX_CONFIG_FILE))
    sync_msg = sync_llm.invoke(test_messages)
    print("sync responses output:", sync_msg.model_dump_json(indent=2))

def test_langchain_openai_sync_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing LangChain OpenAI Sync Chat")
    print("############################################################")
    test_messages = [HumanMessage(content=question)]
    sync_llm = OCIOpenAIHelper.get_langchain_openai_client(model_name=model_name,config=load_config(SANDBOX_CONFIG_FILE))
    sync_msg = sync_llm.invoke(test_messages)
    print("sync chat completion output:", sync_msg.model_dump_json(indent=2))
    
    
   
def test_langchain_openai_sync_responses(model_name="openai.gpt-4.1",question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing LangChain Openai Sync Responses")
    print("############################################################")
    test_messages = [HumanMessage(content=question)]
    sync_llm = OCIOpenAIHelper.get_langchain_openai_client(model_name=model_name,config=load_config(SANDBOX_CONFIG_FILE), use_responses_api=True)
    sync_msg = sync_llm.invoke(test_messages)
    print("sync responses output:", sync_msg.model_dump_json(indent=2))
    
def test_ociopenai_sync_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OCI OpenAI Sync Chat")
    print("############################################################")
    test_messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": question
        }
    ]
        
    llm = OCIOpenAIHelper.get_sync_ociopenai_client(config=load_config(SANDBOX_CONFIG_FILE)) 
    completion = llm.chat.completions.create(
       model=model_name,
       messages=test_messages 
    )
    
    print(completion.model_dump_json(indent=2)) 

def test_ociopenai_sync_responses(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OCI OpenAI Sync Responses")
    print("############################################################")
        
    llm = OCIOpenAIHelper.get_sync_ociopenai_client(config=load_config(SANDBOX_CONFIG_FILE)) 
    response = llm.responses.create(
       model=model_name,
       input=question,
       store=False
    )
    
    print(response.model_dump_json(indent=2)) 

def test_openai_sync_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OpenAI Sync Chat")
    print("############################################################")
    test_messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": question
        }
    ]
        
    llm = OCIOpenAIHelper.get_sync_openai_client(config=load_config(SANDBOX_CONFIG_FILE)) 
    completion = llm.chat.completions.create(
       model=model_name,
       messages=test_messages 
    )
    
    print(completion.model_dump_json(indent=2)) 

def test_openai_key_sync_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OpenAI Sync Chat using key")
    print("############################################################")
    test_messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": question
        }
    ]
        
    llm = OCIOpenAIHelper.get_sync_openai_key_client(config=load_config(SANDBOX_CONFIG_FILE)) 
    completion = llm.chat.completions.create(
       model=model_name,
       messages=test_messages 
    )
    
    print(completion.model_dump_json(indent=2)) 
    
def test_openai_sync_responses(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OpenAI Sync Responses")
    print("############################################################")
        
    llm = OCIOpenAIHelper.get_sync_openai_client(config=load_config(SANDBOX_CONFIG_FILE)) 
    response = llm.responses.create(
       model=model_name,
       input=question,
       store=False
    )
    
    print(response.model_dump_json(indent=2)) 

def test_openai_key_sync_responses(model_name="openai.gpt-5.2", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OpenAI Sync Responses using key")
    print("############################################################")
        
    llm = OCIOpenAIHelper.get_sync_openai_key_client(config=load_config(SANDBOX_CONFIG_FILE)) 
    response = llm.responses.create(
       model=model_name,
       input=question,
       store=False
    )
    
    print(response.model_dump_json(indent=2)) 
        

async def test_langchain_ociopenai_async_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing LangChain OCI OpenAI Async Chat")
    print("############################################################")
    print("not possible using oci client. as responses is hard coded to be true")
   
async def test_langchain_ociopenai_async_responses(model_name="openai.gpt-4.1",question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing LangChain OCI OpenAI Async Responses")
    print("############################################################")
    test_messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": question
        }
    ]
    async_llm = OCIOpenAIHelper.get_langchain_ociopenai_client(model_name=model_name,config=load_config(SANDBOX_CONFIG_FILE))
    async_msg = await async_llm.ainvoke(test_messages)
    print("async responses output:", async_msg.model_dump_json(indent=2))

async def test_langchain_openai_async_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing LangChain OpenAI Async Chat")
    print("############################################################")
    test_messages = [HumanMessage(content=question)]
    async_llm = OCIOpenAIHelper.get_langchain_openai_client(model_name=model_name,config=load_config(SANDBOX_CONFIG_FILE))
    async_msg = await async_llm.ainvoke(test_messages)
    print("async chat completion output:", async_msg.model_dump_json(indent=2))
    
    
   
async def test_langchain_openai_async_responses(model_name="openai.gpt-4.1",question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing LangChain Openai Async Responses")
    print("############################################################")
    test_messages = [HumanMessage(content=question)]
    async_llm = OCIOpenAIHelper.get_langchain_openai_client(model_name=model_name,config=load_config(SANDBOX_CONFIG_FILE), use_responses_api=True)
    async_msg = await async_llm.ainvoke(test_messages)
    print("async responses output:", async_msg.model_dump_json(indent=2))
    
async def test_ociopenai_async_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OCI OpenAI Async Chat")
    print("############################################################")
    test_messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": question
        }
    ]
        
    llm = OCIOpenAIHelper.get_async_ociopenai_client(config=load_config(SANDBOX_CONFIG_FILE),store=False) 
    completion = await llm.chat.completions.create(
       model=model_name,
       messages=test_messages 
    )
    
    print(completion.model_dump_json(indent=2)) 

async def test_ociopenai_async_responses(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OCI OpenAI Async Responses")
    print("############################################################")
        
    llm = OCIOpenAIHelper.get_async_ociopenai_client(config=load_config(SANDBOX_CONFIG_FILE),store=False) 
    response = await llm.responses.create(
       model=model_name,
       input=question,
       store=False
    )
    
    print(response.model_dump_json(indent=2)) 

async def test_openai_async_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OpenAI Async Chat")
    print("############################################################")
    test_messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": question
        }
    ]
        
    llm = OCIOpenAIHelper.get_async_openai_client(config=load_config(SANDBOX_CONFIG_FILE),store=False) 
    completion = await llm.chat.completions.create(
       model=model_name,
       messages=test_messages 
    )
    
    print(completion.model_dump_json(indent=2)) 

async def test_openai_async_responses(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OpenAI Async Responses")
    print("############################################################")
        
    llm = OCIOpenAIHelper.get_async_openai_client(config=load_config(SANDBOX_CONFIG_FILE),store=False) 
    response = await llm.responses.create(
       model=model_name,
       input=question,
#       store=False
    )
    
    print(response.model_dump_json(indent=2)) 
    

async def test_openai_key_async_chat(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OpenAI Async Chat")
    print("############################################################")
    test_messages: List[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": question
        }
    ]
        
    llm = OCIOpenAIHelper.get_async_openai_key_client(config=load_config(SANDBOX_CONFIG_FILE),store=False) 
    completion = await llm.chat.completions.create(
       model=model_name,
       messages=test_messages 
    )
    
    print(completion.model_dump_json(indent=2)) 

async def test_openai_key_async_responses(model_name="openai.gpt-4.1", question="who are you ? answer in one sentence"):
    print("############################################################")
    print("# Testing OpenAI Async Responses")
    print("############################################################")
        
    llm = OCIOpenAIHelper.get_async_openai_key_client(config=load_config(SANDBOX_CONFIG_FILE),store=False) 
    response = await llm.responses.create(
       model=model_name,
       input=question,
#       store=False
    )
    
    print(response.model_dump_json(indent=2)) 
        
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

    #test_langchain_ocigenai_sync_chat(model_name="google.gemini-2.5-flash-lite", question="where is paris? ")
    test_langchain_ocigenai_audio(model_name="openai.gpt-audio", question="where is paris? ") 
    
    
#    test_langchain_ociopenai_sync_chat(model_name="openai.gpt-4.1",question="where is paris?")
#    test_langchain_ociopenai_sync_responses(model_name="openai.gpt-4.1", question="where is paris? ")

#    test_langchain_openai_sync_chat(model_name="openai.gpt-4.1",question="where is paris?")
#    test_langchain_openai_sync_responses(model_name="openai.gpt-4.1", question="where is paris? ")

#    test_ociopenai_sync_chat(model_name="openai.gpt-4.1", question="where is paris? ")
#    test_ociopenai_sync_responses(model_name="openai.gpt-4.1", question="where is paris? ")

#    test_openai_sync_chat(model_name="openai.gpt-4.1", question="where is paris? ")
#    test_openai_sync_responses(model_name="openai.gpt-4.1", question="where is paris? ")
#    test_openai_key_sync_chat(model_name="openai.gpt-4.1", question="where is paris? ")
#    test_openai_key_sync_responses(model_name="openai.gpt-5.2", question="where is paris? ")

#    asyncio.run(test_langchain_ociopenai_async_chat())
#    asyncio.run(test_langchain_ociopenai_async_responses())
#    asyncio.run(test_langchain_openai_async_chat())
#    asyncio.run(test_langchain_openai_async_responses())
#    asyncio.run(test_ociopenai_async_chat())
#    asyncio.run(test_ociopenai_async_responses())
#    asyncio.run(test_openai_async_chat())
#    asyncio.run(test_openai_async_responses())
#    asyncio.run(test_openai_key_async_chat())
#    asyncio.run(test_openai_key_async_responses())

"""
What this file does:
Demonstrates using OCI Generative AI Agent Runtime service for out-of-the-box RAG functionality with a shared knowledge base and citations.

Documentation to reference:
- OCI GenAI Agents: https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/home.htm 
- Agent Runtime API: https://docs.oracle.com/en-us/iaas/api/#/en/generative-ai-agent-runtime/20240531/
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_agent_runtime

Relevant slack channels:
- #generative-ai-agent-users: For OCI Agents questions
- #igiu-innovation-lab: Project discussions
- #igiu-ai-learning: Environment/code help

Env setup:
- sandbox.yaml: Ensure "oci" and "agent" sections (configFile, profile, compartment, endpoint, session/no_session_endpoint, session flag).
- .env: Load environment variables if needed.
- Knowledge base: Upload docs via OCI console (see rag_agents.md for setup).

How to run the file:
uv run rag/oci_rag_agents.py

Comments to important sections of file:
- Step 1: Load config and set up agent client.
- Step 2: Create session if enabled, or use sessionless endpoint.
- Step 3: Interactive chat loop with agent, handling citations.
- Experiment: Switch session mode, add custom preamble, try domain-specific queries, compare session vs sessionless.
"""

from dotenv import load_dotenv
from envyaml import EnvYAML

# Step 1: Import dependencies and define constants
from oci.generative_ai_agent_runtime import GenerativeAiAgentRuntimeClient
import oci
import os

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

AGENT_ENDPOINT = "https://agent-runtime.generativeai.us-chicago-1.oci.oraclecloud.com"

# Step 2: Load config and set up agent client
def load_configuration(config_file_path):
    """Load sandbox config."""
    try:
        return EnvYAML(config_file_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file_path}' not found.")
        return None

sandbox_config = load_configuration(SANDBOX_CONFIG_FILE)
if sandbox_config is None:
    raise RuntimeError("Failed to load sandbox configuration.")

oci_config = oci.config.from_file(
    os.path.expanduser(sandbox_config["oci"]["configFile"]), 
    sandbox_config["oci"]["profile"]
)

agent_client = GenerativeAiAgentRuntimeClient(
    config=oci_config,
    service_endpoint=AGENT_ENDPOINT,
    retry_strategy=oci.retry.NoneRetryStrategy(),
    timeout=(10, 240)
)

# Determine endpoint and session
use_session = sandbox_config.get("agent", {}).get("session", False)
if use_session:
    endpoint = sandbox_config["agent"]["endpoint"]
    session_id = None  # Will create below
else:
    endpoint = sandbox_config["agent"]["no_session_endpoint"]
    session_id = None

def perform_inference(message, session_id, endpoint, preamble=""):
    """Send chat request to agent."""
    chat_details = oci.generative_ai_agent_runtime.models.ChatDetails()
    chat_details.user_message = preamble + " " + message
    chat_details.session_id = session_id
    chat_response = agent_client.chat(endpoint, chat_details)
    return chat_response.data.message.content

# Step 3: Create session if enabled and start chat loop
if use_session:
    session_details = oci.generative_ai_agent_runtime.models.CreateSessionDetails(
        display_name="Inno Lab C2M Agent",
        description="The agent has access to C2M documentation and can answer questions on it."
    )
    session_response = agent_client.create_session(session_details, endpoint)
    session_id = session_response.data.id
    print(f"Created session: {session_id}")

# Interactive chat
while True:
    user_query = input("\n\nAsk a question (or 'q' to exit): ").strip().lower()
    if user_query == "q":
        break

    preamble = "You are an expert on Oracle's C2M. Answer questions professionally and factually. If you don't know, say so. Always quote the source from your knowledge base."
    response = perform_inference(user_query, session_id, endpoint, preamble)

    print("****** Citations ******")
    print(response.citations)
    print("****** Answer ******")
    print(response.text)

# Sample questions for testing:
# - How often do I need to service the battery?
# - When should oil be replaced in recloser?
# - What is the accepted CO2 in DGA?

# Experiment suggestions:
# 1. Change use_session in sandbox.yaml to True/False and compare persistence.
# 2. Modify preamble for different response styles (e.g., add humor or strictness).
# 3. Try queries outside the knowledge base to see how it handles unknowns.
# 4. Upload new docs to knowledge base and test new topics.
# 5. Adjust endpoint in sandbox.yaml for different agents.

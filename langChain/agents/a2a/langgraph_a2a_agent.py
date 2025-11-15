"""
What this file does:
Main host agent that performs A2A calls to specialized agents based on user needs. This agent dynamically discovers available agents from a registry and intelligently routes user queries to the most appropriate specialized agents.

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai  note: supports OpenAI, XAI & Meta models. Also supports OpenAI Responses API
- LangGraph: https://langchain-ai.github.io/langgraph/

Relevant slack channels:
 - #generative-ai-users: for questions on OCI Gen AI
 - #igiu-innovation-lab: general discussions on your project
 - #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/agents/a2a/langgraph_a2a_agent.py

Comments to important sections of file:
- Step 1: Registry interaction module for dynamic agent discovery
- Step 2: System prompt builder module for intelligent agent routing
- Step 3: Tool creation module for A2A agent calls
- Step 4: LangGraph agent builder module for async tool support
- Step 5: Main agent class orchestration
- Step 6: Main execution and demonstration
"""

from langchain_core.tools import tool
from remote_agent_connections import call_a2a_agent

import sys
import os
import httpx
import asyncio

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import SystemMessage, ToolMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END

from dotenv import load_dotenv
from envyaml import EnvYAML
from typing import Any, List, Dict

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oci_openai_helper import OCIOpenAIHelper

# Registry configuration
REGISTRY_URL = "http://localhost:9990"


# ============================================================================
# STEP 1: REGISTRY INTERACTION MODULE
# ============================================================================
# This module handles fetching agent information from the registry

async def fetch_agent_registry(registry_url: str = REGISTRY_URL) -> List[Dict]:
    """
    Fetch the list of available agents from the registry.
    
    Args:
        registry_url: URL of the agent registry server
        
    Returns:
        List of agent dictionaries containing agent cards
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{registry_url}/registry/agents")
            response.raise_for_status()
            agents = response.json()
            
            print(f"✓ Successfully fetched {len(agents)} agents from registry")
            return agents
            
    except Exception as e:
        print(f"✗ Warning: Could not fetch registry: {e}")
        print("  Make sure the registry is running on port 9990.")
        return []


# ============================================================================
# STEP 2: SYSTEM PROMPT BUILDER MODULE
# ============================================================================
# This module builds a rich system prompt from agent card information

def build_agent_description(agent: Dict) -> str:
    """
    Build a detailed description for a single agent from its agent card.
    
    Args:
        agent: Agent card dictionary with name, skills, description, etc.
        
    Returns:
        Formatted string describing the agent's capabilities
    """
    # Step 2.1: Start with agent name and version
    agent_info = [f"\n  • {agent['name']} (v{agent.get('version', '1.0.0')})"]
    
    # Step 2.2: Add high-level description
    description = agent.get('description', 'No description available')
    agent_info.append(f"    Description: {description}")
    
    # Step 2.3: Extract and format skills information
    skills = agent.get('skills', [])
    if skills:
        agent_info.append(f"    Skills:")
        for skill in skills:
            # Skill name and description
            skill_name = skill.get('name', 'Unknown')
            skill_desc = skill.get('description', 'No description')
            agent_info.append(f"      - {skill_name}: {skill_desc}")
            
            # Step 2.4: Add tags (help with semantic matching)
            tags = skill.get('tags', [])
            if tags:
                agent_info.append(f"        Tags: {', '.join(tags)}")
            
            # Step 2.5: Add example queries (help LLM understand usage)
            examples = skill.get('examples', [])
            if examples:
                # Limit to first 3 examples to save tokens
                example_text = ', '.join(examples[:3])
                agent_info.append(f"        Examples: {example_text}")
    
    # Step 2.6: Add capabilities (like streaming support)
    capabilities = agent.get('capabilities', {})
    if capabilities:
        cap_list = []
        if capabilities.get('streaming'):
            cap_list.append('streaming')
        if cap_list:
            agent_info.append(f"    Capabilities: {', '.join(cap_list)}")
    
    return "\n".join(agent_info)


def build_system_prompt_with_agents(registry_agents: List[Dict]) -> str:
    """
    Build a comprehensive system prompt that includes all agent information.
    
    Args:
        registry_agents: List of agent cards from the registry
        
    Returns:
        Complete system prompt string with agent details and instructions
    """
    # Step 2.7: Handle case where no agents are available
    if not registry_agents:
        agent_list = "No agents currently available in the registry."
    else:
        # Step 2.8: Build detailed description for each agent
        agent_descriptions = [build_agent_description(agent) for agent in registry_agents]
        agent_list = "\n".join(agent_descriptions)

    # Step 2.9: Construct the full system prompt
    return f"""You are a helpful assistant with access to specialized A2A agents.

AVAILABLE AGENTS:
{agent_list}

INSTRUCTIONS:
- Use the call_agent tool to delegate tasks to the appropriate specialized agent
- Review the agent's skills, tags, and examples to determine the best match
- Always provide sufficient context when calling an agent
- You can call multiple agents if needed to fully answer the user's question
- Use the exact agent name as listed above
- Each tool call will only call one agent; to call multiple agents, use multiple tool calls

Be concise and helpful in your responses."""


# ============================================================================
# STEP 3: TOOL CREATION MODULE
# ============================================================================
# This module creates the tool that calls A2A agents

def create_call_agent_tool(registry_agents: List[Dict]):
    """
    Create a tool that can call any agent in the registry.
    
    Args:
        registry_agents: List of available agents (captured in closure)
        
    Returns:
        A LangChain tool that can call A2A agents
    """
    @tool
    async def call_agent(agent_name: str, query: str) -> str:
        """
        Call a specialized A2A agent to get information.
        
        Args:
            agent_name: The exact name of the agent to call (see system prompt for available agents)
            query: The question or task to send to the agent with full context
        
        Returns:
            The agent's response or an error message
        """
        # Step 3.1: Validate agent exists in registry
        available_agents = [agent['name'] for agent in registry_agents]
        
        if agent_name not in available_agents:
            return f"Error: Agent '{agent_name}' not found in registry. Available agents: {', '.join(available_agents)}"
        
        # Step 3.2: Make the A2A call
        try:
            response = await call_a2a_agent(agent_name, query)
            return response
        except Exception as e:
            return f"Error calling agent '{agent_name}': {str(e)}"
    
    return call_agent


# ============================================================================
# STEP 4: LANGGRAPH AGENT BUILDER MODULE
# ============================================================================
# This module builds the LangGraph agent with async tool support

def build_langgraph_agent_graph(model_with_tools, system_prompt: str, tools_by_name: Dict):
    """
    Build a LangGraph agent that supports async tool calls.
    
    This is necessary because OCI's OpenAI client doesn't fully support
    async invocation yet, so we manually build the graph to call tools async.
    
    Args:
        model_with_tools: LLM with tools bound
        system_prompt: System instructions for the agent
        tools_by_name: Dictionary mapping tool names to tool objects
        
    Returns:
        Compiled LangGraph agent
    """
    
    # Step 4.1: Define the LLM call node
    def llm_call(state: MessagesState):
        """
        LLM decides whether to call a tool or respond directly.
        System prompt is injected here with agent registry information.
        """
        system_instructions = [SystemMessage(system_prompt)]
        return {"messages": [model_with_tools.invoke(system_instructions + state["messages"])]}

    # Step 4.2: Define the tool execution node
    async def tool_node(state: MessagesState) -> dict[Any, Any]:
        """
        Execute tool calls asynchronously (needed for A2A protocol).
        """
        result = []
        for tool_call in state["messages"][-1].tool_calls:  # type: ignore[attr-defined]
            tool = tools_by_name[tool_call["name"]]
            observation = await tool.ainvoke(tool_call["args"])
            result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
        return {"messages": result}

    # Step 4.3: Define the routing logic
    def should_continue(state: MessagesState) -> str:
        """
        Decide whether to continue calling tools or end the conversation.
        """
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:  # type: ignore[attr-defined]
            return "tool_node"
        return END

    # Step 4.4: Build the graph
    agent_builder = StateGraph(MessagesState)
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)
    
    # Step 4.5: Define edges (flow)
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    agent_builder.add_edge("tool_node", "llm_call")
    
    # Step 4.6: Compile with memory
    agent = agent_builder.compile(checkpointer=InMemorySaver())
    
    return agent


# ============================================================================
# STEP 5: MAIN AGENT CLASS
# ============================================================================
# This class orchestrates all the modules above

class MainAgent:
    """
    Main orchestrator agent that coordinates calls to specialized A2A agents.
    """
    
    SANDBOX_CONFIG_FILE = "sandbox.yaml"
    LLM_MODEL = "xai.grok-4-fast-reasoning"

    def __init__(self, registry_agents: List[Dict]):
        """
        Initialize the main agent by setting up LLM, registry, and tools.
        
        Args:
            registry_agents: Pre-fetched list of agents from the registry
        """
        
        print("\n" + "="*90)
        print("INITIALIZING MAIN AGENT")
        print("="*90)
        
        # Step 5.1: Load configuration
        print("\nStep 1: Loading configuration...")
        self.scfg = self._load_config(self.SANDBOX_CONFIG_FILE)

        # Step 5.2: Initialize LLM client
        print("Step 2: Initializing LLM client...")
        self.openai_llm_client = OCIOpenAIHelper.get_client(
            model_name=self.LLM_MODEL,
            config=self.scfg,
            use_responses_api=True
        )
        print(f"  ✓ Using model: {self.LLM_MODEL}")

        # Step 5.3: Store the registry agents
        print("\nStep 3: Loading agent registry...")
        self.registry_agents = registry_agents
        for agent in self.registry_agents:
            print(f"  ✓ {agent['name']}: {agent.get('description', 'No description')}")

        # Step 5.4: Build system prompt with agent information
        print("\nStep 4: Building system prompt with agent details...")
        self.system_prompt = build_system_prompt_with_agents(self.registry_agents)
        print("  ✓ System prompt created with full agent information")

        # Step 5.5: Create tools
        print("\nStep 5: Creating agent tools...")
        self.tools = [create_call_agent_tool(self.registry_agents)]
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.model_with_tools = self.openai_llm_client.bind_tools(self.tools)
        print(f"  ✓ Created {len(self.tools)} tool(s): {list(self.tools_by_name.keys())}")

        # Step 5.6: Build the LangGraph agent
        print("\nStep 6: Building LangGraph agent...")
        self.agent = build_langgraph_agent_graph(
            self.model_with_tools,
            self.system_prompt,
            self.tools_by_name
        )
        print("  ✓ Agent graph compiled and ready")
        
        print("\n" + "="*90)
        print("AGENT INITIALIZATION COMPLETE")
        print("="*90 + "\n")

    def _load_config(self, config_path: str):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return EnvYAML(config_path)
        except FileNotFoundError:
            print(f"✗ Error: Configuration file '{config_path}' not found.")
            return None


# ============================================================================
# STEP 6: MAIN EXECUTION
# ============================================================================
# This is where the agent runs and processes user queries

async def main():
    """Main execution function - demonstrates the agent in action."""
    
    print(f"\n{'*' * 90}")
    print(f"{'*' * 25} AGENT DEMONSTRATION {'*' * 25}")
    print(f"{'*' * 90}\n")

    # Step 6.1: Fetch agent registry first (before creating MainAgent)
    print("Fetching agent registry...")
    registry_agents = await fetch_agent_registry()
    
    # Step 6.2: Create the main agent with pre-fetched registry
    main_agent = MainAgent(registry_agents)

    # Step 6.3: Define the user query
    prompt = "What types of clothes should I wear on a trip to Oracle headquarters next week?"
    config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    print(f"\n{'=' * 90}")
    print(f"USER QUERY: {prompt}")
    print(f"{'=' * 90}\n")

    # Step 6.4: Stream the agent's response
    async for chunk in main_agent.agent.astream(
        input={"messages": [HumanMessage(prompt)]},
        config=config,
        stream_mode="values",
    ):
        latest_message = chunk["messages"][-1]
        
        # Step 6.5: Display agent's text response
        if latest_message.content:
            print(f"\n{'─' * 90}")
            print("🤖 AGENT RESPONSE:")
            print(f"{'─' * 90}")
            try:
                print(latest_message.content[0]['text'])
            except:
                print(latest_message.content)
        
        # Step 6.6: Display tool calls being made
        elif latest_message.tool_calls:
            print(f"\n{'─' * 90}")
            print(f"🔧 CALLING TOOLS: {[tc['name'] for tc in latest_message.tool_calls]}")
            for tc in latest_message.tool_calls:
                print(f"   Agent: {tc['args'].get('agent_name', 'unknown')}")
                query = tc['args'].get('query', 'unknown')
                print(f"   Query: {query[:100]}{'...' if len(query) > 100 else ''}")
            print(f"{'─' * 90}")

    print(f"\n{'*' * 90}")
    print(f"{'*' * 30} COMPLETE {'*' * 30}")
    print(f"{'*' * 90}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

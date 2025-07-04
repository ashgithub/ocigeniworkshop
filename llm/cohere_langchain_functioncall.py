# /// pyproject.toml
# [project]
# dependencies = [
#   "langchain",
#   "langchain-community",
#   "langchain-core",
# ]
# ///
import os
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate

# 1. Setup LLM
llm = ChatOCIGenAI(
    model_id="cohere.command-a-03-2025",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga",
    model_kwargs={"temperature": 0.7, "max_tokens": 500},
    auth_profile="INNO-SANDBOX"
)

# 2. Define a simple tool as a Python function
def multiply_numbers(input: str) -> str:
    print(f" tool invoked with {input} ")
    numbers = [int(x) for x in input.split() if x.isdigit()]
    return str(numbers[0] * numbers[1]) if len(numbers) == 2 else "Please provide two numbers."

# 3. Register tool with LangChain
multiply_tool = Tool.from_function(
    func=multiply_numbers,
    name="multiply",
    description="Multiplies two numbers given as a space-separated string, e.g. '3 5'"
)

# 4. List of tools
tools = [multiply_tool]


# 5. Minimal ReAct prompt template
REACT_PROMPT = PromptTemplate.from_template(
    """You are a helpful AI assistant. You have access to the following tools:

{tools}

Tool Names: {tool_names}

When you need to use a tool, reply with:
Action: <tool name>
Action Input: <tool input>

If you know the answer, reply with:
Final Answer: <your answer>

Begin!

Question: {input}
{agent_scratchpad}"""
)

# 6. Create the agent
agent = create_react_agent(llm, tools=tools, prompt=REACT_PROMPT)

# 7. Create the executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)  # verbose shows tool usage

# 8. Run the agent with a question that triggers tool usage
result = agent_executor.invoke({"input": "What is 7 times 8?"})

print("Result:", result)

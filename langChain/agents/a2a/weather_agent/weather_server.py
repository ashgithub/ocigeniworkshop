""" Main a2a server that runs and has the agent card to be discovered """
""" TODO: !Important: Make sure to have running weather_server in indicated port BEFORE run main host agent """
""" First run the weather, city, and clothes server and then the main agent to connect to """
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import WeatherAgentExecutor

# Agent server details: https://a2a-protocol.org/latest/tutorials/python/3-agent-skills-and-card/
# Start the server: https://a2a-protocol.org/latest/tutorials/python/5-start-server/

if __name__ == '__main__':
    # --8<-- [start:AgentSkill]
    # Build an agent skill so the host agent knows the remote agent capabilites
    skill = AgentSkill(
        id='get_weather',
        name='get_weather',
        description='Gets the weather for a given city',
        tags=['weather'],
        examples=['get Chicago Weather'],
    )
    # --8<-- [end:AgentSkill]

    # --8<-- [start:AgentCard]
    # This will be the public-facing agent card
    public_agent_card = AgentCard(
        name="weather_agent",
        url='http://localhost:9999/',
        skills=[skill],  # Only the basic skill for the public card
        default_input_modes=['text'],
        default_output_modes=['text'],
        description='Gets the weather for a given city',
        version='1.0.0',
        capabilities=AgentCapabilities(streaming=True),
    )
    # --8<-- [end:AgentCard]

    # This section handles the message request, and uses the AgentExecutor for calling the remote agent.
    request_handler = DefaultRequestHandler(
        agent_executor=WeatherAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    # Starts the server in dedicated port already in the addresses dictionary on the remote_agent_connections.py
    uvicorn.run(server.build(), host='0.0.0.0', port=9999)
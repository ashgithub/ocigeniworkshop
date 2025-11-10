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

if __name__ == '__main__':
    # --8<-- [start:AgentSkill]
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

    request_handler = DefaultRequestHandler(
        agent_executor=WeatherAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9999)
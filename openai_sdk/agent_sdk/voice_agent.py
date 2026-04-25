""" What this file does:
Demonstrates a basic voice pipeline with:
1) STT model, 2) one voice agent workflow, and 3) WAV file output.

Documentation for reference:
- OpenAI SDK Voice agents: https://developers.openai.com/api/docs/guides/voice-agents
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code
- #genai-hosted-deployment-users: Information on GA deployment and integrations

Environment setup:
- Use `.env.example` to create your local `.env`
- Ensure OCI/OpenAI endpoint and project values are configured
- Optional overrides: `VOICE_STT_MODEL`, `VOICE_TTS_MODEL`, `VOICE_OUTPUT_FILE`

How to run the file:
uv run python agent_sdk/voice_agent.py

Safe experiments:
1. Change tool behavior in `get_weather` and ask weather-related prompts.
2. Swap `VOICE_STT_MODEL` / `VOICE_TTS_MODEL` and compare quality.
3. Change `SILENCE_SECONDS` and inspect output size.

Important sections:
1. Step 1: Define tools and build a voice-ready agent.
2. Step 2: Configure voice pipeline models.
3. Step 3: Run pipeline and save streamed audio as WAV. """

import asyncio
import os
import wave

import numpy as np

from agents import Agent, function_tool
from agents.voice import AudioInput, SingleAgentVoiceWorkflow, VoicePipeline
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
DEFAULT_STT_MODEL = "openai.gpt-4o-transcribe"
DEFAULT_TTS_MODEL = "openai.gpt-4o-mini-tts"
DEFAULT_OUTPUT_FILE = "output/voice_output.wav"
SAMPLE_RATE = 24000
SILENCE_SECONDS = 3


@function_tool
def get_weather(city: str) -> str:
    # Step 1: Example tool available to the voice agent.
    return f"The weather in {city} is sunny."


def build_voice_agent() -> Agent:
    # Step 2: Build one voice-capable assistant agent.
    return Agent(
        name="Assistant",
        instructions="You are a helpful voice assistant.",
        model=MODEL_ID,
        tools=[get_weather],
    )


async def main() -> None:
    # Step 3: Configure the OpenAI Agents SDK with OCI settings.
    OpenAIClientProvider().configure_agents_oci_env()
    stt_model = os.getenv("VOICE_STT_MODEL", DEFAULT_STT_MODEL)
    tts_model = os.getenv("VOICE_TTS_MODEL", DEFAULT_TTS_MODEL)

    # Step 4: Build the voice pipeline for one agent.
    pipeline = VoicePipeline(
        workflow=SingleAgentVoiceWorkflow(build_voice_agent()),
        stt_model=stt_model,
        tts_model=tts_model,
    )

    # Step 5: Use silence as placeholder audio input for demo purposes.
    audio_input = AudioInput(buffer=np.zeros(SAMPLE_RATE * SILENCE_SECONDS, dtype=np.int16))

    # Step 6: Run voice workflow and collect streamed audio bytes.
    result = await pipeline.run(audio_input)
    audio_buffer = bytearray()
    async for event in result.stream():
        if event.type == "voice_stream_event_audio":
            audio_buffer.extend(event.data)
            print("Received audio bytes", len(event.data))

    if not audio_buffer:
        print("No audio output received.")
        return

    # Step 7: Save output audio to a WAV file.
    output_file = os.getenv("VOICE_OUTPUT_FILE", DEFAULT_OUTPUT_FILE)
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with wave.open(output_file, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_buffer)

    print(f"Saved audio to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())

# Welcome to the LangChain Multimodal Module

This module explores text, image, and audio workflows by using OCI-hosted OpenAI-compatible multimodal models. It demonstrates how to generate, analyze, and transform content across multiple modalities.

## What You Will Learn

In this module, you will learn how to:

1. Generate images from text prompts (text → image)
2. Convert written prompts into natural speech (text → speech)
3. Transcribe recorded audio back into text (speech → text)
4. Analyze images with multimodal models (image → text)

## Environment Setup

- `sandbox.yaml`: Contains OCI configuration and compartment details.
- `.env`: Loads environment variables for optional overrides.
- Ensure you have access to OCI Generative AI services before running the examples.

## Suggested Study Order and File Descriptions

Work through the assets below to cover each capability end-to-end. All commands assume `uv run` from the repo root.

1. **`langChain/multimodal/text_to_image.py`**
   - Generates brand-new images using `openai.gpt-image-1.5`
   - Highlights: prompt customization, output sizing, base64 decoding, and file persistence
   - Run: `uv run langChain/multimodal/text_to_image.py`

2. **`langChain/multimodal/text_to_speech.py`**
   - Converts prompts into speech clips with `openai.gpt-audio`
   - Highlights: voice selection, output formats, and saved audio artifacts
   - Run: `uv run langChain/multimodal/text_to_speech.py`

3. **`langChain/multimodal/speech_to_text.py`**
   - Downloads or reuses an audio file and produces a transcript
   - Highlights: caching downloads, base64 encoding, and transcript extraction
   - Run: `uv run langChain/multimodal/speech_to_text.py`

4. **`langChain/multimodal/image_to_text.py`**
   - Uses multimodal models to analyze an image and describe what it contains
   - Highlights: image-to-base64 conversion, multimodal payload construction, and model comparison
   - Run: `uv run langChain/multimodal/image_to_text.py`

5. **`langChain/multimodal/multimodal.ipynb`**
   - Notebook walkthrough of the same multimodal pipelines with markdown explanations and practice prompts
   - Covers image → text, text → image, text → speech, and speech → text in one guided notebook
   - Run: open in VS Code or Jupyter and execute cells sequentially

## Project Ideas

1. **Marketing Asset Generator**
   - Chain text → image → speech to storyboard a campaign with visuals and narration.

2. **Interactive Audio Guide**
   - Accept user recordings, transcribe them, and respond with synthesized audio answers.

3. **Accessibility Companion**
   - Describe uploaded images aloud, save transcripts, and share them as study aids.

4. **Compliance Review Bot**
   - Convert spoken notes to text, summarize them, then generate presentation-friendly assets.

## Ideas for Experimenting

- **Prompt Engineering**: Change `IMAGE_PROMPT`, `AUDIO_PROMPT`, or `TRANSCRIBE_PROMPT` to see how results change.
- **Model Selection**: Compare different multimodal-capable models where supported.
- **Content Types**: Try your own images, receipts, or audio recordings.
- **Multi-language**: Generate speech in another language or transcribe bilingual clips.
- **Pipeline Chaining**: Generate an image, then analyze it with the image → text workflow.

## Resources and Links

- **Documentation**:
  - [OpenAI Audio Guide](https://developers.openai.com/api/docs/guides/audio)
  - [OpenAI Images and Vision Guide](https://developers.openai.com/api/docs/guides/images-vision)
  - [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas
  - **#igiu-ai-learning**: Help with environment setup or running the code
  - **#generative-ai-users**: Questions about OCI Generative AI

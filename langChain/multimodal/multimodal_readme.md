
## Welcome to the LangChain Multimodal Module

In this module, we experiment with text, audio, and image workflows using openAI apis 
You will learn how to:
1. Generate images from text prompts (text → image).
2. Convert written prompts into natural speech (text → speech).
3. Transcribe recorded audio back to text (speech → text).
4. Analyze existing images (image -> text)

## Environment Setup
- `sandbox.yaml`: Contains OCI config and compartment details.
- `.env`: Load environment variables (e.g., API keys if needed).
- Ensure you have access to OCI Generative AI services.

## Suggested Study Order and File Descriptions
Work through the assets below to cover each capability end-to-end. All commands assume `uv run` from the repo root.

1. **`langChain/multimodal/text_to_image.py`**  
   - Generates brand-new images using `openai.gpt-image-1.5`.  
   - Highlights: environment overrides for model/size/prompt, base64 decoding, saving to `scratch/`.  
   - Run: `uv run langChain/multimodal/text_to_image.py`.

2. **`langChain/multimodal/text_to_speech.py`**  
   - Turns prompts into audio clips via `openai.gpt-audio`.  
   - Highlights: choose voices, control format, store WAV files for reuse.  
   - Run: `uv run langChain/multimodal/text_to_speech.py`.

3. **`langChain/multimodal/speech_to_text.py`**  
   - Downloads (or reuses) a sample WAV file, encodes it, and obtains transcripts.  
   - Highlights: caching downloads, base64 encoding, usage metadata.  
   - Run: `uv run langChain/multimodal/speech_to_text.py`.

4. **`langChain/multimodal/multimodal.ipynb`**  
   - Notebook tour of the same pipelines with markdown explanations and practice prompts.  
   - New sections walk through text→image, text→speech, and speech→text before revisiting image analysis.  
   - Run: open in VS Code or Jupyter; ensure notebook root points to the repo.

5. **`langChain/multimodal/image_to_text.py`** *(if provided by Ashish)*  
   - Use this as a template for additional workflows like OCR or captioning.

## Project Ideas
1. **Marketing Asset Generator** – Chain text→image→speech to storyboard a campaign with visuals and narration.
2. **Interactive Audio Guide** – Accept user recordings, transcribe them, and respond with synthesized audio answers.
3. **Accessibility Companion** – Describe uploaded images aloud, save transcripts, and share as study aids.
4. **Compliance Review Bot** – Convert spoken notes to text, summarize, then create review-ready slides with generated art.

## Ideas for Experimenting
- **Prompt Engineering**: Control style words for `IMAGE_PROMPT`, emotional tone for `AUDIO_PROMPT`, and transcription focus for `TRANSCRIBE_PROMPT`.
- **Model Selection**: Swap between `openai.gpt-4o-mini`, `meta.llama-4-scout-17b`, or `xai.grok-4` for multimodal analysis.
- **Content Types**: Feed product mockups, receipts, or recordings from your own device.
- **Multi-language**: Request speech output in Spanish or transcribe bilingual clips.
- **Pipelining**: Run text→image, then describe the output using the notebook’s analysis section.

## Resources and Links
- **Documentation**:
  - [OpenAI gpt-audio](https://developers.openai.com/api/docs/guides/audio)
  - [OpenAI gpt-image](https://developers.openai.com/api/docs/guides/images-vision)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas.
  - **#igiu-ai-learning**: Help with sandbox environment or running code.
  - **#generative-ai-users**: Questions about OCI Gen AI.

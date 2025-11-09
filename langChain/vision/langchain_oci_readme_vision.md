
## Welcome to the LangChain Vision Module

In this module, we will experiment with multimodal LLMs using OCI Generative AI to analyze images, documents, and videos.

In this module, we will explore the following capabilities:
1. Image encoding and multimodal prompting with OCI models.
2. Comparing responses from different multimodal models (Llama, OpenAI, Grok).
3. Analyzing various content types including images and videos.
4. Interactive experimentation with prompts and model selection.

## Environment Setup
- `sandbox.yaml`: Contains OCI config and compartment details.
- `.env`: Load environment variables (e.g., API keys if needed).
- Ensure you have access to OCI Generative AI services.

## Suggested Study Order and File Descriptions
The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **openai_oci_multimodal.py**: Demonstrates multimodal LLM capabilities using OCI Generative AI models to analyze images. Encodes an image in base64, sends it to different models with a text prompt, and compares responses.
   - Key features: Base64 encoding, multimodal prompting, model comparison with timing.
   - How to run: `uv run langChain/vision/openai_oci_multimodal.py`.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai).

2. **openai_oci_multimodal.ipynb**: A Jupyter notebook variation of the openai_oci_multimodal.py script, demonstrating multimodal analysis with interactive cells and detailed explanations.
   - Key features: Mirrors the Python script with step-by-step markdown; includes experimentation sections and practice exercises.
   - How to run: Open in Jupyter or VS Code and run cells sequentially.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai).

## Project Ideas
Here are some ideas for projects you can build upon these examples:

1. **Document Analysis System**:
   - Build a tool to extract structured data from receipts, invoices, or forms.
   - Experiment with different prompt strategies for accuracy.
   - Add validation and error handling for real-world use.
   - Resources: [Multimodal Prompting Guide](https://docs.oracle.com/en-us/iaas/Content/generative-ai/multimodal.htm).

2. **Visual Content Moderation**:
   - Create a system to analyze images for content appropriateness.
   - Implement multi-model voting for better accuracy.
   - Add confidence scoring and human-in-the-loop review.
   - Resources: [Content Moderation Best Practices](https://docs.oracle.com/en-us/iaas/Content/generative-ai/content-moderation.htm).

3. **Educational Image Analysis**:
   - Develop tools to describe diagrams, charts, or educational materials.
   - Add support for multiple languages and accessibility features.
   - Integrate with learning management systems.
   - Resources: [Accessibility Guidelines](https://www.w3.org/WAI/).

4. **Video Frame Analysis**:
   - Extend image analysis to video content by processing frames.
   - Implement temporal analysis and scene change detection.
   - Create video summarization tools.
   - Resources: [Video Analysis Techniques](https://docs.oracle.com/en-us/iaas/Content/generative-ai/video-analysis.htm).

## Ideas for Experimenting
- **Prompt Engineering**: Try different question types (descriptive, analytical, comparative).
- **Model Selection**: Compare accuracy vs speed trade-offs between models.
- **Content Types**: Experiment with photos, diagrams, documents, and videos.
- **Multi-language**: Test with images containing text in different languages.
- **Batch Processing**: Modify scripts to process multiple images efficiently.

## Resources and Links
- **Documentation**:
  - [OCI Gen AI Multimodal](https://docs.oracle.com/en-us/iaas/Content/generative-ai/multimodal.htm)
  - [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai)
  - [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview)
  - [Vision Model Capabilities](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm#vision-models)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas.
  - **#igiu-ai-learning**: Help with sandbox environment or running code.
  - **#generative-ai-users**: Questions about OCI Gen AI.
  - **#ocigenerative-ai-users**: SDK questions.

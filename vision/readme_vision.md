
## Welcome to the Vision Module

In this module, we will experiment with the rich set of OCI AI Services that work with images, documents, and videos. You'll learn to analyze visual content using pre-trained models for object detection, text recognition, document understanding, and multimodal AI interactions.

Specifically, we will explore the following capabilities:
1. Using OCI Vision for analyzing images: object detection, text recognition, classification, and face detection.
2. Using OCI Document Understanding for OCR capability: document classification, language detection, key-value extraction, table extraction, and text extraction.
3. Using OCI Vision for analyzing video: temporal object detection, text recognition, and face detection across video frames.
4. Using multimodal LLMs (Llama, OpenAI, or Grok) for interactive image analysis and question-answering.

## Environment Setup
- `sandbox.yaml`: Contains OCI config, compartment, and bucket details for cloud services.
- `.env`: Load environment variables if needed (e.g., API keys).
- Install dependencies: `uv sync` or `pip install -r requirements.txt`

Example `sandbox.yaml` structure:
```yaml
oci:
  configFile: ~/.oci/config
  profile: DEFAULT
  compartment: ocid1.compartment...
bucket:
  namespace: your_namespace
  bucketName: your_bucket
  prefix: vision
```

Example `.env`:
```
# Add your Oracle ID prefix (if needed for sandbox.yaml)
MY_PREFIX=your_oracle_id
```

## Suggested Study Order and File Descriptions
The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **multi_modal.py**: Demonstrates multimodal prompts with OCI Generative AI, using text and image inputs to ask questions about images.
   - Key features: Base64 image encoding, multimodal message construction, LLM interaction.
   - How to run: `uv run vision/multi_modal.py`
   - Experiment: Change user_text to ask different questions, try different images.

2. **multi_model.ipynb**: Jupyter notebook version of multimodal image analysis with step-by-step explanations.
   - Key features: Interactive cells for image selection, model comparison, and result visualization.
   - How to run: Open in Jupyter and run cells sequentially.
   - Experiment: Compare different LLM models, try various image types.

3. **oci_vision.py**: Analyzes images using OCI Vision for comprehensive object detection and classification.
   - Key features: Image upload to Object Storage, feature selection, synchronous analysis.
   - How to run: `uv run vision/oci_vision.py [--file path/to/image]`
   - Experiment: Modify features array to focus on specific detection types.

4. **oci_vision.ipynb**: Notebook version of image analysis with detailed markdown explanations.
   - Key features: Visual image display, step-by-step analysis, result interpretation.
   - How to run: Open in Jupyter and execute cells.
   - Experiment: Try different images and feature combinations.

5. **oci_document_understanding.py**: Processes documents using OCI Document Understanding for advanced OCR and data extraction.
   - Key features: Document upload, asynchronous job processing, structured data extraction.
   - How to run: `uv run vision/oci_document_understanding.py [--file path/to/document]`
   - Experiment: Test with different document types (PDFs, images), modify feature sets.

6. **oci_document_understanding.ipynb**: Comprehensive notebook for document analysis with examples and exercises.
   - Key features: File upload demonstration, job monitoring, result parsing and visualization.
   - How to run: Execute in Jupyter environment.
   - Experiment: Analyze receipts, forms, or handwritten documents.

7. **oci_vision_video.py**: Analyzes videos using OCI Vision for temporal object and text detection.
   - Key features: Video upload, asynchronous processing, timeline-based results.
   - How to run: `uv run vision/oci_vision_video.py [--file path/to/video]`
   - Experiment: Process different video types, focus on specific detection features.

8. **oci_vision_video.ipynb**: Interactive notebook for video analysis with temporal visualizations.
   - Key features: Video processing workflow, progress monitoring, result interpretation.
   - How to run: Run cells in Jupyter.
   - Experiment: Analyze surveillance footage, sports videos, or content with text overlays.

**Note**: `document_understanding.ipynb` is a basic version and duplicates content from `oci_document_understanding.ipynb`. We recommend deleting it and using the more comprehensive `oci_document_understanding.ipynb` instead.

## Project Ideas
Here are some practical projects to build upon these examples:

1. **Smart Document Processor**: Create a system that automatically categorizes and extracts data from various document types (receipts, invoices, forms) for expense management or record-keeping.

2. **Visual Content Moderator**: Build an image/video analysis tool that detects inappropriate content, objects, or text for content moderation workflows.

3. **Interactive Image Assistant**: Develop a multimodal chatbot that can answer questions about uploaded images, provide descriptions, or extract specific information.

4. **Security Monitoring System**: Use video analysis to detect people, objects, or activities in surveillance footage, with alerts for specific events.

5. **Document Digitization Pipeline**: Create an end-to-end solution that scans physical documents, extracts structured data, and stores it in databases.

6. **Accessibility Tool**: Build an application that describes images for visually impaired users or extracts text from images/videos for better accessibility.

## Resources and Links
- **Documentation**:
  - [OCI Vision Overview](https://docs.oracle.com/en-us/iaas/Content/vision/using/home.htm)
  - [OCI Document Understanding](https://docs.oracle.com/en-us/iaas/Content/document-understanding/using/home.htm)
  - [OCI Generative AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [Python SDK Reference](https://github.com/oracle/oci-python-sdk)

- **Slack Channels**:
  - **#igiu-innovation-lab**: General project discussions and idea sharing.
  - **#igiu-ai-learning**: Help with sandbox setup, code issues, and environment problems.
  - **#oci_ai_vision_support**: Technical questions about OCI Vision APIs.
  - **#oci_ai_document_service_users**: Questions about Document Understanding service.
  - **#generative-ai-users**: Discussions about multimodal LLMs and Gen AI.

- **Postman Collections**:
  - [Vision API](https://www.postman.com/oracledevs/oracle-cloud-infrastructure-rest-apis/collection/061avdq/vision-api)
  - [Document Understanding API](https://www.postman.com/oracledevs/oracle-cloud-infrastructure-rest-apis/collection/28z4h20/document-understanding-api)

**Questions?** Don't hesitate to ask in the Slack channels. Experimentation is encouraged - try modifying parameters, testing different file types, and combining multiple services for innovative solutions!

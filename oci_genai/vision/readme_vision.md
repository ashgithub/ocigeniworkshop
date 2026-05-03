# Welcome to the Vision Module

This module explores OCI AI services that work with images, documents, videos, and multimodal prompts. It demonstrates how to analyze visual content by using OCI Vision, OCI Document Understanding, and multimodal LLMs.

> **GA project note**  
> This `oci_genai` tree intentionally shows the OCI Python SDK and service-specific APIs, many of which still use compartment-oriented setup. For new OpenAI-compatible GA project work, start with `openai_sdk/` instead; that tree uses project headers and the Responses API patterns used by the current Generative AI Platform.

## What You Will Learn

In this module, you will learn how to:

1. Use OCI Vision for image analysis such as object detection, text recognition, classification, and face detection
2. Use OCI Document Understanding for OCR, document classification, key-value extraction, and table extraction
3. Use OCI Vision for video analysis across frames
4. Use multimodal LLMs for interactive image understanding and question answering

## Environment Setup

- `sandbox.yaml`: Contains OCI config, compartment, and bucket details for cloud services.
- `.env`: Loads environment variables if needed.
- Install dependencies with `uv sync`.

Example `sandbox.yaml` structure:

```yaml
oci:
  configFile: /absolute/path/to/config
  profile: DEFAULT
  compartment: ocid1.compartment...
bucket:
  namespace: your_namespace
  bucketName: your_bucket
  prefix: vision
```

Example `.env`:

```env
MY_PREFIX=your_oracle_id
```

## Suggested Study Order and File Descriptions

The files are designed to build on one another. Study them in this order for a progressive understanding:

1. **`multi_modal.py`**
   - Demonstrates multimodal prompts with OCI Generative AI by combining text and images
   - How to run: `uv run oci_genai/vision/multi_modal.py`

2. **`oci_multimodal.ipynb`**
   - Notebook walkthrough of multimodal image analysis with interactive steps and model comparisons
   - How to run: open in Jupyter or VS Code and run the cells sequentially

3. **`oci_vision.py`**
   - Demonstrates OCI Vision image analysis for object detection, text recognition, classification, and faces
   - How to run: `uv run oci_genai/vision/oci_vision.py --file path/to/image`

4. **`oci_vision.ipynb`**
   - Notebook version of image analysis with guided steps and result interpretation
   - How to run: open in Jupyter or VS Code and run the cells sequentially

5. **`oci_document_understanding.py`**
   - Demonstrates OCI Document Understanding for OCR and structured document extraction
   - How to run: `uv run oci_genai/vision/oci_document_understanding.py --file path/to/document`

6. **`oci_document_understanding.ipynb`**
   - Comprehensive notebook for document analysis with examples and exercises
   - How to run: open in Jupyter or VS Code and run the cells sequentially

7. **`document_understanding.ipynb`**
   - Simpler or earlier notebook variant for document understanding
   - Keep this as a lighter or legacy example if useful, but prefer `oci_document_understanding.ipynb` for the main guided path

8. **`oci_vision_video.py`**
   - Demonstrates OCI Vision video analysis for labels, text, objects, and faces across frames
   - How to run: `uv run oci_genai/vision/oci_vision_video.py --file path/to/video`

9. **`oci_vision_video.ipynb`**
   - Notebook walkthrough for video analysis with progress monitoring and result interpretation
   - How to run: open in Jupyter or VS Code and run the cells sequentially

## Project Ideas

1. **Smart Document Processor**
   - Automatically classify and extract data from receipts, invoices, and forms.

2. **Visual Content Moderator**
   - Detect inappropriate content, objects, or text in images and videos.

3. **Interactive Image Assistant**
   - Build a multimodal chatbot that answers questions about uploaded images.

4. **Security Monitoring System**
   - Detect people, objects, or events in surveillance footage.

5. **Document Digitization Pipeline**
   - Convert scanned documents into structured machine-readable data.

6. **Accessibility Tool**
   - Describe images and extract text for accessibility-focused applications.

## Resources and Links

- **Documentation**:
  - [OCI Vision Overview](https://docs.oracle.com/en-us/iaas/Content/vision/using/home.htm)
  - [OCI Document Understanding](https://docs.oracle.com/en-us/iaas/Content/document-understanding/using/home.htm)
  - [OCI Generative AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [Python SDK Reference](https://github.com/oracle/oci-python-sdk)

- **Slack Channels**:
  - **#igiu-innovation-lab**: General project discussions and idea sharing
  - **#igiu-ai-learning**: Help with sandbox setup, code issues, and environment problems
  - **#oci_ai_vision_support**: Technical questions about OCI Vision APIs
  - **#oci_ai_document_service_users**: Questions about the Document Understanding service
  - **#generative-ai-users**: Discussions about multimodal LLMs and OCI Generative AI

- **Postman Collections**:
  - [Vision API](https://www.postman.com/oracledevs/oracle-cloud-infrastructure-rest-apis/collection/061avdq/vision-api)
  - [Document Understanding API](https://www.postman.com/oracledevs/oracle-cloud-infrastructure-rest-apis/collection/28z4h20/document-understanding-api)

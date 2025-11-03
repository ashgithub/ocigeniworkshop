
## Welcome to the Vision Module.
In this module, we will experiment with the rich set of OCI AI Services that work with images.

Specifically, we will try the following capabilities:
1. Using OCI Vision for analyzing images: object (including text) detection and classification.
2. Using OCI Document Understanding for OCR capability: classification of documents, and extraction of text, tables, and key/value pairs.
3. Using OCI Vision for analyzing video: object (including text) detection and classification.
4. Using multimodal LLM (Llama, openai or grok)  for working with images using LLM.

Remember to set up your `sandbox.yaml` file per your environment. This module uses the "oci" and "bucket" sections.

Example code in this module is available both as Jupyter notebook and Python code. They are very similar:
1. **oci_vision.py / vision.ipynb**: Upload image to object bucket and analyze it (classification, object/text/face detection).
2. **oci_vision_video.py / video.ipynb**: Upload video to object bucket and analyze it (object/text/face detection).
3. **oci_document_understanding.py / document_understanding.ipynb**: Upload a document to object bucket and analyze it (document/language classification, text, table, key/value extraction).
4. **multi_modal.py, multi_modal.ipynb**: encode the image and ask questions to a multimodal LLM


Here are some ideas for projects you can do (see notebook files for details):
- Convert an image of a business card to vCard file
- Convert an image of an agenda to calendar (iCal) file
- Create a customer record from driver's license


Here are a few links to help you:
- **#igiu-innovation-lab** for project ideas.
- **#igiu-ai-learning** for issues with the code or environment.
- **#oci_ai_vis_service_users** for OCI Vision API questions.
- **#oci_ai_document_service_users** for OCI Document service API questions.

https://docs.oracle.com/en-us/iaas/Content/vision/using/home.htm

## Environment Variables
Create a `.env` file at the project root for sensitive values referenced in `sandbox.yaml`.

Example `.env`:
```
# Add your Oracle ID prefix (if needed for sandbox.yaml)
MY_PREFIX=your_oracle_id
```
Load with `python-dotenv` if needed: `pip install python-dotenv` and `from dotenv import load_dotenv; load_dotenv()`.

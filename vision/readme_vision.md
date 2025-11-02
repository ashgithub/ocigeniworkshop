
## Welcome to the Vision Module.
In this module, we will experiment with the rich set of OCI AI Services that work with images.

Specifically, we will try the following capabilities:
1. Using OCI Vision for analyzing images: object (including text) detection and classification.
2. Using OCI Document Understanding for OCR capability: classification of documents, and extraction of text, tables, and key/value pairs.
3. Using OCI Vision for analyzing video: object (including text) detection and classification.
4. Using multimodal LLM (Llama 3.2) for working with images using LLM.

Remember to set up your `sandbox.yaml` file per your environment. This module uses the "oci" and "bucket" sections.

Example code in this module is available both as Jupyter notebook and Python code. They are very similar:
1. **oci_vision.py / vision.ipynb**: Upload image to object bucket and analyze it (classification, object/text/face detection).
2. **oci_vision_video.py / video.ipynb**: Upload video to object bucket and analyze it (object/text/face detection).
3. **oci_document_understanding.py / document_understanding.ipynb**: Upload a document to object bucket and analyze it (document/language classification, text, table, key/value extraction).


Here are some ideas for projects you can do (see notebook files for details):
- Create an API with a few parameters (e.g., city and days ahead). Try asking a question and see if LLM calls the API using the right values.
    - Sample question: "Next week in Seattle."
    - Sample question: "Weather tomorrow for capital of Colorado."
- Have a set of tools and provide agents with a subset of those tools based on the classification.
    - e.g., categories: billing, outage, rebates.
    - tools: get bills, get account number for name, outage for zip code, zip code of city, rebates for appliance, is appliance efficient.


Here are a few links to help you:
- **#igiu-innovation-lab** for project ideas.
- **#igiu-ai-learning** for issues with the code or environment.
- **#oci_ai_vis_service_users** for OCI Vision API questions.
- **#video-analysis-beta** for OCI Video API questions.
- **#oci_ai_document_service_users** for OCI Document service API questions.

https://docs.oracle.com/en-us/iaas/Content/vision/using/home.htm

## Environment Variables
Create a `.env` file at the project root for sensitive values referenced in `sandbox.yaml`.

Example `.env`:
```
MY_PREFIX=your_oracle_id
DB_PASSWORD=your_db_password
```
Load with `python-dotenv` if needed: `pip install python-dotenv` and `from dotenv import load_dotenv; load_dotenv()`.

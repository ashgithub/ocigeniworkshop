
## Welcome to the Vision Module
In this module, we will experiment with the OCI-compatible APIs and work with images.

### Multimodal LLMs
Using multimodal LLMs (Llama, OpenAI, or Grok) for working with images.

Remember to set up your `sandbox.yaml` file per your environment. This module uses the "oci" and "bucket" sections.

Example code in this module is available both as Jupyter notebook and Python code. They are very similar:
- **openai_oci_multimodal.py, openai_oci_multimodal.ipynb**: encode the image and ask questions to a multimodal LLM

### Project Ideas
Here are some ideas for projects you can do (see notebook files for details):
- Convert an image of a business card to vCard file
- Convert an image of an agenda to calendar (iCal) file
- Create a customer record from driver's license

Here are a few links to help you:
- **#igiu-innovation-lab** for project ideas.
- **#igiu-ai-learning** for issues with the code or environment.
- **#ocigenerative-ai-users** for sdk questions.


https://docs.oracle.com/en-us/iaas/Content/generative-ai/langchain.htm

## Environment Variables
Create a `.env` file at the project root for sensitive values referenced in `sandbox.yaml`.

Example `.env`:
```
# Add your Oracle ID prefix (if needed for sandbox.yaml)
MY_PREFIX=your_oracle_id
```
Load with `python-dotenv` if needed: `pip install python-dotenv` and `from dotenv import load_dotenv; load_dotenv()`.

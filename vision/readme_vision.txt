
Welcome to the Vision Module. In this module, we will experiment with the rich set of OCI AI Services that work with images.

Specifically, we will try the following capabilities:
1. Using OCI Vision for analyzing images: object (including text) detection & classification
2. Using OCI Document Understanding for OCR capability: classification of documents, and extraction of text, tables & key/value pairs
3. Using OCI Vision for analyzing video: object (including text) detection & classification
4. Using multimodel LLM (Llama 3.2) for working with images using LLM

When using OCI AI Vision & Document Understanding services, we will be uploading the documents to an object bucket:
    - Please use the PHX tenancy to work with your object bucket. The Chicago tenancy is a read-only replica.
    - As you are working in a shared sandbox, use a unique prefix (prefix is analogous to a subfolder) (e.g., your Oracle ID).
    - Remember to update the code in this module with the details of your bucket (NAMESPACE, BUCKET_NAME, FILE_NAME, PREFIX)
    - Remember to update the FILE_TO_ANALYZE to the local file you want to analyze

As always, make sure your OCI client config & the compartment you are assigned to are correct:
    - Config file is assumed to be in ~/.oci/config. Change it if needed.
    - CONFIG_PROFILE: for the section on your local OCI config file that you configured for use with the sandbox
    - COMPARTMENT_ID: OCID of the compartment assigned to you

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:

1. oci_vision.py / vision.ipynb: upload image to object bucket & analyze it (classification, object/text/face detection)
2. oci_vision_video.py / video.ipynb: upload video to object bucket & analyze it (object/text/face detection)
3. oci_document_understanding.py / document_understanding.ipynb: upload a document to object bucket & analyze it (document/language classification, text, table, key/value extraction)


Here are some ideas of projects you can do (See notebook files for details):
    - create an api with a few parameters (eg: city & days ahead). try askig question and see if llm calls the api using right values 
        - sample question: next week in seattle
        - sample question:  weather tomm for capital of colorado
    - have a set of tools and provide Agents with subsut of those tools based on the classification 
        eg: categories: billing, outage, rebates
            tools: get biils, get account number for name,  outage for zipcode, zipcode of city, rebates for applicate, is appliance efficent


Here are few links to help you: 

#igiu-innovation-lab
#igiu-ai-learning
#generative-ai-users_

https://docs.oracle.com/en-us/iaas/Content/vision/using/home.htm


# OCI AI Services Workshop

This project is aimed at introducing seasoned developers to Oracle's OCI AI Services.

## Project Constraints
- The project is focused on the OCI Generative AI library. This library is rapidly evolving. We are using the library which was just released: https://github.com/oracle-samples/oci-openai
- We use LangGraph version 1.0.3: https://docs.langchain.com/oss/python/langchain/overview. It does break old libraries; do not revert to older versions.
- We use UV to maintain Python environments.

## Tips
- Keep the code simple and easy to understand. It's focused on teaching concepts.
- The project is divided into folders for various concepts.
- Each folder has a README file. Keep it up to date.
  - maintain the format
  - ensure all links and referneces are valid
  - pay specila attension to urls
    - They shou;d be valid
    - if they ar enot mentioned in python file. make sure it has high value
    - if they are outsideof iracle, confirmm before using

- Each Python file should have comments at the top that explain:
  - What the file does
  - Documentation to reference
  - Relevant Slack channels
  - Environment setup (sandbox.yaml & .env file)
  - How to run the file: `uv run <relative path to file from project root>`
  - Comments on important sections of the file
- Each folder also has a Jupyter notebook variation of the same sample.

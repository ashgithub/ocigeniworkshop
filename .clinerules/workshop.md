This project is aimed at introducing seasoned developers to Oracle's OCI  AI Services. 

Project constrainits:
- The project is focussed at OCI Gen AI library.  This librray is rapidly evolving. We are using the librray which was just released: https://github.com/oracle-samples/oci-openai
- We use langgraph version 1.0.3 https://docs.langchain.com/oss/python/langchain/overview.  it does break old libraries, do not revert to older versions
- We use UV to matain python enviornmnts

Tips
- Keep the code simple as easy to understand. Its focussed at teaching concepts
- Project is divided into folders for various concepts
- each folder has a readme file. keep it upto date
- each pythonn file shuld have comments at top that explain
  - What file does
  - documentation to reference
  - relevant slack channels
  - env setup (sandbix.yaml & .env file)
  - how to run the file `uv run <relative path to file from project root>
  - comments to important sections of file
- each folder also has a jupyter notebook variation of teh sameple code
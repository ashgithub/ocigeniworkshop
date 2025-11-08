""" Sample file to load and chunk documents using LangChain text splitters """

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_core.documents import Document

# Reference for document loaders: https://docs.langchain.com/oss/python/langchain/knowledge-base#1-documents-and-document-loaders
# Reference for chunks: https://docs.langchain.com/oss/python/integrations/splitters

# Using LangChain community document loader
# Sample PDF document
pdf_path = "./langChain/rag/Sample1.pdf"

# Step 1: load the documents
print(f"Loading PDF: {pdf_path}")
loader = PyPDFLoader(pdf_path)
docs = loader.load()  # returns a list of Document objects

# Look at the document details
print(f"Loaded {len(docs)} pages from the PDF.")
print(f"Example page content:\n{docs[0].page_content[:300]}...\n")

# Other option to build custom document chunks without the document loader
# documents = [
#     Document(
#         page_content="Dogs are great companions, known for their loyalty and friendliness.",
#         metadata={"source": "mammal-pets-doc"},
#     ),
#     Document(
#         page_content="Cats are independent pets that often enjoy their own space.",
#         metadata={"source": "mammal-pets-doc"},
#     ),
# ]

# Step 2: use text splitters

# LangChain Text splitter, most common: recursive
# Splits according to default list ["\n\n","\n"," ",""]
text_splitter = RecursiveCharacterTextSplitter(
    # For custom separators patterns
    # separators=[
    #     "\u200b",  # Zero-width space
    #     "\uff0c",  # Fullwidth comma
    #     "\u3001",  # Ideographic comma
    #     "\uff0e",  # Fullwidth full stop
    #     "\u3002",  # Ideographic full stop
    # ]
    chunk_size=300, # Chunk character size
    chunk_overlap=200, # Chunk information overlap
    add_start_index=True, # Includes the reference index
    is_separator_regex=False # Is the separator list ["\n\n","\n"," ",""] interpreted as regex
)

# Performs the chunking of the given documents
splits = text_splitter.split_documents(docs) 
print(f"Created {len(splits)} text chunks for embedding.")

# Inspect the first 3 splits, clearly separated
num_to_show = min(3, len(splits))
print(f"Showing the first {num_to_show} chunks (out of {len(splits)}):")
for i, doc in enumerate(splits[:num_to_show], start=1):
    start = doc.metadata.get("start_index", "N/A") if isinstance(doc.metadata, dict) else "N/A"
    page = doc.metadata.get("page", doc.metadata.get("page_number", "N/A")) if isinstance(doc.metadata, dict) else "N/A"
    print("\n" + "=" * 20 + f" Chunk {i}/{num_to_show} | page={page} | start_index={start} " + "=" * 20)
    # Show a preview of the chunk content (first 400 chars)
    preview = doc.page_content[:400] + ("..." if len(doc.page_content) > 400 else "")
    print(preview)
    print("\n" + "=" * 60 + "\n")

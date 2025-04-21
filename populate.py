import os
import re
import shutil
from collections import defaultdict
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.schema.document import Document
from rag import get_embedding_function
from langchain_chroma import Chroma

CHROMA_PATH = "chroma"
DATA_PATH = "data"

def populate_db():
    print("Deleting Old Database...")
    clear_database()
    print("Loading Documents...")
    documents = load_documents()
    print("Merging pages from same source...")
    merged_documents = merge_documents(documents)
    print("Splitting merged documents into chunks...")
    at_chunks = split_documents_by_at(merged_documents)
    print(f"Number of chunks extracted: {len(at_chunks)}")
    print("Adding chunks to database...")
    add_to_chroma(at_chunks)
    print("Done.")

def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def merge_documents(documents: list[Document]) -> list[Document]:
    groups = defaultdict(list)
    for doc in documents:
        source = doc.metadata.get("source", "unknown")
        groups[source].append(doc)
    merged_docs = []
    for source, docs in groups.items():
        # sort pages if available
        docs.sort(key=lambda d: int(d.metadata.get("page", 0)))
        merged_text = "\n".join(doc.page_content for doc in docs)
        merged_docs.append(Document(page_content=merged_text, metadata={"source": source}))
    return merged_docs

def split_documents_by_at(documents: list[Document]) -> list[Document]:
    splitted_docs = []
    pattern = re.compile(r"@\s*(.*?)\s*@", re.DOTALL)
    for doc in documents:
        matches = pattern.findall(doc.page_content)
        for match in matches:
            text = match.strip()
            if text:
                new_doc = Document(page_content=text, metadata=doc.metadata.copy())
                splitted_docs.append(new_doc)
    return splitted_docs

def add_to_chroma(chunks: list[Document]):
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
    new_chunks = []
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    for idx, chunk in enumerate(chunks):
        chunk_id = f"chunk-{idx}"
        chunk.metadata["id"] = chunk_id
        if chunk_id not in existing_ids:
            new_chunks.append(chunk)
    if new_chunks:
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

if __name__ == "__main__":
    populate_db()
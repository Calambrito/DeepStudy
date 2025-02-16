import re
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question below, use the given context if necessary:

{context}

---

Answer the question, rely on the context given above if needed and do not refer to the context in your response. The user providing the question is not privy to the context: {question}
"""

def get_embedding_function():
    return OllamaEmbeddings(model="nomic-embed-text")

def RAG(query: str, model: OllamaLLM):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    results = db.similarity_search_with_score(query, k=3)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query)

    print(prompt + "\n\n")
    response_text = model.invoke(prompt)

    print("\n\n=== FINAL RESPONSE ===")
    print(response_text)
    
    return response_text

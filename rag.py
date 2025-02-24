from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Given Below is what courses I have for the mentioned weeks.

{context}

---

{question}

Generate study plans following the given template.

Day 1:
X hours: [Topic Name]
Suggestions:
Y hours: [Topic Name]
Suggestions:
... and so on

Day 2:
X hours: [Topic Name]
Suggestions:
Y hours: [Topic Name]
Suggestions:
... and so on

Distribute every single topic covered in the week throughout 5 days adding upto no more than 3.5 hours of studying a day. 
In the Suggestions add crucial insights that people commonly face when using that topic.
If you notice a quiz or midterm for a subject, make sure to add prep for that early on in the week.

"""

def get_embedding_function():
    return OllamaEmbeddings(model="nomic-embed-text")

def RAG(query: str, model: OllamaLLM):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    results = db.similarity_search_with_score(query, k=1)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query)

    print(prompt + "\n\n")
    response_text = model.invoke(prompt)
    print("\n\n=== FINAL RESPONSE ===")
    print(response_text)
    
    return response_text 

from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from google import genai
from pages.key import get_api_key

CHROMA_PATH = "chroma"

# PROMPT_TEMPLATE = """
# YOU ARE AN AI HELPER THAT GENERATES STUDY PLANS FOR A STUDENT AT NORTH SOUTH UNIVERSITY
# Given Below is what courses I have for the mentioned weeks.

# {context}

# ---

# {question}

# Generate study plans following the given template.

# # Study Plan for Week N

# ## Day 1:
# **X hours: [Topic Name]**:
# - [Suggestion]

# **Y hours: [Topic Name]**:
# - [Suggestion]

# ## Day 2:
# **X hours: [Topic Name]**:
# - [Suggestion]


# Distribute every single topic covered in the week throughout 5 days adding upto no more than 3.5 hours of studying a day. 
# In the Suggestions add crucial insights that people commonly face when using that topic.
# If you notice a quiz or midterm for a subject, make sure to add prep for that early on in the week or in the week prior.
# Do not make any references to the prompt in your response.
# Start with "heres a study plan" or something nice and witty.
# Breaks are to be managed by the user do not include breaks or relaxation in the plan.
# """

PROMPT_TEMPLATE = """
YOU ARE AN AI HELPER THAT GENERATES STUDY PLANS FOR A STUDENT AT NORTH SOUTH UNIVERSITY

Weekly Topics:
{context}

---

User Query:
{question}

If the user has a general query, sharing some thoughts or is asking for tips DO NOT provide a study plan. 
Ignore the weekly topics and provide a concise but natural answer.

Otherwise generate study plans using the weekly topics provided above.
If the user has specified course codes in the query then provide a plan ONLY FOR THAT COURSE.
Distribute every topic covered in the week throughout 5 days adding upto no more than 4 hours of studying a day. 
Add short and useful suggestions at the end of each topic.
Dont any topic less than 45 minutes.
Do not make any references to the prompt in your response.
Start with "heres a study plan" or something nice and witty.
Breaks are to be managed by the user do not include breaks or relaxation in the plan.
"""

def get_embedding_function():
    return OllamaEmbeddings(model="nomic-embed-text")

def RAG(query: str, model: OllamaLLM):
    key = get_api_key()
    client = genai.Client(api_key=key)
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    results = db.similarity_search_with_score(query, k=14)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query)

    print(prompt + "\n\n")
    response_text = client.models.generate_content(model = "gemini-2.0-flash", contents = prompt)
    print("\n\n=== FINAL RESPONSE ===")
    print(response_text)
    
    return response_text 

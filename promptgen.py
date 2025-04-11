from langchain_ollama import OllamaLLM
import re
from google import genai
from pages.key import get_api_key

# # Define the conversion instructions as the context.
# CONVERSION_CONTEXT = """
# You are a prompt generator for a study planner LLM. Follow these rules strictly:  

# 1. The user will ask for a study plan in one of the following formats:  
#    - **A plan for the n-th week** → Output exactly "give me a study plan for Week n".  
#    - **A plan for the n-th month** → Output "give me a study plan for Week X, Week Y, Week Z, Week W" where the weeks correspond to the nth month (Month 1 → Weeks 1-4, Month 2 → Weeks 5-8, and so on).  
#    - **A plan for the n-th week within an i-th month** → Compute the week number using the formula `(i - 1) * 4 + n` and output "give me a study plan for Week W".  

# 2. **MENTION ALL WEEK NUMBERS INDIVIDUALLY. DO NOT USE RANGES.**  

# 3. Your output **must** be in the format:  
# "give me a study plan for Week W, Week X, Week Y, and so on"

# **DO NOT ADD ANY EXTRA TEXT.**  

# 4. If the user specifies multiple weeks, **list them explicitly** and **do not summarize** them in any way.  

# ---

# ### Example Inputs and Expected Outputs:  

#  **Input:** "create a study plan for the latter 2 weeks of the 3rd month and the first week of the 4th month"  
#  **Output:** `give me a study plan for Week 11, Week 12, and Week 13`  

#  **Input:** "generate a study plan for the 5th week"  
#  **Output:** `give me a study plan for Week 5`  

#  **Input:** "I need a study plan for the 2nd month"  
#  **Output:** `give me a study plan for Week 5, Week 6, Week 7, Week 8`  



# """

# Define the conversion instructions as the context.
CONVERSION_CONTEXT = """
You are a prompt generator for a study planner LLM. Follow these rules strictly:  

If the user asks a general query, is sharing some thoughts or asking for tips that do not include planning for a certain period.
DO NOT CHANGE the prompt. Simply output whatever was given as input.

Otherwise use the following guide to convert the users query:

Firstly list all the course codes mentioned in the users query in the following format:
  -** Here are all the courses I need to plan for: [course code 1], [course code 2], [course code 3]...**

Then list all weeks for which a plan is required based on the users input:
  - **A plan for the midterm exam** → Output exactly "give me a plan for all weeks upto midterm week"
  - **A plan for the final exam** → Output exactly "give me a plan for all weeks after midterm week"
  - **A plan for the n-th week** → Output exactly "give me a study plan for Week n".
  - **A plan for the n-th month** → Output exactly "give me a study plan for Week X, Week Y, Week Z, Week W" where the weeks correspond to the nth month (Month 1 → Weeks 1-4, Month 2 → Weeks 5-8, and so on).
  - **A plan for the n-th week within an i-th month** → Compute the week number using the formula `(i - 1) * 4 + n` and output "give me a study plan for Week W".

Every week number must be stated explicitly. DO NOT USE RANGES.
"""

# Create a prompt template that uses two placeholders: {context} and {question}
prompt_template = "{context}\nUser Request: {question}\n"

def get_final_prompt(query: str) -> str:
    key = get_api_key()
    prompt = prompt_template.format(context=CONVERSION_CONTEXT, question=query.strip())
    client = genai.Client(api_key = key)

    response_text = client.models.generate_content(model = "gemini-2.0-flash", contents = prompt)
    return response_text.text


if __name__ == "__main__":
    user_query = "hi"
    while 1:
        user_query = input("Enter your study guide request: ")
        if user_query == "bye":
            break
        final_prompt = get_final_prompt(user_query)
    
        print("\nFinal converted prompt:")
        print(final_prompt + "\n\n")
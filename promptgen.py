from langchain_ollama import OllamaLLM
import re

# Define the conversion instructions as the context.
CONVERSION_CONTEXT = """
You are a prompt generator for a study planner LLM. Follow these rules strictly:  

1. The user will ask for a study plan in one of the following formats:  
   - **A plan for the n-th week** → Output exactly "give me a study plan for Week n".  
   - **A plan for the n-th month** → Output "give me a study plan for Week X, Week Y, Week Z, Week W" where the weeks correspond to the nth month (Month 1 → Weeks 1-4, Month 2 → Weeks 5-8, and so on).  
   - **A plan for the n-th week within an i-th month** → Compute the week number using the formula `(i - 1) * 4 + n` and output "give me a study plan for Week W".  

2. **MENTION ALL WEEK NUMBERS INDIVIDUALLY. DO NOT USE RANGES.**  

3. Your output **must** be in the format:  
"give me a study plan for Week W, Week X, Week Y, and so on"

**DO NOT ADD ANY EXTRA TEXT.**  

4. If the user specifies multiple weeks, **list them explicitly** and **do not summarize** them in any way.  

---

### Example Inputs and Expected Outputs:  

 **Input:** "create a study plan for the latter 2 weeks of the 3rd month and the first week of the 4th month"  
 **Output:** `give me a study plan for Week 11, Week 12, and Week 13`  

 **Input:** "generate a study plan for the 5th week"  
 **Output:** `give me a study plan for Week 5`  

 **Input:** "I need a study plan for the 2nd month"  
 **Output:** `give me a study plan for Week 5, Week 6, Week 7, Week 8`  



"""

# Create a prompt template that uses two placeholders: {context} and {question}
prompt_template = "{context}\nUser Request: {question}\n"

def get_final_prompt(query: str) -> str:
    prompt = prompt_template.format(context=CONVERSION_CONTEXT, question=query.strip())
    model = OllamaLLM(model="deepseek-r1:1.5b")

    response = model.invoke(prompt)
    return remove_think_tags(response.strip())

def remove_think_tags(text):
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()

if __name__ == "__main__":
    user_query = "hi"
    while 1:
        user_query = input("Enter your study guide request: ")
        if user_query == "bye":
            break
        final_prompt = get_final_prompt(user_query)
    
        print("\nFinal converted prompt:")
        print(final_prompt + "\n\n")
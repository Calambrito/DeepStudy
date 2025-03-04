from langchain_ollama import OllamaLLM
import re

# Define the conversion instructions as the context.
CONVERSION_CONTEXT = """
You are a precise conversion assistant. Your task is to take a human’s loosely defined study plan request and generate a clear, unambiguous prompt that specifies the exact weeks for a study plan. Follow these instructions:

The user will always demand a study plan in one of the following formats:
    -a plan for the n-th week
        How to handle: Just output the nth week raw no need to do anything.
    -a plan for the n-th month
        How to handle: Output the 4 weeks that consitute said month, for the 1st month it would be week 1, week 2, week 3, week 4 for month 2 it will be start from week 5 to week 8 and so on.
    -a plan for the n-th week within an i-th month
        How to handle: find the number weeks in the months prior to the mentioned month and then add the given number of weeks
    Your output must me similar to the examples given. examples: "give me a study plan for week x" or "give me a study plan for week x and week y" or "give me a study plan for week x and week y and week z" 
    MENTION ALL WEEK NUMBERS IN THE OUTPUT PROMPT DO NOT USE RANGES
"""

# Create a prompt template that uses two placeholders: {context} and {question}
prompt_template = "{context}\nUser Request: {question}\n"

def get_final_prompt(query: str) -> str:
    """
    Build the composite prompt with the conversion context and user query.
    Then use ollama.mode.invoke to generate the final prompt.
    """
    prompt = prompt_template.format(context=CONVERSION_CONTEXT, question=query.strip())
    model = OllamaLLM(model="deepseek-r1:7b")

    response = model.invoke(prompt)
    return remove_think_tags(response.strip())

def remove_think_tags(text):
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()

if __name__ == "__main__":
    user_query = input("Enter your study guide request: ")
    final_prompt = get_final_prompt(user_query)
    
    print("\nFinal converted prompt:")
    print(final_prompt)
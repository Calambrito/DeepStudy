import time
import re
import streamlit as st
from langchain_ollama import OllamaLLM
from rag import RAG

def main():
    st.set_page_config(page_title="DeepStudy Chat", page_icon="🤖", layout="centered")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Let's start studying!"}]
    if "toggle" not in st.session_state:
        st.session_state.toggle = False

    col_header_left, col_header_right = st.columns([3, 1])
    with col_header_left:
        st.title("DeepStudy Chat")
    with col_header_right:
        if st.button(f"DeepPlan {'ON' if st.session_state.toggle else 'OFF'}"):
            st.session_state.toggle = not st.session_state.toggle
            st.rerun()

    for msg in st.session_state.messages:
        content = msg["content"].replace("\n", "\n\n")
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(content)
        else:
            with st.chat_message("user"):
                st.markdown(content)

    user_input = st.chat_input("What instructions do you want for studying?")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input.replace("\n", "\n\n"))
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("Generating response..."):
                model = OllamaLLM(model="llama3.2")
                response_text = RAG(user_input, model)
            for token in response_text.split():
                full_response += token + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response.replace("\n", "\n\n") + "▌")
            message_placeholder.markdown(full_response.replace("\n", "\n\n"))
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
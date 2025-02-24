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

    col_header_left, col_header_center, col_header_right = st.columns([3, 1, 1])
    with col_header_left:
        st.title("DeepStudy Chat")
    with col_header_center:
        if st.button("Clear Chat"):
            st.session_state.messages = [{"role": "assistant", "content": "Let's start studying!"}]
            st.rerun()
    with col_header_right:
        if st.button(f"DeepPlan {'ON' if st.session_state.toggle else 'OFF'}"):
            st.session_state.toggle = not st.session_state.toggle
            st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

    user_input = st.chat_input("Start planning!")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input, unsafe_allow_html=True)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("Generating response..."):
                model = OllamaLLM(model="qwen2.5:14b")
                response_text = RAG(user_input, model)
            tokens = re.split(r'(\s+)', response_text)
            for token in tokens:
                full_response += token
                time.sleep(0.03)
                message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            message_placeholder.markdown(full_response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
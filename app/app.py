import streamlit as st
from msal_streamlit_authentication import msal_authentication
import openai

# openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="NUSHChat")

st.session_state["openai_model"] = "gpt-3.5-turbo"
if "messages" not in st.session_state.keys():
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input(): #disabled=not (hf_email and hf_pass))
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    full_response = "Hello"

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
    #     full_response = ""
    #     for response in openai.ChatCompletion.create(
    #         model=st.session_state["openai_model"],
    #         messages=[
    #             {"role": m["role"], "content": m["content"]}
    #             for m in st.session_state.messages
    #         ],
    #         stream=True,
    #     ):
    #         full_response += response.choices[0].delta.get("content", "")
            # message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})


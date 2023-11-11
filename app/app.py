import streamlit as st
import openai
import msal
import webbrowser
import requests
from PIL import Image
import io
import urllib.request
from msal_streamlit_authentication import msal_authentication
import mimetypes 
import os

mimetypes.add_type('application/javascript', '.js') 
mimetypes.add_type('text/css', '.css')

openai.api_key = os.environ["key"]

st.set_page_config(page_title="NUSHChat")

client_id = "487941ff-cc17-4706-a900-6a0578516e86"
tenant_id = "d72a7172-d5f8-4889-9a85-d7424751592a"
redirect_uri = "http://localhost:8501/"
scopes = ["profile"]
authority = f"https://login.microsoftonline.com/{tenant_id}"
endpoint = "https://graph.microsoft.com/v1.0/me"

os.environ['ENABLED'] = ""


token = None
temp = 0.0

with st.sidebar:
    
    token = msal_authentication(
        auth={
            "clientId": client_id,
            "authority": authority,
            "redirectUri": redirect_uri,
            "postLogoutRedirectUri": redirect_uri
        }, # Corresponds to the 'auth' configuration for an MSAL Instance
        cache={
            "cacheLocation": "sessionStorage",
            "storeAuthStateInCookie": False
        }, # Corresponds to the 'cache' configuration for an MSAL Instance
        login_request={
            "scopes": ["user.read"]
        }, # Optional
        logout_request={}, # Optional
        login_button_text="Login", # Optional, defaults to "Login"
        logout_button_text="Logout", # Optional, defaults to "Logout"
        class_name="css_button_class_selector", # Optional, defaults to None. Corresponds to HTML class.
        html_id="html_id_for_button", # Optional, defaults to None. Corresponds to HTML id.
    )
    if (token):
        if (True or token['idTokenClaims']['preferred_username'].split('@')[-1].strip() in ["nushigh.edu.sg","nus.edu.sg"] and token['idTokenClaims']['preferred_username'][:3] in "anhs"):
            on = st.toggle('Activate Chat', value=os.environ['ENABLED'])
            
            if on:
                os.environ['ENABLED']  = "1"
            else:
                os.environ['ENABLED']  = ""
        token = True if (token['idTokenClaims']['preferred_username'].split('@')[-1].strip() in ["nushigh.edu.sg","nus.edu.sg"]) else False
        st.text("")
        st.text("")
        temp = st.slider('Temperature', 0.0, 1.0, 0.0)

    

st.session_state["openai_model"] = "gpt-3.5-turbo"
if "messages" not in st.session_state.keys():
    st.session_state.messages = []  
    
# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Your Input (Use /image for image creation)", disabled=not (token and os.environ['ENABLED'])): 
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    full_response = "Hello"
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        if (prompt.split(" ")[0] == "/image"):
            full_response = openai.Image.create(prompt=" ".join(prompt.split(" ")[1:]), n=1, size="512x512")["data"][0]["url"]
            with urllib.request.urlopen(full_response) as response:
                st.image(Image.open(response))
        else:
            full_response = ""
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})


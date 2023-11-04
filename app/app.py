import streamlit as st
import openai
import msal
import webbrowser
import requests
from PIL import Image
import io
import urllib.request

# openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="NUSHChat")

client_id = "487941ff-cc17-4706-a900-6a0578516e86"
tenant_id = "d72a7172-d5f8-4889-9a85-d7424751592a"
redirect_uri = "http://localhost:8501/"
scopes = ["profile"]
authority = f"https://login.microsoftonline.com/{tenant_id}"
endpoint = "https://graph.microsoft.com/v1.0/me"

app = msal.PublicClientApplication(
    client_id, authority=authority
)

token = None
temp = 0.0

def get_token_from_cache():
    accounts = app.get_accounts()
    if not accounts:
        return None
    
    result = app.acquire_token_silent(scopes, account=accounts[0])
    if "access_token" in result:
        return result["access_token"]
    else:
        return None

def login():
    flow = app.initiate_auth_code_flow(scopes=scopes, state=['todo'])
    
    if "auth_uri" not in flow:
        return st.write("Failed with token")
    
    auth_uri = flow['auth_uri']
    webbrowser.open(auth_uri, new=0)
    auth_code = st.experimental_get_query_params()
    
    if 'code' not in auth_code:
        return st.write("Failed with token")
    
    result = app.acquire_token_by_authorization_code(auth_code, scopes=scopes)
    if "access_token" in result:
        return result["access_token"]
    else:
        return st.write("No token found")
    
st.markdown(
        """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 200px;
           max-width: 200px;
       }
       """,
        unsafe_allow_html=True,
    )   

with st.sidebar:
    col1, col2, col3 = st.columns([0.4,1,0.4])
    if col2.button("Login", type="primary"):
        get_token_from_cache()
        token = login()

        st.write(st.experimental_get_query_params())
        if token:
            st.write("Logged in successfully!")
            st.write(token)
        else:
            st.write("Failed to login")  
    
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

if prompt := st.chat_input("Your Input (Use /image for image creation)", disabled=not (token)): 
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    full_response = "Hello"
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        if (prompt.split(" ")[0] == "/image"):
            full_response = "https://wallpapers.com/images/featured-full/batman-pictures-ldrww5lw9rhd7hyo.jpg"#openai.Image.create(prompt=" ".join(prompt.split(" ")[1:]), n=1, size="512x512")["data"][0]["url"]
            with urllib.request.urlopen(full_response) as response:
                st.image(Image.open(response))
        else:
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


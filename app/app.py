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

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred_path = 'y1llmbot-firebase-adminsdk-19xt8-069c3296b3.json'
cred_path = os.path.join(os.path.dirname(__file__),cred_path)
cred = credentials.Certificate(cred_path)
if 'Y1LLMBOT' not in firebase_admin._apps:
    firebase_admin.initialize_app(cred, name="Y1LLMBOT")

app = firebase_admin.get_app(name="Y1LLMBOT")

# Initialize Firestore DB
db = firestore.client(app=app)

# Function to add a message to Firestore
def add_message_to_firestore(email, message, role):
    user_ref = db.collection('users').document(email)
    messages_ref = user_ref.collection('messages')
    messages_ref.add({
        'message': message,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'role': role
    })

# Function to retrieve messages from Firestore
def get_messages_from_firestore(email):
    user_ref = db.collection('users').document(email)
    messages = user_ref.collection('messages').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    return [msg.to_dict() for msg in messages]


mimetypes.add_type('application/javascript', '.js') 
mimetypes.add_type('text/css', '.css')

openai.api_key = st.secrets['api']

client_id = st.secrets['client']
tenant_id = st.secrets['tenant']
redirect_uri = "http://localhost:8501/"
scopes = ["profile"]
authority = f"https://login.microsoftonline.com/{tenant_id}"
endpoint = "https://graph.microsoft.com/v1.0/me"

os.environ['ENABLED'] = "1"


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
        if (token['idTokenClaims']['preferred_username'].split('@')[-1].strip() in ["nushigh.edu.sg","nus.edu.sg"] and token['idTokenClaims']['preferred_username'][:3] in "anhs"):
            on = st.toggle('Activate Chat', value=os.environ['ENABLED'])
            
            if on:
                os.environ['ENABLED']  = "1"
            else:
                os.environ['ENABLED']  = ""
        token = token if token['idTokenClaims']['preferred_username'].split('@')[-1].strip() in ["nushigh.edu.sg","nus.edu.sg"] else False
        st.text("")
        st.text("")
        temp = st.slider('Temperature', 0.0, 1.0, 0.0)
        if "messages" not in st.session_state.keys():
            print(get_messages_from_firestore(token['idTokenClaims']['preferred_username']))
            st.session_state.messages = []  
            try :
                for msg in get_messages_from_firestore(token['idTokenClaims']['preferred_username']):
                    print(msg)
                    st.session_state.messages.insert(0,{"role": msg["role"], "content": msg["message"]})
            except TypeError:
                pass
            print(st.session_state.messages)


# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])    

st.session_state["openai_model"] = "gpt-3.5-turbo-1106"
if "messages" not in st.session_state.keys():
    st.session_state.messages = []  
    try :
        for msg in get_messages_from_firestore(token['idTokenClaims']['preferred_username']):
            st.session_state.messages.insert(0, {"role": msg["role"], "content": msg["message"]})
    except TypeError:
        pass
# Display chat message
try:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
except AttributeError:
    pass

if prompt := st.chat_input("Your Input (Use /image for image creation)", disabled=not (token and os.environ['ENABLED'])):
    if token:
        print(token)
        user_email = token['idTokenClaims']['preferred_username']
        add_message_to_firestore(user_email, prompt, "user")

    # Append message to local session state
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
    if token:
        add_message_to_firestore(user_email, full_response, "assistant")
    st.session_state.messages.append({"role": "assistant", "content": full_response})
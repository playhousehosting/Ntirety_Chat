import streamlit as st
import requests
import json
import sseclient
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import os

# Dify API configuration
BASE_URL = os.environ.get('DIFY_BASE_URL', "https://bots.chatwithgpt.app/v1")
API_KEY = os.environ.get('DIFY_API_KEY', "app-3wTiB7TV6d1UY3qHf0GL2W5J")

# File handling configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

def handle_file_upload(file, user_id):
    if file is None:
        return {"error": "no_file_uploaded", "message": "A file must be provided"}, 400
    
    if not allowed_file(file.name):
        return {"error": "unsupported_file_type", "message": "Unsupported extension"}, 415
    
    file_size = len(file.getvalue())
    if file_size > MAX_FILE_SIZE:
        return {"error": "file_too_large", "message": f"File size exceeds {MAX_FILE_SIZE/1024/1024}MB limit"}, 413

    url = f"{BASE_URL}/files/upload"
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    
    try:
        files = {
            'file': (file.name, file.getvalue(), f'image/{file.name.rsplit(".", 1)[1].lower()}')
        }
        data = {
            'user': user_id
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        return response.json(), response.status_code
    except Exception as e:
        return {"error": "upload_failed", "message": str(e)}, 500

def send_chat_message(query, user, conversation_id='', inputs=None):
    url = f"{BASE_URL}/chat-messages"
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "inputs": inputs or {},
        "query": query,
        "user": user,
        "response_mode": "streaming"
    }
    
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        client = sseclient.SSEClient(response)
        return client
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None

def set_page_style():
    st.set_page_config(
        page_title="Ntirety Chatbot Beta",
        page_icon="https://store-images.s-microsoft.com/image/apps.14523.bc534f0d-6fce-4ed8-b2f0-753241f88142.9f95a076-5057-472c-aef1-12b77eb3864c.99756f73-ac05-4d71-a9c7-2d31feeb7bd7",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .user-message {
            background-color: #e3f2fd;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .assistant-message {
            background-color: white;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .chat-container {
            max-width: 800px;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    set_page_style()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = ''
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    st.title("Ntirety Chatbot Beta")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an image", type=list(ALLOWED_EXTENSIONS))
    
    # Chat input
    user_input = st.text_input("Type your message here", key="user_input")
    
    # Handle file upload
    if uploaded_file:
        result, status_code = handle_file_upload(uploaded_file, st.session_state.user_id)
        if status_code == 200:
            st.success("File uploaded successfully!")
            if 'id' in result:
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"[Uploaded file: {uploaded_file.name}]",
                    "file_id": result['id']
                })
        else:
            st.error(f"Error uploading file: {result.get('message', 'Unknown error')}")
    
    # Handle text input
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        response_stream = send_chat_message(
            user_input,
            st.session_state.user_id,
            st.session_state.conversation_id
        )
        
        if response_stream:
            message_placeholder = st.empty()
            full_response = ""
            
            for event in response_stream:
                if event.data != '[DONE]':
                    try:
                        data = json.loads(event.data)
                        if 'answer' in data:
                            full_response += data['answer']
                            message_placeholder.markdown(full_response + "▌")
                    except json.JSONDecodeError:
                        continue
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            if not st.session_state.conversation_id and 'conversation_id' in data:
                st.session_state.conversation_id = data['conversation_id']
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

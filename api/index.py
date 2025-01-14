from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import os
import uuid
from typing import Optional, Dict, Any
import base64

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dify API configuration
BASE_URL = os.environ.get('DIFY_BASE_URL', "https://bots.chatwithgpt.app/v1")
API_KEY = os.environ.get('DIFY_API_KEY', "app-3wTiB7TV6d1UY3qHf0GL2W5J")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ntirety Chatbot Beta</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .chat-container { height: calc(100vh - 400px); }
            .suggested-topic {
                transition: all 0.3s ease;
            }
            .suggested-topic:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            .file-upload-area {
                border: 2px dashed #e2e8f0;
                transition: all 0.3s ease;
            }
            .file-upload-area:hover {
                border-color: #93c5fd;
                background-color: #f8fafc;
            }
        </style>
    </head>
    <body class="bg-gray-50">
        <div class="container mx-auto px-4 py-8 max-w-6xl">
            <div class="flex items-center gap-4 mb-8">
                <img src="https://store-images.s-microsoft.com/image/apps.14523.bc534f0d-6fce-4ed8-b2f0-753241f88142.9f95a076-5057-472c-aef1-12b77eb3864c.99756f73-ac05-4d71-a9c7-2d31feeb7bd7" 
                     alt="Ntirety Logo" 
                     class="w-12 h-12 object-contain">
                <h1 class="text-3xl font-bold">Ntirety Chatbot Beta</h1>
            </div>

            <!-- Suggested Topics -->
            <div class="mb-8">
                <h2 class="text-lg font-semibold mb-4">Get started with these topics:</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button onclick="sendSuggestedTopic('How to change CrypSafe password')" 
                            class="suggested-topic bg-white p-4 rounded-lg border border-gray-200 text-left hover:border-blue-500">
                        How to change CrypSafe password
                    </button>
                    <button onclick="sendSuggestedTopic('How to unlock RSA')" 
                            class="suggested-topic bg-white p-4 rounded-lg border border-gray-200 text-left hover:border-blue-500">
                        How to unlock RSA
                    </button>
                    <button onclick="sendSuggestedTopic('How to reset N-central password')" 
                            class="suggested-topic bg-white p-4 rounded-lg border border-gray-200 text-left hover:border-blue-500">
                        How to reset N-central password
                    </button>
                </div>
            </div>

            <!-- Chat Container -->
            <div id="chat-container" class="bg-white rounded-lg shadow-lg p-6 mb-4 chat-container overflow-y-auto"></div>

            <!-- File Upload Area -->
            <div class="mb-4">
                <div class="file-upload-area rounded-lg p-4 text-center cursor-pointer" onclick="document.getElementById('file-input').click()">
                    <p class="text-gray-600 mb-2">Drag and drop file here</p>
                    <p class="text-gray-500 text-sm">Currently only images (PNG, JPG, JPEG, WEBP, GIF) are supported</p>
                    <input type="file" id="file-input" class="hidden" accept="image/*" onchange="handleFileUpload(event)">
                </div>
            </div>

            <!-- Message Input -->
            <div class="flex gap-2">
                <input type="text" id="user-input" class="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                       placeholder="Type your message here...">
                <button onclick="sendMessage()" 
                        class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors">
                    Send
                </button>
            </div>
        </div>

        <script>
            const chatContainer = document.getElementById('chat-container');
            const userInput = document.getElementById('user-input');
            let userId = localStorage.getItem('userId') || generateUUID();
            localStorage.setItem('userId', userId);

            function generateUUID() {
                return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
                    return v.toString(16);
                });
            }

            function appendMessage(content, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `mb-4 ${isUser ? 'text-right' : 'text-left'}`;
                messageDiv.innerHTML = `
                    <div class="${isUser ? 'bg-blue-100 ml-auto' : 'bg-gray-100'} inline-block px-6 py-3 rounded-lg max-w-[70%]">
                        <p class="text-gray-800">${content}</p>
                    </div>
                `;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            async function sendMessage(message = null) {
                const messageText = message || userInput.value.trim();
                if (!messageText) return;

                appendMessage(messageText, true);
                userInput.value = '';

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: messageText,
                            user_id: userId
                        })
                    });

                    const data = await response.json();
                    if (data.error) {
                        appendMessage('Error: ' + data.error, false);
                    } else if (data.response) {
                        appendMessage(data.response, false);
                    } else {
                        appendMessage('Received an invalid response from the server.', false);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    appendMessage('Sorry, there was an error processing your message.', false);
                }
            }

            function sendSuggestedTopic(topic) {
                sendMessage(topic);
            }

            async function handleFileUpload(event) {
                const file = event.target.files[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('file', file);
                formData.append('user_id', userId);

                try {
                    const response = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();
                    if (data.error) {
                        appendMessage('Error uploading file: ' + data.error, false);
                    } else {
                        appendMessage(`Uploaded file: ${file.name}`, true);
                        if (data.response) {
                            appendMessage(data.response, false);
                        }
                    }
                } catch (error) {
                    console.error('Error:', error);
                    appendMessage('Sorry, there was an error uploading the file.', false);
                }
            }

            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            // Add drag and drop support
            const dropArea = document.querySelector('.file-upload-area');
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults (e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                dropArea.addEventListener(eventName, highlight, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, unhighlight, false);
            });

            function highlight(e) {
                dropArea.classList.add('border-blue-500', 'bg-blue-50');
            }

            function unhighlight(e) {
                dropArea.classList.remove('border-blue-500', 'bg-blue-50');
            }

            dropArea.addEventListener('drop', handleDrop, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const file = dt.files[0];
                
                document.getElementById('file-input').files = dt.files;
                handleFileUpload({target: {files: [file]}});
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/chat")
async def chat(request: Request):
    try:
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid JSON data"}
            )

        message = data.get('message')
        user_id = data.get('user_id')

        if not message or not user_id:
            return JSONResponse(
                status_code=400,
                content={"error": "Message and user_id are required"}
            )

        # Call Dify API
        url = f"{BASE_URL}/chat-messages"
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "inputs": {},
            "query": message,
            "user": user_id,
            "response_mode": "blocking"
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            response_data = response.json()
        except requests.RequestException as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to communicate with chat service: {str(e)}"}
            )
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=500,
                content={"error": "Received invalid response from chat service"}
            )

        if 'answer' in response_data:
            return {"response": response_data['answer']}
        else:
            return {"error": "No answer received from the chat service"}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred: {str(e)}"}
        )

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = None):
    if not user_id:
        return JSONResponse(
            status_code=400,
            content={"error": "user_id is required"}
        )

    try:
        # Validate file type
        allowed_types = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}
        content_type = file.content_type or 'application/octet-stream'
        
        if content_type not in allowed_types:
            return JSONResponse(
                status_code=400,
                content={"error": f"File type {content_type} not supported. Allowed types: PNG, JPEG, GIF, WEBP"}
            )

        # Read file content
        try:
            contents = await file.read()
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Failed to read file: {str(e)}"}
            )
        
        # Call Dify API for file upload
        url = f"{BASE_URL}/files/upload"
        headers = {
            'Authorization': f'Bearer {API_KEY}'
        }
        
        files = {
            'file': (file.filename, contents, content_type)
        }
        data = {
            'user': user_id
        }

        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to upload file to chat service: {str(e)}"}
            )

        try:
            response_data = response.json()
            return {"response": "File uploaded successfully", "data": response_data}
        except json.JSONDecodeError:
            if response.status_code == 200:
                return {"response": "File uploaded successfully"}
            else:
                return {"error": "Failed to parse response from chat service"}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred: {str(e)}"}
        )

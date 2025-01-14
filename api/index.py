from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import uuid
from typing import Optional, Dict, Any
import base64
import asyncio
import aiohttp
from sse_starlette.sse import EventSourceResponse

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
BASE_URL = os.environ.get('DIFY_BASE_URL', "http://bots.chatwithgpt.app/v1")
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
                    const eventSource = new EventSource(`/api/chat/stream?message=${encodeURIComponent(messageText)}&user_id=${userId}`);
                    let fullResponse = '';
                    let responseElement = null;

                    eventSource.onmessage = (event) => {
                        try {
                            const data = JSON.parse(event.data);
                            if (data.answer) {
                                fullResponse += data.answer;
                                
                                if (!responseElement) {
                                    responseElement = document.createElement('div');
                                    responseElement.className = 'mb-4 text-left';
                                    responseElement.innerHTML = `
                                        <div class="bg-gray-100 inline-block px-6 py-3 rounded-lg max-w-[70%]">
                                            <p class="text-gray-800 assistant-message">${fullResponse}</p>
                                        </div>
                                    `;
                                    chatContainer.appendChild(responseElement);
                                } else {
                                    const messageP = responseElement.querySelector('.assistant-message');
                                    if (messageP) {
                                        messageP.textContent = fullResponse;
                                    }
                                }
                                
                                chatContainer.scrollTop = chatContainer.scrollHeight;
                            }
                        } catch (error) {
                            console.error('Error parsing message:', error);
                        }
                    };

                    eventSource.addEventListener('error', (event) => {
                        console.error('EventSource error:', event);
                        try {
                            const data = JSON.parse(event.data);
                            appendMessage(`Error: ${data.error}`, false);
                        } catch (e) {
                            appendMessage('Connection error occurred', false);
                        }
                        eventSource.close();
                    });

                    // Close the connection when the response is complete
                    eventSource.addEventListener('done', (event) => {
                        eventSource.close();
                    });

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

@app.get("/api/chat/stream")
async def chat_stream(message: str, user_id: str):
    async def event_generator():
        try:
            url = f"{BASE_URL}/chat-messages"
            headers = {
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "inputs": {},
                "query": message,
                "user": user_id,
                "response_mode": "streaming",
                "conversation_id": ""
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield "event: error\n"
                        yield f"data: {json.dumps({'error': f'API Error: {error_text}'})}\n\n"
                        return

                    # Send a keep-alive comment
                    yield ": keep-alive\n\n"

                    async for line in response.content:
                        if line:
                            try:
                                line_text = line.decode('utf-8').strip()
                                if line_text:
                                    data = json.loads(line_text)
                                    # Send the chat message event
                                    yield "event: message\n"
                                    yield f"data: {json.dumps(data)}\n\n"
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                yield "event: error\n"
                                yield f"data: {json.dumps({'error': f'Processing error: {str(e)}'})}\n\n"

        except Exception as e:
            yield "event: error\n"
            yield f"data: {json.dumps({'error': f'Connection error: {str(e)}'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get('message')
        user_id = data.get('user_id')

        if not message or not user_id:
            return JSONResponse(
                status_code=400,
                content={"error": "Message and user_id are required"}
            )

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

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return JSONResponse(
                        status_code=response.status,
                        content={"error": f"API Error: {error_text}"}
                    )

                response_data = await response.json()
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
        allowed_types = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}
        content_type = file.content_type or 'application/octet-stream'
        
        if content_type not in allowed_types:
            return JSONResponse(
                status_code=400,
                content={"error": f"File type {content_type} not supported. Allowed types: PNG, JPEG, GIF, WEBP"}
            )

        contents = await file.read()
        
        url = f"{BASE_URL}/files/upload"
        headers = {
            'Authorization': f'Bearer {API_KEY}'
        }
        
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field('file', contents, filename=file.filename, content_type=content_type)
            form.add_field('user', user_id)

            async with session.post(url, headers=headers, data=form) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return JSONResponse(
                        status_code=response.status,
                        content={"error": f"Failed to upload file: {error_text}"}
                    )

                try:
                    response_data = await response.json()
                    return {"response": "File uploaded successfully", "data": response_data}
                except json.JSONDecodeError:
                    if response.status == 200:
                        return {"response": "File uploaded successfully"}
                    else:
                        return {"error": "Failed to parse response from chat service"}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred: {str(e)}"}
        )

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests
import json
import os
import uuid
from typing import Optional, Dict, Any

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
        <title>Ntirety Chatbot</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .chat-container { height: calc(100vh - 200px); }
        </style>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold mb-8 text-center">Ntirety Chatbot</h1>
            <div id="chat-container" class="bg-white rounded-lg shadow-lg p-6 mb-4 chat-container overflow-y-auto"></div>
            <div class="flex gap-2">
                <input type="text" id="user-input" class="flex-1 p-2 border rounded" placeholder="Type your message...">
                <button onclick="sendMessage()" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Send</button>
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
                    <div class="${isUser ? 'bg-blue-100 ml-auto' : 'bg-gray-100'} inline-block px-4 py-2 rounded-lg max-w-[70%]">
                        <p class="text-gray-800">${content}</p>
                    </div>
                `;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;

                appendMessage(message, true);
                userInput.value = '';

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            user_id: userId
                        })
                    });

                    const data = await response.json();
                    appendMessage(data.response, false);
                } catch (error) {
                    console.error('Error:', error);
                    appendMessage('Sorry, there was an error processing your message.', false);
                }
            }

            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get('message')
        user_id = data.get('user_id')

        if not message or not user_id:
            raise HTTPException(status_code=400, detail="Message and user_id are required")

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
            "response_mode": "blocking"  # Changed to blocking for simpler implementation
        }

        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        return {
            "response": response_data.get('answer', 'Sorry, I could not process your request.')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

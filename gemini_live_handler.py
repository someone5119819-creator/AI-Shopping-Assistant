"""
Gemini Live API WebSocket Handler - With Enhanced Logging
"""
import os
import json
import asyncio
import websockets
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_WS_URL = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"

from agent_graph import SYSTEM_PROMPT, search_products

class GeminiLiveSession:
    def __init__(self, session_id: str, client_ws):
        self.session_id = session_id
        self.client_ws = client_ws
        self.gemini_ws = None
        self.running = True
        
    async def connect_to_gemini(self):
        """Connect to Gemini Live API"""
        try:
            print(f"[Session {self.session_id}] Connecting to Gemini...")
            self.gemini_ws = await websockets.connect(GEMINI_WS_URL)
            print(f"[Session {self.session_id}] Connected to Gemini WebSocket")
            
            # Send setup - Request BOTH text and audio
            setup = {
                "setup": {
                    "model": "models/gemini-2.0-flash-exp",
                    "generation_config": {
                        "response_modalities": ["TEXT", "AUDIO"],  # Both modalities
                        "speech_config": {
                            "voice_config": {"prebuilt_voice_config": {"voice_name": "Aoede"}}
                        }
                    },
                    "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
                }
            }
            await self.gemini_ws.send(json.dumps(setup))
            print(f"[Session {self.session_id}] Sent setup message")
            
        except Exception as e:
            print(f"[Session {self.session_id}] Gemini connection error: {e}")
            raise
            
    async def handle_client_messages(self):
        """Receive audio from frontend and forward to Gemini"""
        print(f"[Session {self.session_id}] Starting client message handler")
        try:
            async for message in self.client_ws:
                data = json.loads(message)
                
                if data["type"] == "audio" and self.gemini_ws:
                    audio_msg = {
                        "realtime_input": {
                            "media_chunks": [{
                                "mime_type": "audio/pcm",
                                "data": data["data"]
                            }]
                        }
                    }
                    await self.gemini_ws.send(json.dumps(audio_msg))
                    
        except websockets.exceptions.ConnectionClosed:
            self.running = False
        except Exception as e:
            print(f"[Session {self.session_id}] Client handler error: {e}")
            self.running = False
            
    async def handle_gemini_messages(self):
        """Receive responses from Gemini and forward to frontend"""
        print(f"[Session {self.session_id}] Starting Gemini message handler")
        try:
            async for message in self.gemini_ws:
                response = json.loads(message)
                
                # Enhanced logging
                response_type = list(response.keys())[0] if response else "empty"
                print(f"[{self.session_id}] 📩 Gemini: {response_type}")
                
                # Handle server content
                if "serverContent" in response:
                    content = response["serverContent"]
                    
                    if "modelTurn" in content and "parts" in content["modelTurn"]:
                        parts = content["modelTurn"]["parts"]
                        
                        for i, part in enumerate(parts):
                            # Handle audio
                            if "inlineData" in part:
                                audio_data = part["inlineData"]["data"]
                                await self.client_ws.send(json.dumps({
                                    "type": "audio",
                                    "data": audio_data
                                }))
                                print(f"[{self.session_id}] 🔊 Sent {len(audio_data)} chars audio")
                            
                            # Handle text
                            if "text" in part:
                                text = part["text"]
                                await self.client_ws.send(json.dumps({
                                    "type": "transcript",
                                    "role": "assistant",
                                    "text": text
                                }))
                                print(f"[{self.session_id}] 💬 Text: {text[:60]}...")
                                 
                # Setup complete
                if "setupComplete" in response:
                    print(f"[{self.session_id}] ✅ Setup complete")
                    
        except websockets.exceptions.ConnectionClosed:
            self.running = False
        except Exception as e:
            print(f"[Session {self.session_id}] Gemini handler error: {e}")
            self.running = False
            
    async def run(self):
        """Main session loop"""
        try:
            await self.connect_to_gemini()
            await asyncio.gather(
                self.handle_client_messages(),
                self.handle_gemini_messages()
            )
        except Exception as e:
            print(f"[Session {self.session_id}] Session error: {e}")
        finally:
            if self.gemini_ws:
                await self.gemini_ws.close()
            print(f"[Session {self.session_id}] Session ended")

active_sessions: Dict[str, GeminiLiveSession] = {}

async def handle_connection(websocket):
    """Handle new WebSocket connection from frontend"""
    session_id = f"session_{id(websocket)}"
    print(f"\n🔗 New connection: {session_id}")
    
    session = GeminiLiveSession(session_id, websocket)
    active_sessions[session_id] = session
    
    try:
        await session.run()
    finally:
        active_sessions.pop(session_id, None)
        print(f"❌ Connection closed: {session_id}\n")

async def start_server(host="0.0.0.0", port=8002):
    """Start WebSocket server"""
    print(f"🎙️  Gemini Live API Server")
    print(f"   Model: gemini-2.0-flash-exp")
    print(f"   Voice: Aoede")
    print(f"   Listening: ws://{host}:{port}\n")
    
    async with websockets.serve(handle_connection, host, port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(start_server())

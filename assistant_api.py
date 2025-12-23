"""
AI Shopping Assistant API
Provides conversational AI endpoints for voice-based shopping experience
"""
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
CORS(app)

# Store conversation sessions (in-memory for MVP - use Redis in production)
sessions = {}

# System prompt for shopping assistant  
SYSTEM_PROMPT = """ROLE: Specialized Camera & Audio Equipment Consultant
SPECIALTY: High-end video/photography gear.
OBJECTIVE: You must NEITHER suggest products NOR mention brands until you have gathered specific user requirements and performed a search.

CRITICAL PROTOCOL (STRICT STATE MACHINE):

STATE 1: INVESTIGATOR (Default State)
- **Goal**: Understand the user's specific Use Case (e.g., "vlogging", "studio photography", "travel").
- **Constraints**:
  - NEVER mention specific product names or brands (e.g., DO NOT say "GoPro", "Sony", "DSLR").
  - DO NOT say "I can recommend..." yet.
  - ASK 1-2 clarifying questions to narrow down the need.
  - Example Question: "Is this for outdoor adventure or indoor studio use?" (Good - generic)
  - Bad Question: "Do you want a GoPro or a Canon?" (BAD - specific brands)
- **Exit Condition**: When specific needs are clear -> ACTION: SEARCH.

STATE 2: SEARCHER
- **Goal**: Find products matching the CONFIRMED requirements.
- **Action**: Output the JSON search action.
- **Query**: Use broad, semantic terms based on needs (e.g., "waterproof action camera 4k", "professional studio lighting").

STATE 3: PRESENTER (Only active when System Context has results)
- **Goal**: Recommend products from the Search Results.
- **Constraints**:
  - STRICTLY limited to products in the "System Context" below.
  - IF Context is Empty -> "I don't have a product matching those exact specs in stock."
  - NEVER Hallucinate. If it's not in the context, it doesn't exist.
  - Select ONLY top 1-2 best matches. NEVER list more than 2.
  - **Explain WHY**: Explicitly explain why you chose this specific product for their needs (e.g., "I picked this because you mentioned low-light shooting...").

USER PROFILING & MEMORY (New Rule):
- **Listen for Personal Details**: If user mentions their name, hobby, or experience level (e.g., "I'm a beginner", "Hi I'm Alex"), REMEMBER IT.
- **Build Rapport**: Use these details to personalize responses naturally.
  - *User*: "I'm heading to Hawaii for my honeymoon."
  - *Response*: "Hawaii sounds amazing! For a honeymoon trip, you'll want something lightweight..."
- **Small Talk**: Respond warmly to greetings/small talk, but subtly pivot back to their creative needs.

FORBIDDEN TOPICS (Immediate Refusal):
- Software, Code, Computers, General Electronics.
- Response: "I specialize strictly in camera and audio gear."

OUTPUT FORMAT RULES (CRITICAL):
- **NO MARKDOWN**: Do NOT use asterisks (*), bold (**), bullet points (-), or hash marks (#).
- **NATURAL SPEECH**: Write exactly as you would SPEAK. Use full sentences.
- **TONE**: Warm, professional, and conversational. Do not sound robotic.
- **No Lists**: Do not output lists. Describe items naturally in prose.
- **INVISIBLE ACTIONS**: Do NOT say "I am searching" or "Let me check the database" or "Entering search mode". Just say something natural like "Let me see what fits that description..." and then output the action.

FORMAT FOR ACTIONS:
Search: {"action": "search", "query": "generic keywords", "message": "Let me see what we have that matches your needs..."}

System Context (Search Results):
"""

def search_products(query, limit=5):
    """Search products using the existing RAG API"""
    try:
        # Use GET method with query parameters as per api.py specification
        params = {
            'q': query,
            'top_k': limit,
            'use_hybrid': True,
            'semantic_weight': 0.5,
            'keyword_weight': 0.5
        }
        response = requests.get(
            'http://localhost:8000/search',
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            print(f"API returned status {response.status_code}: {response.text}")
        return []
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

def generate_ollama_response(messages):
    """Generate response using local Ollama instance"""
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    model = os.getenv('OLLAMA_MODEL', 'llama3')
    
    try:
        response = requests.post(
            f"{ollama_host}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()['message']['content']
        else:
            return f"Error: Ollama returned status {response.status_code}"
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return "I'm having trouble connecting to my brain. Please make sure Ollama is running."

@app.route('/api/assistant/chat', methods=['POST'])
def chat():
    """Handle chat messages from the user"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize or get session
        if session_id not in sessions:
            sessions[session_id] = {
                'history': [],
                'created_at': datetime.now().isoformat()
            }
        
        session = sessions[session_id]
        
        # Build conversation context for Ollama
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add history
        for msg in session['history'][-10:]:  # Keep last 10 messages for better context
            messages.append({"role": msg['role'], "content": msg['content']})
            
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate AI response
        ai_message = generate_ollama_response(messages)
        
        # Check if AI wants to search for products or place order
        products = None
        order_status = None
        
        if '{"action":' in ai_message and '}' in ai_message:
            try:
                # Extract JSON from response
                start = ai_message.find('{')
                end = ai_message.rfind('}') + 1
                action_data = json.loads(ai_message[start:end])
                
                action = action_data.get('action')
                
                if action == 'search':
                    search_query = action_data.get('query', user_message)
                    products = search_products(search_query)
                    ai_message = action_data.get('message', 'Let me search for that...')
                    
                    # INJECT CONTEXT: Add found products to history so AI "remembers" them
                    if products:
                        product_context = "System Context: Found the following products:\n"
                        for p in products:
                            price = p.get('variants', [{}])[0].get('price', 'N/A')
                            product_context += f"- {p.get('title')} (Price: {price})\n"
                        
                        # Add hidden system message to history
                        session['history'].append({'role': 'system', 'content': product_context})
                    
                elif action == 'add_to_cart':
                    product_name = action_data.get('product', '')
                    if product_name:
                        session['cart'].append({'name': product_name, 'quantity': 1})
                        ai_message = action_data.get('message', f'Added {product_name} to your cart!')
                    
                elif action == 'remove_from_cart':
                    product_name = action_data.get('product', '')
                    session['cart'] = [item for item in session['cart'] if item['name'] != product_name]
                    ai_message = action_data.get('message', f'Removed {product_name} from cart.')
                    
                elif action == 'view_cart':
                    if session['cart']:
                        cart_items = [item['name'] for item in session['cart']]
                        ai_message = f"Your cart has: {', '.join(cart_items)}"
                    else:
                        ai_message = "Your cart is empty."
                    
                elif action == 'place_order':
                    if session['cart']:
                        items = [item['name'] for item in session['cart']]
                        order_status = {
                            'status': 'success',
                            'order_id': f'ORD-{int(datetime.now().timestamp())}',
                            'items': items,
                            'message': f"Order placed successfully! You will receive a confirmation email shortly."
                        }
                        session['cart'] = []  # Clear cart
                        ai_message = order_status['message']
                    else:
                        ai_message = "Your cart is empty. Add some products first!"
                    
                elif action == 'order':
                    items = action_data.get('items', [])
                    # Simulate order placement
                    order_status = {
                        'status': 'success',
                        'order_id': f'ORD-{int(datetime.now().timestamp())}',
                        'items': items,
                        'message': f"Order placed successfully for {', '.join(items)}! You will receive a confirmation email shortly."
                    }
                    ai_message = action_data.get('message', 'Placing your order now...')
                    
            except json.JSONDecodeError:
                pass  # If JSON parsing fails, just continue with the text response
        
        # Add to session history
        session['history'].append({'role': 'user', 'content': user_message})
        session['history'].append({'role': 'assistant', 'content': ai_message})
        
        # Prepare response
        response_data = {
            'message': ai_message,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }
        
        if products:
            response_data['products'] = products
            
        if order_status:
            response_data['order'] = order_status
            # If order successful, append the success message to the response text so user hears/sees it
            response_data['message'] = order_status['message']
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assistant/session/new', methods=['POST'])
def new_session():
    """Create a new conversation session"""
    session_id = f"session_{datetime.now().timestamp()}"
    sessions[session_id] = {
        'history': [],
        'created_at': datetime.now().isoformat()
    }
    return jsonify({'session_id': session_id})

@app.route('/api/assistant/session/<session_id>', methods=['DELETE'])
def end_session(session_id):
    """End a conversation session"""
    if session_id in sessions:
        del sessions[session_id]
    return jsonify({'status': 'success'})

@app.route('/api/assistant/tts', methods=['POST'])
def tts():
    """Text-to-Speech proxy for ElevenLabs"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
            
        api_key = os.getenv('ELEVENLABS_API_KEY')
        voice_id = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM') # Default to Rachel
        
        if not api_key:
             return jsonify({'error': 'ElevenLabs API key not configured'}), 500

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.content, 200, {'Content-Type': 'audio/mpeg'}
        else:
            return jsonify({'error': f"ElevenLabs API error: {response.text}"}), response.status_code
            
    except Exception as e:
        print(f"Error in TTS endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assistant/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'backend': 'ollama',
        'model': os.getenv('OLLAMA_MODEL', 'llama3'),
        'active_sessions': len(sessions)
    })

if __name__ == '__main__':
    port = int(os.getenv('ASSISTANT_PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=True)

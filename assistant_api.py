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

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
CORS(app)

# Store conversation sessions (in-memory for MVP - use Redis in production)
sessions = {}

# Initialize Multi-Agent System
from agents.orchestrator import OrchestratorAgent

# Note: Orchestrator will be initialized per session to maintain state

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

STATE 2: SEARCHER (never show the stage in the response)
- **Goal**: Find products matching the CONFIRMED requirements.
- **Multi-Category Detection**: 
  - If user wants MULTIPLE distinct product types (e.g., "camera + tripod + mic"), use multi_search action.
  - Break down into specific category queries (e.g., ["camera for vlogging", "tripod lightweight", "microphone shotgun"]).
  - If SINGLE product type: use regular search action.
- **Action Output**:
  - Single: {"action": "search", "query": "keywords", "message": "natural bridge"}
  - Multi: {"action": "multi_search", "categories": ["query1", "query2"], "message": "natural bridge"}


STATE 3: PRESENTER (Only active when System Context has results)
- **Goal**: Recommend products from the Search Results.
- **ABSOLUTE CONSTRAINTS (ZERO KNOWLEDGE RULE)**:
  - You have ZERO knowledge of products outside the "System Context" below.
  - You CANNOT recommend products from memory, training data, or general knowledge.
  - IF a product name is NOT explicitly listed in "System Context", IT DOES NOT EXIST.
  - ONLY mention products by their EXACT title as shown in "System Context".
  - If Context is Empty → "I don't have any products matching that description in stock."
  - Select ONLY top 1-2 best matches from the System Context. NEVER list more than 2.

MANDATORY REASONING (CRITICAL):
- For EVERY product you mention, you MUST immediately explain WHY it's the best choice.
- Format: "The [Product Name] because [specific reason tied to user's needs]"
- Example: "The Sony A7 IV because you mentioned needing excellent low-light performance and 4K video"
- DO NOT just list products. ALWAYS pair product name with reasoning in the SAME sentence.
- Reasoning must reference specific user needs, use cases, or requirements they mentioned.

CRITICAL VALIDATION:
- Before recommending ANY product, verify its EXACT title exists in "System Context".
- If unsure whether a product exists in the context, DO NOT mention it.
- Generic brand names without specific products in context = FORBIDDEN.


USER PROFILING & MEMORY:
CRITICAL: These are EXAMPLE SCENARIOS ONLY. Do NOT assume any user is named "Alex" or going to "Hawaii" unless THEY explicitly tell you.
- **Listen for Personal Details**: If THIS user mentions their name, hobby, or experience level, REMEMBER IT.
- **Build Rapport**: Use details THEY provide to personalize responses naturally.
- **Small Talk**: Respond warmly to greetings/small talk, but subtly pivot back to their creative needs.
- **NEVER assume information**: Only use details the CURRENT user explicitly provides in THIS conversation.

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

CRITICAL REMINDER BEFORE PRESENTING:
- Maximum 2 products. If you present 3 or more, you have FAILED.
- Each recommendation MUST include "I chose this because..." reasoning.

System Context (Search Results):
"""

def search_products(query, limit=3):
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
            results = response.json().get('results', [])
            # Filter low-relevance results (garbage filter)
            # Valid matches usually > 0.15. Absolute garbage is often < 0.1
            high_quality_results = [
                r for r in results 
                if r.get('hybrid_score', 0) > 0.1
            ]
            
            if len(high_quality_results) < len(results):
                logger.info(f"Filtered {len(results) - len(high_quality_results)} low-quality results")
                
            return high_quality_results
        else:
            logger.error(f"RAG API returned status {response.status_code}: {response.text}")
        return []
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return []

def multi_category_search(categories):
    """
    Execute parallel searches for multiple product categories.
    Returns top 1 result per category.
    
    Args:
        categories: List of search queries (e.g., ["camera for vlogging", "tripod lightweight"])
    
    Returns:
        List of top products, one per category
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = []
    
    # Optimize: Use parallel execution for multiple categories
    with ThreadPoolExecutor(max_workers=min(len(categories), 5)) as executor:
        # Submit all searches in parallel
        future_to_category = {
            executor.submit(search_products, category, 3): category 
            for category in categories
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_category):
            try:
                products = future.result()
                if products:
                    results.append(products[0])  # Take top 1 per category
            except Exception as e:
                logger.error(f"Error searching category: {e}")
    
    return results


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
        logger.error(f"Ollama connection error: {e}")
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
        
        # Get or create session
        if session_id not in sessions:
            sessions[session_id] = {
                'id': session_id,
                'history': [],
                'created_at': datetime.now().isoformat(),
                'orchestrator': None  # Will initialize on first use
            }
        
        session = sessions[session_id]
        
        # Initialize orchestrator if not exists
        if not session['orchestrator']:
            session['orchestrator'] = OrchestratorAgent(
                ollama_generator=generate_ollama_response,
                search_function=search_products,
                multi_search_function=multi_category_search
            )
        
        orchestrator = session['orchestrator']
        
        # Build context for orchestrator
        context = {
            'user_message': user_message,
            'history': session['history']
        }
        
        # Process through multi-agent system
        result = orchestrator.process(context)
        
        ai_message = result.get('response', 'I apologize, I encountered an issue.')
        products = result.get('products', [])
        
        # Add to session history
        session['history'].append({'role': 'user', 'content': user_message})
        session['history'].append({'role': 'assistant', 'content': ai_message})
        
        # Prepare response
        response_data = {
            'message': ai_message,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'products': products if products else []
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
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
        logger.error(f"Error in TTS endpoint: {e}", exc_info=True)
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

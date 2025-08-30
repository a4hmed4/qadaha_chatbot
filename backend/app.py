import yaml
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import MongoClient
from lang_graph import MathRagGraph
import uuid

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# MongoDB connection
try:
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongodb_uri)
    db = client['qadaha_chatbot']
    users_collection = db['users']
    conversations_collection = db['conversations']
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

def load_config():
    """Load configuration from YAML file."""
    try:
        with open("config.yaml", 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading config file: {str(e)}")
        raise

# Load configuration and initialize the MathRagGraph
try:
    config = load_config()
    # Initialize graph with config file
    rag_graph = MathRagGraph("config.yaml")
    logger.info("Successfully initialized Math Problems Bot with LangGraph")
except Exception as e:
    logger.error(f"Failed to initialize Math Problems Bot: {str(e)}")
    raise

# Display database statistics for diagnostics
try:
    total_docs = rag_graph.document_retriever.collection.count_documents({})
    logger.info(f"Total documents in MongoDB collection: {total_docs}")

    # Sample documents for validation
    sample_docs = list(rag_graph.document_retriever.collection.find({}).limit(2))
    logger.info(f"Sample document fields: {list(sample_docs[0].keys()) if sample_docs else 'No documents found'}")
except Exception as e:
    logger.error(f"Error checking database statistics: {str(e)}")

def create_user():
    """Create a new user and return user ID."""
    try:
        user_id = str(uuid.uuid4())
        user_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'last_active': datetime.utcnow(),
            'total_conversations': 0,
            'total_messages': 0
        }
        users_collection.insert_one(user_data)
        logger.info(f"Created new user: {user_id}")
        return user_id
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise

def get_or_create_user(user_id=None):
    """Get existing user or create new one."""
    if user_id:
        user = users_collection.find_one({'user_id': user_id})
        if user:
            # Update last active
            users_collection.update_one(
                {'user_id': user_id},
                {'$set': {'last_active': datetime.utcnow()}}
            )
            return user_id
        else:
            logger.warning(f"User {user_id} not found, creating new user")
    
    return create_user()

def save_conversation(user_id, conversation_data):
    """Save conversation to database."""
    try:
        conversation = {
            'user_id': user_id,
            'title': conversation_data.get('title', 'محادثة جديدة'),
            'messages': conversation_data['messages'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'message_count': len(conversation_data['messages'])
        }
        
        result = conversations_collection.insert_one(conversation)
        conversation_id = str(result.inserted_id)
        
        # Update user statistics
        users_collection.update_one(
            {'user_id': user_id},
            {
                '$inc': {
                    'total_conversations': 1,
                    'total_messages': len(conversation_data['messages'])
                }
            }
        )
        
        logger.info(f"Saved conversation {conversation_id} for user {user_id}")
        return conversation_id
    except Exception as e:
        logger.error(f"Error saving conversation: {str(e)}")
        raise

def update_conversation(conversation_id, messages):
    """Update existing conversation with new messages."""
    try:
        conversations_collection.update_one(
            {'_id': ObjectId(conversation_id)},
            {
                '$set': {
                    'messages': messages,
                    'updated_at': datetime.utcnow(),
                    'message_count': len(messages)
                }
            }
        )
        logger.info(f"Updated conversation {conversation_id}")
    except Exception as e:
        logger.error(f"Error updating conversation: {str(e)}")
        raise

def get_user_conversations(user_id, limit=50):
    """Get user's conversation history."""
    try:
        conversations = list(conversations_collection.find(
            {'user_id': user_id},
            {
                '_id': 1,
                'title': 1,
                'created_at': 1,
                'updated_at': 1,
                'message_count': 1
            }
        ).sort('updated_at', -1).limit(limit))
        
        # Convert ObjectId to string
        for conv in conversations:
            conv['_id'] = str(conv['_id'])
            conv['created_at'] = conv['created_at'].isoformat()
            conv['updated_at'] = conv['updated_at'].isoformat()
        
        return conversations
    except Exception as e:
        logger.error(f"Error getting user conversations: {str(e)}")
        return []

def get_conversation(conversation_id):
    """Get specific conversation by ID."""
    try:
        conversation = conversations_collection.find_one({'_id': ObjectId(conversation_id)})
        if conversation:
            conversation['_id'] = str(conversation['_id'])
            conversation['created_at'] = conversation['created_at'].isoformat()
            conversation['updated_at'] = conversation['updated_at'].isoformat()
        return conversation
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        return None

def delete_conversation(conversation_id, user_id):
    """Delete conversation."""
    try:
        result = conversations_collection.delete_one({
            '_id': ObjectId(conversation_id),
            'user_id': user_id
        })
        if result.deleted_count > 0:
            logger.info(f"Deleted conversation {conversation_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return False

@app.route('/chat', methods=['POST'])
def chat():
    try:
        logger.debug("Received chat request")
        data = request.get_json()
        logger.debug(f"Request data: {data}")
        
        if not data or 'message' not in data:
            logger.warning("Invalid request: message is missing")
            return jsonify({'error': 'Message is required'}), 400
        
        user_input = data['message']
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        
        # Get or create user
        user_id = get_or_create_user(user_id)
        
        # Get conversation history
        conversation_history = []
        if conversation_id:
            conversation = get_conversation(conversation_id)
            if conversation and conversation['user_id'] == user_id:
                conversation_history = conversation['messages']
            else:
                conversation_id = None
        
        # Process the chat request
        response = rag_graph.chat(
            message=user_input,
            conversation_history=conversation_history
        )
        
        # Create new message
        new_message = {
            'id': str(uuid.uuid4()),
            'text': user_input,
            'sender': 'user',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        bot_message = {
            'id': str(uuid.uuid4()),
            'text': response,
            'sender': 'bot',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Update conversation
        updated_messages = conversation_history + [new_message, bot_message]
        
        if conversation_id:
            update_conversation(conversation_id, updated_messages)
        else:
            # Create new conversation
            conversation_data = {
                'title': user_input[:50] + '...' if len(user_input) > 50 else user_input,
                'messages': updated_messages
            }
            conversation_id = save_conversation(user_id, conversation_data)
        
        # Log the response length
        logger.info(f"Generated response of length: {len(response)} characters")
        
        # Create response data
        response_data = {
            'response': response,
            'status': 'success',
            'user_id': user_id,
            'conversation_id': conversation_id,
            'message_id': bot_message['id']
        }
        
        # Use Flask's Response directly with proper encoding
        result = app.response_class(
            response=json.dumps(response_data, ensure_ascii=False).encode('utf-8'),
            status=200,
            mimetype='application/json'
        )
        result.headers['Content-Type'] = 'application/json; charset=utf-8'
        
        return result
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/conversations', methods=['GET'])
def get_conversations():
    """Get user's conversation history."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        conversations = get_user_conversations(user_id)
        return jsonify({
            'conversations': conversations,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation_by_id(conversation_id):
    """Get specific conversation."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        conversation = get_conversation(conversation_id)
        if not conversation or conversation['user_id'] != user_id:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify({
            'conversation': conversation,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation_endpoint(conversation_id):
    """Delete conversation."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        success = delete_conversation(conversation_id, user_id)
        if not success:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify({
            'message': 'Conversation deleted successfully',
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/users', methods=['POST'])
def create_user_endpoint():
    """Create new user."""
    try:
        user_id = create_user()
        return jsonify({
            'user_id': user_id,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Check MongoDB connection
        client.admin.command('ping')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'mongodb': 'connected',
                'rag_graph': 'initialized'
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
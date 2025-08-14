import yaml
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
from lang_graph import MathRagGraph

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

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
        conversation_history = data.get('conversation_history', [])
        session_id = data.get('session_id')
        
        # Process the chat request
        response = rag_graph.chat(
            message=user_input,
            conversation_history=conversation_history
        )
        
        # Log the response length
        logger.info(f"Generated response of length: {len(response)} characters")
        
        # Create response data
        response_data = {
            'response': response,
            'status': 'success'
        }
        
        if session_id:
            response_data['session_id'] = session_id
        
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
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
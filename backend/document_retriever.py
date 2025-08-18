import logging
import numpy as np
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DocumentRetriever:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the DocumentRetriever with configuration."""
        self.config = config
        
        # Connect to MongoDB
        self.client = MongoClient(config.get('mongo_connection_str'))
        self.db = self.client[config.get('database_name')]
        self.collection = self.db[config.get('collection_name')]
        
        # Initialize the embedding model
        self.embedding_model = SentenceTransformer(config.get('embedding_model'))
    
    def compute_cosine_similarity(self, vec1, vec2):
        """Compute cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)
    
    def retrieve(self, query: str, k: int = 5, score_threshold: float = 0.35, query_type: str = "general") -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents based on the mathematical query.
        
        Args:
            query: The search query for mathematical problems
            k: Number of documents to retrieve
            score_threshold: Similarity threshold for retrieval
            query_type: Type of query (e.g., "جبري", "هندسي", "تحية")
            
        Returns:
            List of retrieved documents containing mathematical content
        """
        logger.info(f"Retrieving documents for query: {query} (k={k}, threshold={score_threshold}, type={query_type})")
        
        # إذا كان نوع الاستعلام هو تحية، نعيد قائمة فارغة لأننا لا نحتاج إلى استرجاع وثائق
        if query_type == "تحية":
            logger.info("Query is a greeting, returning empty document list")
            return []
        
        try:
            query_embedding = self.embedding_model.encode(query)
            
            # Get all documents from MongoDB
            all_docs = list(self.collection.find({}, {
                'content': 1, 
                'embedding': 1, 
                'source_filename': 1
            }))
            
            # Compute similarities
            similarities = []
            
            for doc in all_docs:
                # Calculate base similarity
                similarity = self.compute_cosine_similarity(query_embedding, doc['embedding'])
                
                # Analyze for exact matches of important words and mathematical terms
                query_lower = query.lower()
                content_lower = doc['content'].lower()
                
                # Count exact matches of important words
                exact_matches = 0
                important_words = set(word for word in query_lower.split() if len(word) > 2)
                
                # Mathematical terms that should get higher boost
                math_terms = ['معادلة', 'مثلث', 'زاوية', 'مربع', 'دائرة', 'مستطيل', 'متوازي', 'قطر', 'محيط', 'مساحة', 'حجم', 'جذر', 'لوغاريتم', 'اشتقاق', 'تكامل', 'مصفوفة', 'متجه', 'احتمال', 'إحصاء']
                
                for word in important_words:
                    if word in content_lower:
                        exact_matches += 1
                        # Give extra boost for mathematical terms
                        if any(term in word for term in math_terms):
                            exact_matches += 1
                
                # Boost similarity for exact matches
                if exact_matches > 0:
                    boost = min(exact_matches * 0.05, 0.25)
                    similarity += boost
                
                # Store document with similarity score
                if similarity >= score_threshold:
                    doc['similarity'] = similarity
                    similarities.append(doc)
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top k results
            return similarities[:k]
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
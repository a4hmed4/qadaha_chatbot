import logging
from typing import Dict, Any, List
import os

logger = logging.getLogger(__name__)

class ContextProcessor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the ContextProcessor with configuration."""
        self.config = config
    
    def process(self, query: str, documents: List[Dict[str, Any]], query_type: str = "general") -> str:
        """
        Process the retrieved documents into a coherent context.
        
        Args:
            query: The original query
            documents: The retrieved documents
            query_type: The type of query (factual, conceptual, etc.)
            
        Returns:
            Formatted context string
        """
        logger.info(f"Processing context for {len(documents)} documents")
        
        if not documents:
            return "لم أجد معلومات كافية للإجابة على سؤالك."
        
        # Format contexts based on document type
        formatted_contexts = []
        
        for doc in documents:
            context_text = doc.get('content', '')
            metadata = []
            
            # Add source information if available
            if doc.get('source_filename'):
                # Extract page number and side from filename
                filename = doc.get('source_filename')
                base_name = os.path.basename(filename) if filename else ''
                metadata.append(f"المصدر: {base_name}")
            
            # Format the document with metadata
            if metadata:
                formatted_doc = f"[{' - '.join(metadata)}]\n{context_text}"
            else:
                formatted_doc = context_text
            
            # Add similarity score if available
            if 'similarity' in doc:
                formatted_doc += f"\n[درجة التطابق: {doc['similarity']:.2f}]"
            
            formatted_contexts.append(formatted_doc)
        
        # Combine all formatted contexts
        combined_context = "\n\n".join(formatted_contexts)
        
        # Add a summary section for all query types
        summary = f"فيما يلي المعلومات المتاحة حول المسألة الرياضية: '{query}'\n\n"
        combined_context = summary + combined_context
        
        return combined_context
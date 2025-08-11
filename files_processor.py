import os
from typing import List, Dict
import logging
from pymongo import MongoClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self, mongodb_uri: str = "mongodb://localhost:27017/", config_path: str = "config.yaml"):
        """Initialize TextProcessor with MongoDB connection."""
        # Load config file
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            
        self.client = MongoClient(self.config['mongo_connection_str'])
        self.db = self.client[self.config['database_name']]
        self.collection = self.db[self.config['collection_name']]
        
        self.model = SentenceTransformer(self.config['embedding_model'])
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300
        )

    def process_files_directory(self, files_dir: str) -> List[Dict]:
        """Process all text files in a directory and return their chunks with embeddings."""
        processed_chunks = []
        
        # Create files directory if it doesn't exist
        if not os.path.exists(files_dir):
            os.makedirs(files_dir)
            logger.warning(f"Created directory {files_dir} as it did not exist.")
            return processed_chunks
        
        # Get all text files
        txt_files = [f for f in os.listdir(files_dir) if f.endswith('.txt')]
        
        if not txt_files:
            logger.warning(f"No TXT files found in {files_dir}")
            return processed_chunks
            
        logger.info(f"Found {len(txt_files)} text files in {files_dir}")
        
        # Process each file
        for file_name in txt_files:
            file_path = os.path.join(files_dir, file_name)
            try:
                logger.info(f"Processing TXT file: {file_name}")
                chunks = self._process_text_file(file_path)
                
                processed_chunks.extend(chunks)
                logger.info(f"Successfully processed {file_name}")
            except Exception as e:
                logger.error(f"Error processing {file_name}: {str(e)}")
                continue
        
        return processed_chunks

    def _process_text_file(self, txt_path: str) -> List[Dict]:
        """Process a single TXT file and return chunks with embeddings."""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
                
                # Chunk the document
                chunks = self.text_splitter.split_text(text_content)
                
                processed_chunks = []
                for i, chunk_text in enumerate(chunks):
                    embedding = self.model.encode(chunk_text)
                    embedding_list = embedding.tolist()
                    
                    processed_chunk = {
                        "content": chunk_text,
                        "embedding": embedding_list,
                        "metadata": {
                            "source": txt_path,
                            "chunk_index": i
                        },
                        "type": "txt",
                        "source_file": os.path.basename(txt_path)
                    }
                    processed_chunks.append(processed_chunk)
                
                return processed_chunks
        except Exception as e:
            logger.error(f"Error reading or processing text file {txt_path}: {str(e)}")
            return []

    def save_to_mongodb(self, chunks: List[Dict]) -> None:
        """Save processed chunks to MongoDB."""
        if not chunks:
            logger.warning("No chunks to save")
            return
        
        try:
            self.collection.create_index([("embedding", "2dsphere")])
            
            result = self.collection.insert_many(chunks)
            logger.info(f"Successfully saved {len(result.inserted_ids)} chunks to MongoDB")
        except Exception as e:
            logger.error(f"Error saving to MongoDB: {str(e)}")

    def process_and_save_files(self, files_dir: str) -> None:
        """Process all text files in directory and save to MongoDB."""
        chunks = self.process_files_directory(files_dir)
        if chunks:
            self.save_to_mongodb(chunks)
        else:
            logger.info(f"No chunks to save from {files_dir}")

def main():
    processor = TextProcessor()
    files_dir = "resources"
    processor.process_and_save_files(files_dir)

if __name__ == "__main__":
    main()
"""
Embeddings module for generating vector representations of text.
Uses Sentence Transformers for local embedding generation.
"""
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from config import config


class EmbeddingGenerator:
    """Generate embeddings using Sentence Transformers."""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name or config.EMBEDDING_MODEL
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print(f"Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding vectors
        """
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        print(f"Generated {len(embeddings)} embeddings")
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        return self.model.get_sentence_embedding_dimension()


def main():
    """Test the embedding generator."""
    generator = EmbeddingGenerator()
    
    # Test with sample texts
    texts = [
        "Premium leather wallet with RFID protection",
        "Wireless Bluetooth headphones with noise cancellation",
        "Organic cotton t-shirt in multiple colors"
    ]
    
    embeddings = generator.generate_embeddings(texts)
    
    print(f"\n--- Embedding Stats ---")
    print(f"Number of embeddings: {len(embeddings)}")
    print(f"Embedding dimension: {len(embeddings[0])}")
    print(f"First embedding (first 10 values): {embeddings[0][:10]}")


if __name__ == "__main__":
    main()

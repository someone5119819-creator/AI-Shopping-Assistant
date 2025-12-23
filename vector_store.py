"""
Vector store using ChromaDB for storing and searching product embeddings.
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from config import config
from embeddings import EmbeddingGenerator


class VectorStore:
    """Manage vector storage and similarity search using ChromaDB."""
    
    def __init__(self, collection_name: Optional[str] = None):
        """
        Initialize the vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name or config.COLLECTION_NAME
        self.persist_directory = config.CHROMA_PERSIST_DIRECTORY
        
        # Initialize ChromaDB client
        print(f"Initializing ChromaDB at {self.persist_directory}")
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding function
        self.embedding_generator = EmbeddingGenerator()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Shopify product embeddings"}
        )
        
        print(f"Collection '{self.collection_name}' ready. Contains {self.collection.count()} documents")
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 100
    ):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents with 'text' and 'metadata' keys
            batch_size: Batch size for processing
        """
        if not documents:
            print("No documents to add")
            return
        
        print(f"Adding {len(documents)} documents to vector store...")
        
        # Extract texts and metadata
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        ids = [doc["metadata"]["product_id"] for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_generator.generate_embeddings(
            texts,
            batch_size=batch_size
        )
        
        # Add to ChromaDB in batches
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            
            # Convert metadata to strings where needed (ChromaDB requirement)
            batch_metadata = []
            for meta in metadatas[i:end_idx]:
                clean_meta = {}
                for key, value in meta.items():
                    if value is None:
                        continue
                    elif isinstance(value, (str, int, float, bool)):
                        clean_meta[key] = value
                    else:
                        clean_meta[key] = str(value)
                batch_metadata.append(clean_meta)
            
            self.collection.add(
                embeddings=embeddings[i:end_idx],
                documents=texts[i:end_idx],
                metadatas=batch_metadata,
                ids=ids[i:end_idx]
            )
            print(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        print(f"Successfully added {len(documents)} documents")
        print(f"Total documents in collection: {self.collection.count()}")
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where_filter: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Search for similar products using semantic search.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            where_filter: Optional metadata filter (e.g., {"vendor": "Nike"})
            
        Returns:
            Search results with documents, metadata, and distances
        """
        print(f"Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        formatted_results = {
            "query": query,
            "results": []
        }
        
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                formatted_results["results"].append({
                    "product_id": results["ids"][0][i],
                    "title": results["metadatas"][0][i].get("title", ""),
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                    "relevance_score": 1 - (results["distances"][0][i] if "distances" in results else 0)
                })
        
        print(f"Found {len(formatted_results['results'])} results")
        return formatted_results
    
    def delete_collection(self):
        """Delete the entire collection."""
        self.client.delete_collection(name=self.collection_name)
        print(f"Deleted collection '{self.collection_name}'")
    
    def reset_collection(self):
        """Reset the collection by deleting and recreating it."""
        self.delete_collection()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Shopify product embeddings"}
        )
        print(f"Reset collection '{self.collection_name}'")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "collection_name": self.collection_name,
            "total_documents": self.collection.count(),
            "persist_directory": self.persist_directory
        }


def main():
    """Test the vector store."""
    from data_processor import ProductDataProcessor
    import json
    
    # Load and process products
    with open("products.json", "r", encoding="utf-8") as f:
        products = json.load(f)
    
    processor = ProductDataProcessor()
    documents = processor.process_products(products[:10])  # Test with first 10
    
    # Initialize vector store
    store = VectorStore()
    
    # Option to reset
    # store.reset_collection()
    
    # Add documents
    store.add_documents(documents)
    
    # Test search
    results = store.search("leather wallet", n_results=3)
    
    print("\n--- Search Results ---")
    for i, result in enumerate(results["results"], 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Relevance: {result['relevance_score']:.3f}")
        print(f"   Price: ${result['metadata'].get('price', 'N/A')}")


if __name__ == "__main__":
    main()

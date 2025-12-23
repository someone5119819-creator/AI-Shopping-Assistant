"""
Keyword-based search using BM25 algorithm.
Provides field-specific search with configurable weights.
"""
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
import re
from collections import defaultdict


class KeywordSearchEngine:
    """BM25-based keyword search with field weighting."""
    
    def __init__(self, documents: List[Dict[str, Any]], field_weights: Optional[Dict[str, float]] = None):
        """
        Initialize keyword search engine.
        
        Args:
            documents: List of documents with text and metadata
            field_weights: Weight for each field (higher = more important)
        """
        self.documents = documents
        self.field_weights = field_weights or {
            "title": 3.0,
            "description": 2.0,
            "tags": 1.5,
            "vendor": 1.0,
            "product_type": 1.0
        }
        
        # Build BM25 indexes for each field
        self.bm25_indexes = {}
        self.tokenized_docs = {}
        
        self._build_indexes()
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of lowercase tokens
        """
        if not text:
            return []
        
        # Convert to lowercase and split on non-alphanumeric
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def _build_indexes(self):
        """Build BM25 indexes for each field."""
        # Group documents by field
        field_texts = defaultdict(list)
        
        for doc in self.documents:
            metadata = doc.get("metadata", {})
            
            # Extract each field
            for field in self.field_weights.keys():
                text = metadata.get(field, "")
                if isinstance(text, str):
                    field_texts[field].append(text)
                else:
                    field_texts[field].append("")
        
        # Build BM25 index for each field
        for field, texts in field_texts.items():
            tokenized = [self._tokenize(text) for text in texts]
            self.tokenized_docs[field] = tokenized
            
            # Only create BM25 index if we have valid tokens
            if tokenized and any(tokens for tokens in tokenized):
                # Filter out empty tokenized documents
                non_empty_tokenized = [tokens if tokens else ["empty"] for tokens in tokenized]
                self.bm25_indexes[field] = BM25Okapi(non_empty_tokenized)
            else:
                # No valid tokens, skip this field
                self.bm25_indexes[field] = None
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        field_weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search using BM25 across all fields with weighting.
        
        Args:
            query: Search query
            top_k: Number of results to return
            field_weights: Optional custom field weights for this query
            
        Returns:
            List of documents with keyword scores
        """
        if not query.strip():
            return []
        
        weights = field_weights or self.field_weights
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []
        
        # Calculate scores for each field
        field_scores = {}
        for field, bm25 in self.bm25_indexes.items():
            if bm25 is not None:  # Only process if BM25 index exists
                scores = bm25.get_scores(query_tokens)
                field_scores[field] = scores
        
        # Combine scores with field weights
        final_scores = []
        for i in range(len(self.documents)):
            weighted_score = 0.0
            field_breakdown = {}
            
            for field, scores in field_scores.items():
                field_score = scores[i] if i < len(scores) else 0.0
                weight = weights.get(field, 1.0)
                weighted_score += field_score * weight
                field_breakdown[field] = field_score
            
            final_scores.append({
                "index": i,
                "score": weighted_score,
                "field_breakdown": field_breakdown
            })
        
        # Sort by score
        final_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top k results
        results = []
        for score_info in final_scores[:top_k]:
            if score_info["score"] > 0:  # Only include non-zero scores
                doc = self.documents[score_info["index"]]
                results.append({
                    "document": doc,
                    "keyword_score": score_info["score"],
                    "field_scores": score_info["field_breakdown"]
                })
        
        return results
    
    def search_field(
        self,
        query: str,
        field: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search in a specific field only.
        
        Args:
            query: Search query
            field: Field to search in
            top_k: Number of results
            
        Returns:
            List of documents with scores
        """
        if field not in self.bm25_indexes:
            return []
        
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        bm25 = self.bm25_indexes[field]
        scores = bm25.get_scores(query_tokens)
        
        # Create results
        results = []
        for i, score in enumerate(scores):
            if score > 0:
                results.append({
                    "index": i,
                    "score": score,
                    "document": self.documents[i]
                })
        
        # Sort and return top k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def get_field_matches(self, query: str, document_index: int) -> Dict[str, float]:
        """
        Get match scores for each field for a specific document.
        
        Args:
            query: Search query
            document_index: Index of document
            
        Returns:
            Dictionary of field scores
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return {}
        
        field_matches = {}
        for field, bm25 in self.bm25_indexes.items():
            scores = bm25.get_scores(query_tokens)
            if document_index < len(scores):
                field_matches[field] = scores[document_index]
        
        return field_matches


def main():
    """Test the keyword search engine."""
    # Sample documents
    documents = [
        {
            "text": "Premium wireless headphones with noise cancellation",
            "metadata": {
                "title": "Wireless Bluetooth Headphones",
                "description": "Premium wireless headphones with noise cancellation and long battery life",
                "tags": "audio, wireless, bluetooth, headphones",
                "vendor": "AudioTech",
                "product_type": "Electronics"
            }
        },
        {
            "text": "LED ring light for photography",
            "metadata": {
                "title": "LED Ring Light",
                "description": "Professional LED ring light for photography and video streaming",
                "tags": "photography, lighting, LED, studio",
                "vendor": "PhotoPro",
                "product_type": "Photography"
            }
        }
    ]
    
    # Create search engine
    engine = KeywordSearchEngine(documents)
    
    # Test search
    print("=== Keyword Search Test ===\n")
    
    query = "wireless headphones"
    results = engine.search(query, top_k=5)
    
    print(f"Query: '{query}'")
    print(f"Found {len(results)} results\n")
    
    for i, result in enumerate(results, 1):
        meta = result["document"]["metadata"]
        print(f"{i}. {meta['title']}")
        print(f"   Score: {result['keyword_score']:.2f}")
        print(f"   Field scores: {result['field_scores']}")
        print()


if __name__ == "__main__":
    main()

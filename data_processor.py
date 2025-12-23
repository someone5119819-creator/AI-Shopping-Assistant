"""
Data processor for Shopify products.
Converts raw product data into searchable text chunks with metadata.
"""
from typing import List, Dict, Any
import json


class ProductDataProcessor:
    """Process Shopify product data for embedding generation."""
    
    def __init__(self):
        """Initialize the data processor."""
        pass
    
    def extract_product_text(self, product: Dict) -> str:
        """
        Extract searchable text from a product.
        
        Args:
            product: Product dictionary from Shopify API
            
        Returns:
            Combined text representation of the product
        """
        parts = []
        
        # Title
        if product.get("title"):
            parts.append(f"Title: {product['title']}")
        
        # Description (strip HTML)
        if product.get("body_html"):
            # Simple HTML strip - in production, use a library like BeautifulSoup
            description = product["body_html"]
            description = description.replace("<br>", " ").replace("<br/>", " ")
            description = description.replace("</p>", " ")
            # Basic HTML tag removal
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()
            if description:
                parts.append(f"Description: {description}")
        
        # Product type
        if product.get("product_type"):
            parts.append(f"Type: {product['product_type']}")
        
        # Vendor
        if product.get("vendor"):
            parts.append(f"Vendor: {product['vendor']}")
        
        # Tags
        if product.get("tags"):
            tags = product["tags"]
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            if tags:
                parts.append(f"Tags: {', '.join(tags)}")
        
        # Variants information
        variants = product.get("variants", [])
        if variants:
            variant_info = []
            for variant in variants:
                variant_parts = []
                if variant.get("title") and variant["title"] != "Default Title":
                    variant_parts.append(variant["title"])
                if variant.get("sku"):
                    variant_parts.append(f"SKU: {variant['sku']}")
                if variant_parts:
                    variant_info.append(" ".join(variant_parts))
            if variant_info:
                parts.append(f"Variants: {'; '.join(variant_info[:5])}")  # Limit to 5 variants
        
        return "\n".join(parts)
    
    def extract_metadata(self, product: Dict) -> Dict[str, Any]:
        """
        Extract metadata from a product for filtering.
        
        Args:
            product: Product dictionary from Shopify API
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "product_id": str(product.get("id", "")),
            "title": product.get("title", ""),
            "handle": product.get("handle", ""),
            "product_type": product.get("product_type", ""),
            "vendor": product.get("vendor", ""),
            "created_at": product.get("created_at", ""),
            "updated_at": product.get("updated_at", ""),
        }
        
        # Store description separately for keyword search
        if product.get("body_html"):
            description = product["body_html"]
            description = description.replace("<br>", " ").replace("<br/>", " ")
            description = description.replace("</p>", " ")
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()
            metadata["description"] = description
        else:
            metadata["description"] = ""
        
        # Tags
        tags = product.get("tags", "")
        if isinstance(tags, str):
            metadata["tags"] = tags
        else:
            metadata["tags"] = ", ".join(tags) if tags else ""
        
        # Price range (from variants)
        variants = product.get("variants", [])
        if variants:
            prices = [float(v.get("price", 0)) for v in variants if v.get("price")]
            if prices:
                metadata["min_price"] = min(prices)
                metadata["max_price"] = max(prices)
                metadata["price"] = min(prices)  # Use min price for simple filtering
        
        # Availability
        metadata["available"] = any(
            v.get("inventory_quantity", 0) > 0 or v.get("inventory_policy") == "continue"
            for v in variants
        )
        
        # Images
        images = product.get("images", [])
        if images:
            metadata["image_url"] = images[0].get("src", "")
            metadata["num_images"] = len(images)
        
        # Product URL
        if product.get("handle"):
            metadata["product_url"] = f"{product.get('handle')}"
        
        return metadata
    
    def process_products(self, products: List[Dict]) -> List[Dict[str, Any]]:
        """
        Process a list of products into searchable documents.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            List of processed documents with text and metadata
        """
        documents = []
        
        for product in products:
            try:
                text = self.extract_product_text(product)
                metadata = self.extract_metadata(product)
                
                if text.strip():  # Only include products with text
                    documents.append({
                        "text": text,
                        "metadata": metadata
                    })
            except Exception as e:
                print(f"Error processing product {product.get('id', 'unknown')}: {e}")
                continue
        
        print(f"Processed {len(documents)} products into searchable documents")
        return documents


def main():
    """Test the data processor."""
    # Load products
    with open("products.json", "r", encoding="utf-8") as f:
        products = json.load(f)
    
    # Process
    processor = ProductDataProcessor()
    documents = processor.process_products(products)
    
    # Print sample
    if documents:
        print("\n--- Sample Document ---")
        print("Text:")
        print(documents[0]["text"][:500])
        print("\nMetadata:")
        print(json.dumps(documents[0]["metadata"], indent=2))


if __name__ == "__main__":
    main()

"""
Shopify Product Fetcher with enhanced error handling and pagination.
Fetches all products from a Shopify store using the Admin API.
"""
import requests
import json
import time
from typing import List, Dict, Optional
from config import config


class ShopifyFetcher:
    """Handles fetching products from Shopify Admin API."""
    
    def __init__(self):
        """Initialize the Shopify fetcher with configuration."""
        config.validate()
        self.shop_url = config.SHOPIFY_SHOP_URL
        self.api_version = config.SHOPIFY_API_VERSION
        self.headers = config.get_shopify_headers()
        
    def get_all_products(self, limit: int = 250) -> List[Dict]:
        """
        Fetch all products from Shopify using pagination.
        
        Args:
            limit: Number of products per page (max 250)
            
        Returns:
            List of product dictionaries
        """
        all_products = []
        next_url = f"{self.shop_url}/admin/api/{self.api_version}/products.json?limit={limit}"
        
        print(f"Starting to fetch products from {self.shop_url}...")
        
        while next_url:
            try:
                print(f"Fetching: {next_url}")
                response = requests.get(next_url, headers=self.headers, timeout=30)
                
                if response.status_code == 429:
                    # Rate limit hit, wait and retry
                    retry_after = int(response.headers.get("Retry-After", 2))
                    print(f"Rate limit hit. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                    
                if response.status_code != 200:
                    print(f"Error {response.status_code}: {response.text}")
                    break
                
                data = response.json()
                products = data.get("products", [])
                all_products.extend(products)
                print(f"Fetched {len(products)} products. Total: {len(all_products)}")
                
                # Parse pagination link header
                link_header = response.headers.get("Link")
                if link_header and 'rel="next"' in link_header:
                    import re
                    match = re.search(r'<([^>]+)>; rel="next"', link_header)
                    next_url = match.group(1) if match else None
                else:
                    next_url = None
                    
                # Be nice to the API
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                break
        
        print(f"\nSuccessfully fetched {len(all_products)} total products")
        return all_products
    
    def save_products(self, products: List[Dict], filename: Optional[str] = None):
        """
        Save products to a JSON file.
        
        Args:
            products: List of product dictionaries
            filename: Output filename (default from config)
        """
        if filename is None:
            filename = config.PRODUCTS_JSON_PATH
            
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(products)} products to {filename}")
    
    def load_products(self, filename: Optional[str] = None) -> List[Dict]:
        """
        Load products from a JSON file.
        
        Args:
            filename: Input filename (default from config)
            
        Returns:
            List of product dictionaries
        """
        if filename is None:
            filename = config.PRODUCTS_JSON_PATH
            
        try:
            with open(filename, "r", encoding="utf-8") as f:
                products = json.load(f)
            print(f"Loaded {len(products)} products from {filename}")
            return products
        except FileNotFoundError:
            print(f"File {filename} not found")
            return []


def main():
    """Main function to fetch and save products."""
    fetcher = ShopifyFetcher()
    products = fetcher.get_all_products()
    fetcher.save_products(products)
    
    # Print some stats
    print(f"\n--- Product Statistics ---")
    print(f"Total products: {len(products)}")
    if products:
        print(f"Sample product: {products[0].get('title', 'N/A')}")


if __name__ == "__main__":
    main()

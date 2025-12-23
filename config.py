"""
Configuration management for Shopify RAG system.
Loads settings from environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Centralized configuration class."""
    
    # Shopify Settings
    SHOPIFY_SHOP_URL = os.getenv("SHOPIFY_SHOP_URL", "https://ladani-store-2.myshopify.com")
    SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2025-10")
    SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
    
    # Vector Database Settings
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "shopify_products")
    
    # Embedding Model Settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # OpenAI Settings (optional)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Data Files
    PRODUCTS_JSON_PATH = "products.json"
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.SHOPIFY_ACCESS_TOKEN:
            raise ValueError(
                "SHOPIFY_ACCESS_TOKEN is required. "
                "Please set it in .env file or environment variables."
            )
        return True
    
    @classmethod
    def get_shopify_headers(cls):
        """Get HTTP headers for Shopify API requests."""
        return {
            "X-Shopify-Access-Token": cls.SHOPIFY_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }

# Create instance for easy importing
config = Config()

import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SearchEngine:
    """
    Wrapper for Meilisearch.
    Provides typo-tolerant, lightning-fast product search.
    """
    def __init__(self):
        self.host = os.environ.get("MEILISEARCH_HOST", "http://localhost:7700")
        self.api_key = os.environ.get("MEILISEARCH_MASTER_KEY", "masterKey")
        self.enabled = os.environ.get("ENABLE_SEARCH_ENGINE", "false").lower() == "true"
        self.client = None

        if self.enabled:
            try:
                import meilisearch
                self.client = meilisearch.Client(self.host, self.api_key)
                # Ensure the products index exists
                self.client.index('products').update_settings({
                    'searchableAttributes': [
                        'name',
                        'description',
                        'category',
                        'materials',
                        'colors'
                    ],
                    'filterableAttributes': [
                        'brand_id',
                        'store_id',
                        'category',
                        'price',
                        'materials',
                        'colors'
                    ],
                    'sortableAttributes': [
                        'price',
                        'created_at'
                    ]
                })
                logger.info("Meilisearch client initialized and 'products' index configured.")
            except ImportError:
                logger.warning("meilisearch python package not installed. Search engine disabled.")
                self.enabled = False
            except Exception as e:
                logger.warning(f"Could not connect to Meilisearch at {self.host}: {e}")
                self.enabled = False

    def index_product(self, product_dict: Dict[str, Any]) -> bool:
        """Add or update a product in the search index"""
        if not self.enabled or not self.client:
            return False

        try:
            # Ensure id is string and handle datetime objects
            doc = {k: v for k, v in product_dict.items() if k not in ['created_at', 'updated_at']}
            doc['id'] = str(doc['id'])

            self.client.index('products').add_documents([doc])
            return True
        except Exception as e:
            logger.error(f"Failed to index product {product_dict.get('id')}: {e}")
            return False

    def remove_product(self, product_id: str) -> bool:
        """Remove a product from the search index"""
        if not self.enabled or not self.client:
            return False

        try:
            self.client.index('products').delete_document(str(product_id))
            return True
        except Exception as e:
            logger.error(f"Failed to remove product {product_id} from index: {e}")
            return False

    def search_products(self, query: str, filters: Optional[List[str]] = None, limit: int = 50) -> List[Dict]:
        """
        Execute a typo-tolerant search.
        filters should be a list of Meilisearch filter strings, e.g., ["price < 50", "category = 'shirts'"]
        """
        if not self.enabled or not self.client:
            return []

        try:
            search_params = {'limit': limit}
            if filters:
                search_params['filter'] = filters

            result = self.client.index('products').search(query, search_params)
            return result.get('hits', [])
        except Exception as e:
            logger.error(f"Search query failed: {e}")
            return []

search_engine = SearchEngine()

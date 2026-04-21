# retrieval/qdrant_retriever.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path
from typing import List, Tuple, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain_huggingface import HuggingFaceEmbeddings
from rank_bm25 import BM25Okapi
from config import Config
from utils import tokenize_text, roman_to_int


class QdrantRetriever:
    def __init__(self):
        self.client = QdrantClient(path=str(Config.QDRANT_DB_PATH))
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.bm25 = None
        self.all_payloads = []
        self.available_chapters = []
        self._load_metadata()
    
    def _load_metadata(self):
        metadata_path = Path(Config.METADATA_PATH) / "chunks.json"
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.all_payloads = json.load(f)
            
            documents = [chunk.get("content_preview", "") for chunk in self.all_payloads]
            tokenized_docs = [tokenize_text(doc) for doc in documents]
            self.bm25 = BM25Okapi(tokenized_docs)
            
            chapters = set()
            for chunk in self.all_payloads:
                if chunk.get('chapter'):
                    chapters.add(chunk['chapter'])
            self.available_chapters = sorted(list(chapters), key=roman_to_int)
            
            print(f"✅ Loaded {len(documents)} documents, {len(self.available_chapters)} chapters")
    
    def search(self, query: str, chapter: str, top_k: int = Config.TOP_K_RESULTS) -> List[Tuple[Dict, float]]:
        """Tìm kiếm trong Qdrant - SỬA CHO API MỚI"""
        query_vector = self.embeddings.embed_query(query)
        
        # Tạo filter
        qdrant_filter = Filter(must=[FieldCondition(key="chapter", match=MatchValue(value=chapter))])
        
        try:
            # THỬ CÁCH 1: API cũ
            search_result = self.client.search(
                collection_name=Config.COLLECTION_NAME,
                query_vector=query_vector,
                limit=top_k,
                query_filter=qdrant_filter
            )
        except AttributeError:
            try:
                # THỬ CÁCH 2: API mới (dùng search_batch)
                from qdrant_client.http import models as rest
                search_result = self.client.search_batch(
                    collection_name=Config.COLLECTION_NAME,
                    requests=[
                        rest.SearchRequest(
                            vector=query_vector,
                            limit=top_k,
                            filter=qdrant_filter
                        )
                    ]
                )[0]
            except:
                # THỬ CÁCH 3: Dùng REST API trực tiếp
                import requests
                url = f"http://localhost:6333/collections/{Config.COLLECTION_NAME}/points/search"
                payload = {
                    "vector": query_vector,
                    "limit": top_k,
                    "filter": {
                        "must": [
                            {"key": "chapter", "match": {"value": chapter}}
                        ]
                    }
                }
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    search_result = response.json()["result"]
                else:
                    return []
        
        results = []
        for point in search_result:
            if hasattr(point, 'payload'):
                payload = point.payload
                score = point.score
            elif isinstance(point, dict):
                payload = point.get('payload', {})
                score = point.get('score', 0)
            else:
                continue
            results.append((payload, score))
        
        return results
    
    def get_chapters(self) -> List[str]:
        return self.available_chapters
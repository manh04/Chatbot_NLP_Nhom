# retrieval/qdrant_retriever.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import atexit
from pathlib import Path
from typing import List, Tuple, Dict
from langchain_huggingface import HuggingFaceEmbeddings
from rank_bm25 import BM25Okapi
from config import Config
from utils import tokenize_text, roman_to_int

# Import Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Filter, FieldCondition, MatchValue
except ImportError:
    raise ImportError("Cần cài qdrant-client: pip install qdrant-client")


class QdrantRetriever:
    """Quản lý kết nối Qdrant, tự động giải phóng lock"""
    
    _instance = None  # Singleton pattern để chỉ có một kết nối duy nhất
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self.client = None
        self.embeddings = None
        self.bm25 = None
        self.all_payloads = []
        self.available_chapters = []
        
        # Đăng ký giải phóng kết nối khi thoát
        atexit.register(self.close)
        
        self._load()
    
    def _load(self):
        """Load Qdrant database"""
        print(f"    Kết nối Qdrant database: {Config.QDRANT_DB_PATH}")
        
        # Kiểm tra xem có database không
        if not Path(Config.QDRANT_DB_PATH).exists():
            raise FileNotFoundError(f"Không tìm thấy database tại {Config.QDRANT_DB_PATH}")
        
        # Xóa file lock nếu tồn tại (do lần chạy trước bị lỗi)
        lock_file = Path(Config.QDRANT_DB_PATH) / ".lock"
        if lock_file.exists():
            try:
                lock_file.unlink()
                print(f"    Đã xóa file lock cũ")
            except:
                pass
        
        # Kết nối với chế độ read-only để tránh lock
        try:
            self.client = QdrantClient(path=str(Config.QDRANT_DB_PATH))
            print(f"    Kết nối thành công")
        except Exception as e:
            print(f"    Lỗi kết nối: {e}")
            raise
        
        # Khởi tạo embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load metadata
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata và BM25 index"""
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
            
            print(f"    Loaded {len(documents)} documents, {len(self.available_chapters)} chapters")
    
    def search(self, query: str, chapter: str, top_k: int = Config.TOP_K_RESULTS) -> List[Tuple[Dict, float]]:
        """Tìm kiếm trong Qdrant"""
        query_vector = self.embeddings.embed_query(query)
        
        # Tạo filter
        qdrant_filter = Filter(must=[FieldCondition(key="chapter", match=MatchValue(value=chapter))])
        
        try:
            search_result = self.client.search(
                collection_name=Config.COLLECTION_NAME,
                query_vector=query_vector,
                limit=top_k,
                query_filter=qdrant_filter
            )
        except Exception as e:
            print(f"    Lỗi tìm kiếm: {e}")
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
    
    def close(self):
        """Đóng kết nối và giải phóng tài nguyên"""
        if self.client:
            try:
                # Qdrant client có method close không?
                if hasattr(self.client, 'close'):
                    self.client.close()
            except:
                pass
            self.client = None
            print("   Đã đóng kết nối Qdrant")
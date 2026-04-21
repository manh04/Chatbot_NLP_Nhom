# config.py
from pathlib import Path

class Config:
    # Đường dẫn
    BASE_DIR = Path(__file__).parent
    PDF_PATH = BASE_DIR / "nghi_dinh_168.pdf"
    QDRANT_DB_PATH = BASE_DIR / "qdrant_legal_db"
    METADATA_PATH = BASE_DIR / "metadata_qdrant"
    COLLECTION_NAME = "legal_docs"
    
    # Mô hình
    EMBEDDING_MODEL = "keepitreal/vietnamese-sbert"
    EMBEDDING_DIM = 768
    
    # Tham số chunking
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150
    
    # Tham số tìm kiếm
    TOP_K_RESULTS = 5
    
    # Tham số LLM (nếu dùng)
    LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    TEMPERATURE = 0.3
    MAX_NEW_TOKENS = 256
    
    # Cache
    CACHE_DIR = BASE_DIR / "cache"
    MODEL_CACHE_DIR = BASE_DIR / "model_cache"
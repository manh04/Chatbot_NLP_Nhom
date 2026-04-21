# agent/legal_agent_crossref.py - Agent với truy xuất tham chiếu chéo
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import torch
from typing import Dict, Any, List, Tuple, Set
from config import Config
from retrieval.qdrant_retriever import QdrantRetriever

# Import LLM
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline

# Import Reranker
try:
    from sentence_transformers import CrossEncoder
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False


class LegalAgentWithCrossRef:
    """Agent với khả năng truy xuất tham chiếu chéo giữa các Điều, Khoản"""
    
    # Pattern nhận diện tham chiếu
    REFERENCE_PATTERNS = [
        r'(?:theo quy định tại|quy định tại|căn cứ)\s+(?:khoản\s+(\d+)\s+)?(?:Điều\s+(\d+))',
        r'(?:Điều\s+(\d+))\s+(?:khoản\s+(\d+))?',
        r'(?:khoản\s+(\d+))\s+(?:Điều\s+(\d+))',
    ]
    
    def __init__(self):
        # 1. Load retriever
        print(" Bước 1: Load Qdrant retriever...")
        self.retriever = QdrantRetriever()
        self.current_chapter = None
        
        # 2. Build index cho truy xuất nhanh
        self._build_reference_index()
        
        # 3. Load LLM
        print("\n Bước 2: Load LLM model...")
        self._load_llm()
        
        # 4. Load Reranker
        print("\n Bước 3: Load Reranker...")
        self._load_reranker()
        
        print("\n AGENT ĐÃ SẴN SÀNG!")
        print("   - Có khả năng truy xuất tham chiếu chéo")
        print("   - Tự động lấy nội dung của Điều/Khoản được nhắc đến")
    
    def _build_reference_index(self):
        """Xây dựng chỉ mục để truy xuất nhanh Điều, Khoản"""
        self.article_cache = {}  # {article_num: {clause_num: content}}
        self.article_title_cache = {}  # {article_num: title}
        
        # Lấy tất cả chunks từ metadata
        import json
        from pathlib import Path
        
        metadata_path = Path(Config.METADATA_PATH) / "chunks.json"
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            
            for chunk in chunks:
                article = chunk.get('article')
                clause = chunk.get('clause')
                content = chunk.get('content', '')
                chunk_type = chunk.get('chunk_type')
                
                if article:
                    if article not in self.article_cache:
                        self.article_cache[article] = {}
                        self.article_title_cache[article] = chunk.get('title', '')
                    
                    if clause and chunk_type == 'clause':
                        self.article_cache[article][clause] = content
                    elif chunk_type == 'article':
                        self.article_title_cache[article] = chunk.get('title', '')
            
            print(f"    Đã index {len(self.article_cache)} Điều")
    
    def _extract_references(self, text: str) -> List[Tuple[int, int]]:
        """Trích xuất các tham chiếu đến Điều, Khoản từ văn bản"""
        references = set()
        
        for pattern in self.REFERENCE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) == 2:
                    clause = int(groups[0]) if groups[0] else None
                    article = int(groups[1]) if groups[1] else None
                    
                    if article:
                        references.add((article, clause if clause else 0))
        
        return list(references)
    
    def _get_referenced_content(self, references: List[Tuple[int, int]]) -> str:
        """Lấy nội dung của các Điều, Khoản được tham chiếu"""
        if not references:
            return ""
        
        content_parts = []
        for article, clause in references:
            if article in self.article_cache:
                # Lấy tiêu đề Điều
                title = self.article_title_cache.get(article, "")
                content_parts.append(f"\n📌 **Tham chiếu đến Điều {article}**{': ' + title if title else ''}")
                
                if clause > 0 and clause in self.article_cache[article]:
                    # Lấy nội dung Khoản cụ thể
                    clause_content = self.article_cache[article][clause]
                    content_parts.append(f"   Khoản {clause}: {clause_content[:500]}")
                else:
                    # Lấy tất cả các Khoản của Điều
                    for k, v in self.article_cache[article].items():
                        content_parts.append(f"   Khoản {k}: {v[:300]}...")
        
        return "\n".join(content_parts)
    
    def _load_llm(self):
        """Load mô hình LLM"""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Device: {device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                Config.LLM_MODEL,
                trust_remote_code=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                Config.LLM_MODEL,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=Config.MAX_NEW_TOKENS,
                temperature=Config.TEMPERATURE,
                do_sample=True,
                top_p=0.95,
                repetition_penalty=1.1
            )
            
            self.llm = HuggingFacePipeline(pipeline=self.pipe)
            print(f"    Loaded {Config.LLM_MODEL}")
            
        except Exception as e:
            print(f"    Không thể load LLM: {e}")
            self.llm = None
    
    def _load_reranker(self):
        """Load reranker"""
        if RERANKER_AVAILABLE:
            try:
                self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                print("    Reranker ready")
            except:
                self.reranker = None
        else:
            self.reranker = None
    
    def set_chapter(self, chapter: str):
        self.current_chapter = chapter
    
    def _rerank_results(self, query: str, results: List[Tuple[Dict, float]], top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Rerank kết quả tìm kiếm"""
        if not results or self.reranker is None:
            return results[:top_k]
        
        pairs = [(query, payload.get('content_preview', payload.get('content', ''))) 
                 for payload, _ in results]
        
        rerank_scores = self.reranker.predict(pairs)
        
        combined = []
        for i, (payload, orig_score) in enumerate(results):
            rerank_score = float(rerank_scores[i]) / 10.0
            final_score = 0.6 * rerank_score + 0.4 * orig_score
            combined.append((payload, final_score))
        
        combined.sort(key=lambda x: x[1], reverse=True)
        return combined[:top_k]
    
    def _build_prompt(self, question: str, context: str, cross_refs: str) -> str:
        """Xây dựng prompt cho LLM với tham chiếu chéo"""
        system_prompt = f"""Bạn là trợ lý AI chuyên về Nghị định 168 về đăng ký doanh nghiệp.

QUY TẮC:
1. Trả lời DỰA VÀO thông tin trong CONTEXT và CROSS_REFERENCES
2. Nếu có tham chiếu đến Điều/Khoản khác, hãy giải thích luôn nội dung của nó
3. Trả lời bằng tiếng Việt, rõ ràng, mượt mà, dễ hiểu
4. Đưa ra hướng dẫn cụ thể cho người dùng

CONTEXT (kết quả tìm kiếm chính):
{context}

CROSS_REFERENCES (nội dung của các Điều/Khoản được nhắc đến):
{cross_refs if cross_refs else "Không có tham chiếu chéo"}

CÂU HỎI: {question}

CÂU TRẢ LỜI:"""
        
        return system_prompt
    
    def ask(self, question: str) -> Dict[str, Any]:
        """Hỏi agent - tự động truy xuất tham chiếu chéo"""
        if self.current_chapter is None:
            return {
                "answer": " Vui lòng chọn Chương trước khi hỏi!",
                "sources": []
            }
        
        # 1. Tìm kiếm
        results = self.retriever.search(question, self.current_chapter, top_k=Config.TOP_K_RESULTS * 2)
        
        # 2. Rerank
        results = self._rerank_results(question, results, top_k=Config.TOP_K_RESULTS)
        
        if not results:
            return {
                "answer": f" Không tìm thấy thông tin liên quan.",
                "sources": []
            }
        
        # 3. Xây dựng context
        context_parts = []
        sources = []
        all_references = []
        
        for payload, score in results:
            header_parts = [f"Chương {payload.get('chapter', self.current_chapter)}"]
            if payload.get('article'):
                header_parts.append(f"Điều {payload['article']}")
            if payload.get('clause'):
                header_parts.append(f"Khoản {payload['clause']}")
            
            header = " - ".join(header_parts)
            content = payload.get('content_preview', payload.get('content', ''))
            
            context_parts.append(f"[{header}]\n{content}")
            sources.append({
                "article": payload.get('article'),
                "clause": payload.get('clause'),
                "score": score
            })
            
            # Trích xuất tham chiếu từ nội dung
            refs = self._extract_references(content)
            all_references.extend(refs)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # 4. Lấy nội dung của các tham chiếu
        cross_ref_content = self._get_referenced_content(all_references)
        
        # 5. Sinh câu trả lời
        if self.llm:
            prompt = self._build_prompt(question, context, cross_ref_content)
            try:
                llm_answer = self.llm.invoke(prompt)
                if len(llm_answer) > len(prompt):
                    llm_answer = llm_answer[len(prompt):].strip()
            except Exception as e:
                llm_answer = f"Lỗi LLM: {e}\n\n{context}"
        else:
            llm_answer = f" **KẾT QUẢ TÌM KIẾM**\n\n{context}"
            if cross_ref_content:
                llm_answer += f"\n\n **THAM CHIẾU LIÊN QUAN:**\n{cross_ref_content}"
        
        return {
            "answer": llm_answer,
            "sources": sources,
            "cross_references": all_references,
            "num_chunks": len(results)
        }
    
    def get_chapters(self) -> List[str]:
        return self.retriever.get_chapters()
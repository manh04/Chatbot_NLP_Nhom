# main.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import warnings
warnings.filterwarnings("ignore")

from config import Config
from data.ocr import PDFOCRProcessor
from data.parser import SmartLegalParser  # Dùng parser thông minh
from data.chunker import DatabaseBuilder


def main():
    print("=" * 70)
    print(" GIAI ĐOẠN 1: XỬ LÝ PDF VÀ TẠO DATABASE")
    print("=" * 70)
    
    if not Config.PDF_PATH.exists():
        print(f" Không tìm thấy file PDF: {Config.PDF_PATH}")
        return
    
    # 1. OCR
    print("\n Bước 1: OCR file PDF...")
    ocr = PDFOCRProcessor()
    text = ocr.extract_text(str(Config.PDF_PATH), use_cache=True)
    print(f"    Trích xuất {len(text):,} ký tự")
    
    # 2. Parse thông minh
    print("\n Bước 2: Parse cấu trúc pháp lý (Chương → Điều → Khoản → Điểm)...")
    parser = SmartLegalParser()
    chunks = parser.parse_to_chunks(text)
    print(f"\n    Tổng số chunks: {len(chunks)}")
    
    # 3. Kiểm tra chất lượng
    articles = set(c.article for c in chunks if c.article > 0)
    print(f"\n    Số Điều tìm được: {len(articles)}/124")
    
    if len(articles) < 100:
        print(f"\n    CẢNH BÁO: Chỉ tìm được {len(articles)} Điều!")
        print("   Hãy kiểm tra file OCR hoặc điều chỉnh pattern parser")
        
        # In preview để debug
        print("\n    Preview text (1000 ký tự):")
        print("-" * 50)
        print(text[:1000])
        print("-" * 50)
        
        confirm = input("\n   Vẫn tiếp tục tạo database? (y/n): ").strip().lower()
        if confirm != 'y':
            print("   Dừng lại để kiểm tra.")
            return
    
    # 4. Tạo database
    print("\n Bước 3: Tạo Qdrant database...")
    builder = DatabaseBuilder()
    builder.build(chunks)
    
    print("\n GIAI ĐOẠN 1 HOÀN TẤT!")
    print(f"\n Kết quả:")
    print(f"   - Database: {Config.QDRANT_DB_PATH}")
    print(f"   - Metadata: {Config.METADATA_PATH}")
    print(f"   - Tổng chunks: {len(chunks)}")
    print(f"   - Số Chương: {len(set(c.chapter for c in chunks if c.chapter))}")
    print(f"   - Số Điều: {len(articles)}")


if __name__ == "__main__":
    main()
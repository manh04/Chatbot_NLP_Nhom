# test_api_simple.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🔍 KIỂM TRA QDRANT API")
print("=" * 40)

try:
    from qdrant_client import QdrantClient
    
    # Kiểm tra client có method search không
    client = QdrantClient(location=":memory:")  # Tạo client in-memory để test
    
    if hasattr(client, 'search'):
        print("✅ Client có method 'search'")
        print("   → Dùng API cũ (phù hợp với code hiện tại)")
    else:
        print("❌ Client KHÔNG có method 'search'")
        print("   → Cần downgrade qdrant-client")
    
    # Liệt kê các method có thể dùng
    methods = [m for m in dir(client) if not m.startswith('_')]
    print(f"\n📋 Các method có sẵn: {methods[:10]}...")
    
except Exception as e:
    print(f"❌ Lỗi: {e}")
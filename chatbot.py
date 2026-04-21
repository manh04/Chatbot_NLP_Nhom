# gd2_main.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.legal_agent import LegalAgentWithCrossRef

def main():
    print("=" * 70)
    print(" LEGAL AGENT - HỖ TRỢ ĐĂNG KÝ DOANH NGHIỆP")
    print("   Tự động truy xuất nội dung của Điều/Khoản được tham chiếu")
    print("=" * 70)
    
    agent = LegalAgentWithCrossRef()
    chapters = agent.get_chapters()
    
    print("\n Các Chương có sẵn:")
    for i, ch in enumerate(chapters, 1):
        print(f"   {i}. Chương {ch}")
    
    while True:
        try:
            choice = input("\nChọn Chương (nhập số): ")
            idx = int(choice) - 1
            if 0 <= idx < len(chapters):
                agent.set_chapter(chapters[idx])
                break
        except:
            pass
    
    print(f"\nĐã chọn Chương {agent.current_chapter}")
    print("-" * 50)
    
    while True:
        question = input("\n Bạn: ").strip()
        if question.lower() in ['exit', 'quit']:
            break
        
        result = agent.ask(question)
        print(f"\n Agent:\n{result['answer']}")
        
        if result.get('cross_references'):
            print(f"\n Đã tự động tra cứu {len(result['cross_references'])} tham chiếu chéo")

if __name__ == "__main__":
    main()
# utils.py
import re
from typing import List

def roman_to_int(roman: str) -> int:
    """Chuyển số La Mã thành số nguyên"""
    roman_map = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
        'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
        'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20
    }
    return roman_map.get(roman.upper(), 999)

def extract_keywords(text: str) -> List[str]:
    """Trích xuất từ khóa từ văn bản"""
    keywords = set()
    text_lower = text.lower()
    
    legal_terms = {
        'đăng ký doanh nghiệp': 'business_registration',
        'hộ kinh doanh': 'household_business',
        'chuyển nhượng': 'transfer',
        'ủy quyền': 'delegation',
        'mã số doanh nghiệp': 'enterprise_code',
        'giấy tờ': 'documents',
        'vốn góp': 'capital_contribution',
        'thành viên': 'member',
        'cổ đông': 'shareholder',
    }
    
    for viet_term, eng_term in legal_terms.items():
        if viet_term in text_lower:
            keywords.add(viet_term)
            keywords.add(eng_term)
    
    article_match = re.search(r'điều\s+(\d+)', text_lower)
    if article_match:
        keywords.add(f'article_{article_match.group(1)}')
    
    clause_match = re.search(r'khoản\s+(\d+)', text_lower)
    if clause_match:
        keywords.add(f'clause_{clause_match.group(1)}')
    
    return list(keywords)

def tokenize_text(text: str) -> List[str]:
    """Tokenize văn bản cho BM25"""
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    stopwords = {'của', 'và', 'là', 'có', 'không', 'thì', 'mà', 'đã', 'sẽ', 
                 'được', 'cho', 'với', 'tại', 'theo', 'một', 'những', 'các'}
    words = text.split()
    return [w for w in words if w not in stopwords and len(w) > 1]
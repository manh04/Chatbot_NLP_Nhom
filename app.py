# app.py - Streamlit demo
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from agent.legal_agent import LegalAgentWithCrossRef
from utils import roman_to_int

# Chủ đề Chương
CHAPTER_TOPICS = {
    "I": {"name": "CHƯƠNG I: QUY ĐỊNH CHUNG", "color": "#1f77b4"},
    "II": {"name": "CHƯƠNG II: ĐĂNG KÝ DOANH NGHIỆP", "color": "#2ca02c"},
    "III": {"name": "CHƯƠNG III: ĐĂNG KÝ HỘ KINH DOANH", "color": "#ff7f0e"},
    "IV": {"name": "CHƯƠNG IV: ĐĂNG KÝ CHI NHÁNH", "color": "#d62728"},
    "V": {"name": "CHƯƠNG V: CUNG CẤP THÔNG TIN", "color": "#9467bd"},
    "VI": {"name": "CHƯƠNG VI: XỬ LÝ VI PHẠM", "color": "#8c564b"},
    "VII": {"name": "CHƯƠNG VII: ĐIỀU KHOẢN THI HÀNH", "color": "#e377c2"},
    "VIII": {"name": "CHƯƠNG VIII: QUY ĐỊNH CHUYỂN TIẾP", "color": "#7f7f7f"},
    "IX": {"name": "CHƯƠNG IX: QUY ĐỊNH KHÁC", "color": "#bcbd22"}
}

st.set_page_config(page_title="Legal Agent", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; text-align: center;">
    <h1 style="color: white;"> LEGAL AGENT</h1>
    <p style="color: rgba(255,255,255,0.9);">Trợ lý AI - Nghị định 168 về đăng ký doanh nghiệp</p>
    <p style="color: rgba(255,255,255,0.7); font-size: 0.8rem;"> Tự động truy xuất tham chiếu chéo |  Rerank kết quả |  Hướng dẫn chi tiết</p>
</div>
""", unsafe_allow_html=True)

# Khởi tạo agent
if "agent" not in st.session_state:
    with st.spinner(" Đang khởi tạo Agent (lần đầu có thể mất 1-2 phút để tải model)..."):
        st.session_state.agent = LegalAgentWithCrossRef()
        st.session_state.current_chapter = None
        st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/law.png", width=80)
    st.markdown("###  Chọn Chương cần tư vấn")
    
    chapters = st.session_state.agent.get_chapters()
    
    for chapter in chapters:
        topic = CHAPTER_TOPICS.get(chapter, {"name": f"CHƯƠNG {chapter}"})
        if st.button(f"{topic['icon']} {topic['name'][:35]}", key=chapter, use_container_width=True):
            st.session_state.agent.set_chapter(chapter)
            st.session_state.current_chapter = chapter
            st.session_state.chat_history = []
            st.rerun()
    
    if st.session_state.current_chapter:
        topic = CHAPTER_TOPICS.get(st.session_state.current_chapter, {})
        st.markdown("---")
        st.markdown(f"""
        <div style="background: {topic.get('color', '#667eea')}20; padding: 10px; border-radius: 10px;">
            <b> Đang tư vấn</b><br>
            {topic.get('icon', '📌')} {topic.get('name', '')}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(" Nghị định 168/2020/NĐ-CP")

# Main content
if st.session_state.current_chapter is None:
    st.info(" Vui lòng chọn một Chương từ thanh bên trái để bắt đầu tư vấn")
    
    st.markdown("###  Giới thiệu các Chương")
    cols = st.columns(3)
    for i, chapter in enumerate(chapters[:9]):
        topic = CHAPTER_TOPICS.get(chapter, {})
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: {topic.get('color', "#f0f0f000")}20; padding: 10px; border-radius: 10px; margin: 5px;">
                <b>{topic.get('icon', '📌')} {topic.get('name', f'Chương {chapter}')}</b>
            </div>
            """, unsafe_allow_html=True)
else:
    # Hiển thị chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                <div style="background: #e3f2fd; padding: 10px 15px; border-radius: 15px; max-width: 80%;">
                    <b> Bạn</b><br>{msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                <div style="background: #f5f5f5; padding: 10px 15px; border-radius: 15px; max-width: 80%;">
                    <b> Agent</b><br>{msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Input
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(" Nhập câu hỏi:", key="input", placeholder="Ví dụ: Thủ tục đăng ký doanh nghiệp qua mạng?")
    with col2:
        send_button = st.button(" Gửi", use_container_width=True)
    
    if send_button and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("🔍 Đang tra cứu và tổng hợp câu trả lời..."):
            result = st.session_state.agent.ask(user_input)
        
        st.session_state.chat_history.append({"role": "assistant", "content": result['answer']})
        st.rerun()
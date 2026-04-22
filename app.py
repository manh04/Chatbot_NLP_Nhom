# app.py - Streamlit demo với giao diện tối ưu
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from agent.legal_agent import LegalAgentWithCrossRef
from utils import roman_to_int

# Chủ đề Chương
CHAPTER_TOPICS = {
    "I": {
        "name": "CHƯƠNG I: QUY ĐỊNH CHUNG",
        "short_name": "CHƯƠNG I",
        "desc": "Quy định chung, phạm vi, đối tượng áp dụng",
        "color": "#1f77b4"
    },
    "II": {
        "name": "CHƯƠNG II: NHIỆM VỤ, QUYỀN HẠN CỦA CƠ QUAN ĐĂNG KÝ KINH DOANH VÀ TRÁCH NHIỆM CỦA CÁC CƠ QUAN QUẢN LÝ NHÀ NƯỚC TRONG ĐĂNG KÝ DOANH NGHIỆP, ĐĂNG KÝ HỘ KINH DOANH",
        "short_name": "CHƯƠNG II",
        "desc": "Nhiệm vụ, quyền hạn của cơ quan đăng ký kinh doanh",
        "color": "#2ca02c"
    },
    "III": {
        "name": "CHƯƠNG III: HỒ SƠ, TRÌNH TỰ THỦ TỤC ĐĂNG KÝ DOANH NGHIỆP, ĐĂNG KÝ HOẠT ĐỘNG CHI NHÁNH, VĂN PHÒNG ĐẠI DIỆN, ĐỊA ĐIỂM KINH DOANH",
        "short_name": "CHƯƠNG III",
        "desc": "Hồ sơ, trình tự thủ tục đăng ký doanh nghiệp",
        "color": "#ff7f0e"
    },
    "IV": {
        "name": "CHƯƠNG IV: ĐĂNG KÝ DOANH NGHIỆP QUA MẠNG THÔNG TIN ĐIỆN TỬ",
        "short_name": "CHƯƠNG IV",
        "desc": "Đăng ký doanh nghiệp qua mạng điện tử",
        "color": "#d62728"
    },
    "V": {
        "name": "CHƯƠNG V: HỒ SƠ, TRÌNH TỰ, THỦ TỤC ĐĂNG KÝ THAY ĐỔI, THÔNG BÁO THAY ĐỔI NỘI DUNG ĐĂNG KÝ DOANH NGHIỆP",
        "short_name": "CHƯƠNG V",
        "desc": "Đăng ký thay đổi nội dung doanh nghiệp",
        "color": "#9467bd"
    },
    "VI": {
        "name": "CHƯƠNG VI: HỒ SƠ, TRÌNH TỰ, THỦ TỤC THÔNG BÁO TẠM NGƯNG KINH DOANH, CẤP LẠI GIẤY CHỨNG NHẬN ĐĂNG KÝ DOANH NGHIỆP, GIẢI THỂ DOANH NGHIỆP, THU HỒI GIẤY CHỨNG NHẬN ĐĂNG KÝ DOANH NGHIỆP",
        "short_name": "CHƯƠNG VI",
        "desc": "Tạm ngưng, giải thể, thu hồi giấy chứng nhận",
        "color": "#8c564b"
    },
    "VII": {
        "name": "CHƯƠNG VII: CÔNG BỐ, CUNG CẤP THÔNG TIN ĐĂNG KÝ DOANH NGHIỆP, LIÊN THÔNG, KẾT NỐI VÀ CHIA SẺ THÔNG TIN",
        "short_name": "CHƯƠNG VII",
        "desc": "Công bố, cung cấp thông tin doanh nghiệp",
        "color": "#e377c2"
    },
    "VIII": {
        "name": "CHƯƠNG VIII: HỘ KINH DOANH VÀ ĐĂNG KÝ HỘ KINH DOANH",
        "short_name": "CHƯƠNG VIII",
        "desc": "Đăng ký và quản lý hộ kinh doanh",
        "color": "#7f7f7f"
    },
    "IX": {
        "name": "CHƯƠNG IX: ĐIỀU KHOẢN THI HÀNH",
        "short_name": "CHƯƠNG IX",
        "desc": "Điều khoản thi hành",
        "color": "#bcbd22"
    }
}

# Cấu hình trang
st.set_page_config(
    page_title="Legal Agent - Nghị định 168",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh giao diện
st.markdown("""
<style>
    /* Nền tổng thể */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.8rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 600;
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.8rem 0 0 0;
        font-size: 1rem;
    }
    .main-header .badge {
        margin-top: 0.8rem;
        font-size: 0.8rem;
        color: rgba(255,255,255,0.7);
    }
    
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #1e293b;
    }
    .sidebar-header {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #334155;
        margin-bottom: 20px;
    }
    .sidebar-header h3 {
        color: white;
        margin: 10px 0 0 0;
    }
    .sidebar-header p {
        color: #94a3b8;
        font-size: 0.8rem;
    }
    
    /* Button trong sidebar */
    .stButton button {
        background-color: #334155;
        color: #e2e8f0;
        border: none;
        border-radius: 10px;
        padding: 10px 15px;
        margin: 5px 0;
        width: 100%;
        text-align: left;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    .stButton button:hover {
        background-color: #2a5298;
        transform: translateX(5px);
        color: white;
    }
    
    /* Chat container - nền tối */
    .chat-container {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 15px;
        min-height: 400px;
        max-height: 550px;
        overflow-y: auto;
        margin-bottom: 20px;
        border: 1px solid #334155;
    }
    
    /* Tin nhắn người dùng - nền gradient tím, chữ trắng */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px;
        border-bottom-right-radius: 5px;
        margin: 8px 0;
        display: inline-block;
        max-width: 75%;
        float: right;
        clear: both;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        font-size: 15px;
        line-height: 1.5;
    }
    
    /* Tin nhắn agent - nền xám đậm, chữ sáng */
    .agent-message {
        background-color: #334155;
        color: #f1f5f9;
        padding: 12px 18px;
        border-radius: 20px;
        border-bottom-left-radius: 5px;
        margin: 8px 0;
        display: inline-block;
        max-width: 75%;
        float: left;
        clear: both;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        border-left: 4px solid #667eea;
        font-size: 15px;
        line-height: 1.5;
    }
    
    /* Clear fix */
    .clearfix::after {
        content: "";
        clear: both;
        display: table;
    }
    
    /* Input box - nền tối, chữ sáng */
    .stTextInput input {
        background-color: #1e293b;
        border: 1px solid #475569;
        border-radius: 25px;
        padding: 14px 20px;
        font-size: 16px;
        color: #f1f5f9;
    }
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.2);
        background-color: #1e293b;
        color: #f1f5f9;
    }
    .stTextInput input::placeholder {
        color: #94a3b8;
    }
    
    /* Send button */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        font-size: 16px;
        color: white;
        border: none;
    }
    .stButton button[kind="primary"]:hover {
        transform: scale(1.02);
        opacity: 0.9;
    }
    
    /* Info box - nền tối, chữ sáng */
    .info-box {
        background-color: #1e293b;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: #f1f5f9;
    }
    .info-box b {
        color: #a78bfa;
    }
    
    /* Chapter card - nền tối, chữ sáng */
    .chapter-card {
        background-color: #1e293b;
        padding: 12px;
        border-radius: 10px;
        margin: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        cursor: pointer;
        color: #f1f5f9;
    }
    .chapter-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        background-color: #2d3a5e;
    }
    .chapter-card .chapter-num {
        font-weight: bold;
        font-size: 1.1rem;
        color: #a78bfa;
    }
    .chapter-card .chapter-desc {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 5px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #2a5298;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #667eea;
    }
    
    /* Loading spinner */
    .stSpinner {
        text-align: center;
    }
    
    /* Markdown text trong agent message */
    .agent-message p, .agent-message li, .agent-message div {
        color: #f1f5f9;
    }
    .agent-message strong, .agent-message b {
        color: #a78bfa;
    }
    
    /* Nút trong sidebar */
    .stMarkdown {
        color: #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1> LEGAL AGENT</h1>
    <p>Trợ lý AI thông minh - Hỗ trợ tra cứu Nghị định 168 về đăng ký doanh nghiệp</p>
    <div class="badge"> Tự động truy xuất tham chiếu chéo |  Rerank kết quả |  Hướng dẫn chi tiết</div>
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
    st.markdown("""
    <div class="sidebar-header">
        <div style="font-size: 3rem;"></div>
        <h3>Legal Agent</h3>
        <p>Nghị định 168/NĐ-CP</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("###  Chọn Chương")
    
    chapters = st.session_state.agent.get_chapters()
    
    for chapter in chapters:
        topic = CHAPTER_TOPICS.get(chapter, {"short_name": f"CHƯƠNG {chapter}", "color": "#888888"})
        if st.button(f" {topic['short_name']}", key=f"btn_{chapter}"):
            st.session_state.agent.set_chapter(chapter)
            st.session_state.current_chapter = chapter
            st.session_state.chat_history = []
            st.rerun()
    
    if st.session_state.current_chapter:
        topic = CHAPTER_TOPICS.get(st.session_state.current_chapter, {})
        st.markdown("---")
        st.markdown(f"""
        <div style="background: {topic.get('color', '#2a5298')}20; padding: 12px; border-radius: 10px; margin-top: 15px;">
            <b style="color: #a78bfa;"> Đang tư vấn</b><br>
            <span style="font-size: 0.85rem; color: #f1f5f9;">{topic.get('short_name', f'Chương {st.session_state.current_chapter}')}</span>
            <p style="font-size: 0.7rem; color: #94a3b8; margin-top: 5px;">{topic.get('desc', '')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(" Nguồn dữ liệu: Nghị định 168/2020/NĐ-CP")
    st.caption(" Cập nhật: 2024")

# Main content
if st.session_state.current_chapter is None:
    st.markdown("""
    <div class="info-box">
        <b> Hướng dẫn</b><br>
         Vui lòng chọn một Chương từ thanh bên trái để bắt đầu tư vấn.<br>
         Bạn có thể hỏi về thủ tục, hồ sơ, trình tự đăng ký doanh nghiệp theo từng Chương cụ thể.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("###  Danh sách các Chương")
    
    cols = st.columns(3)
    for i, chapter in enumerate(chapters[:9]):
        topic = CHAPTER_TOPICS.get(chapter, {"short_name": f"CHƯƠNG {chapter}", "desc": "", "color": "#888888"})
        with cols[i % 3]:
            st.markdown(f"""
            <div class="chapter-card" style="border-left: 4px solid {topic.get('color', '#888888')};">
                <div class="chapter-num">{topic.get('short_name', f'Chương {chapter}')}</div>
                <div class="chapter-desc">{topic.get('desc', '')}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="clearfix">
                    <div class="user-message">
                        <b> Bạn</b><br>{msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="clearfix">
                    <div class="agent-message">
                        <b> Legal Agent</b><br>{msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            " Nhập câu hỏi của bạn:",
            key="input",
            placeholder="Ví dụ: Thủ tục đăng ký doanh nghiệp qua mạng?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button(" Gửi câu hỏi", type="primary", use_container_width=True)
    
    if send_button and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner(" Đang tra cứu và tổng hợp câu trả lời..."):
            result = st.session_state.agent.ask(user_input)
        
        st.session_state.chat_history.append({"role": "assistant", "content": result['answer']})
        st.rerun()
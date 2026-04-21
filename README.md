# 📚 LEGAL AGENT - Hệ thống tư vấn Nghị định 168 về đăng ký doanh nghiệp

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.7.3-green.svg)](https://qdrant.tech/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📌 Giới thiệu

**Legal Agent** là một hệ thống trợ lý ảo thông minh chuyên tư vấn và tra cứu **Nghị định 168/NĐ-CP** về đăng ký doanh nghiệp. Dự án được xây dựng như một bài tập nhóm, áp dụng các kỹ thuật xử lý ngôn ngữ tự nhiên (NLP) và trí tuệ nhân tạo (AI) để giải quyết bài toán tra cứu văn bản pháp luật một cách hiệu quả.

### 🎯 Mục tiêu

- Tự động hóa việc tra cứu thông tin từ văn bản pháp luật dài hàng trăm trang
- Cung cấp câu trả lời chính xác, nhanh chóng thay vì đọc toàn bộ văn bản
- Hỗ trợ người dùng cuối (doanh nghiệp, cá nhân) trong việc tìm hiểu thủ tục đăng ký kinh doanh
- Ứng dụng các công nghệ AI hiện đại như RAG, Hybrid Search, Reranking

---

## ✨ Tính năng nổi bật

| Tính năng | Mô tả |
|-----------|-------|
| **Xử lý PDF scanned** | Có thể xử lý file PDF được scan từ sách giấy bằng EasyOCR + tiền xử lý ảnh |
| **Parse cấu trúc pháp luật** | Tự động nhận diện Chương, Điều, Khoản, Điểm từ văn bản thô |
| **Hybrid Search** | Kết hợp BM25 (tìm kiếm từ khóa) + Dense Embedding (tìm kiếm ngữ nghĩa) |
| **Reranking** | Tái sắp xếp kết quả tìm kiếm bằng Cross-Encoder để ưu tiên thông tin liên quan nhất |
| **Truy xuất tham chiếu chéo** | Tự động lấy nội dung của Điều/Khoản được nhắc đến trong văn bản |
| **Cache thông minh** | Lưu cache OCR, câu trả lời, model config để tăng tốc độ |
| **Hướng dẫn chi tiết** | Câu trả lời kèm hướng dẫn thực hiện, giấy tờ cần chuẩn bị, cơ quan có thẩm quyền |
| **Giao diện Streamlit** | Web app thân thiện, dễ sử dụng, hiển thị rõ nguồn tham khảo |

---
┌─────────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 1 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────────┐ │
│ │ OCR + Cache │ -> │ Parser │ -> │ Qdrant Vector DB + BM25 Index │ │
│ │ (EasyOCR) │ │ (thông minh)│ │ │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 2 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────────┐ │
│ │ Hybrid │ -> │ Reranker │ -> │ Cross-Reference Resolution │ │
│ │ Search │ │ │ │ │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 3 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────────┐ │
│ │ LLM │ -> │ Prompt │ -> │ Câu trả lời + Hướng dẫn chi tiết │ │
│ │ (TinyLlama) │ │ Engineering │ │ │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GIAO DIỆN │
│ Streamlit App │
└─────────────────────────────────────────────────────────────────────────────┘



---

## Cấu trúc dự án
Chatbot_NLP/
│
├── README.md # Tài liệu dự án
├── requirements.txt # Danh sách thư viện
│
├── config.py # Cấu hình hệ thống
├── utils.py # Hàm tiện ích
│
├── data/ # Module xử lý dữ liệu
│ ├── init.py
│ ├── gd1_ocr.py # OCR và cache
│ ├── gd1_parser.py # Parse văn bản pháp luật
│ └── gd1_chunker.py # Chunking và tạo database
│
├── retrieval/ # Module truy xuất
│ ├── init.py
│ └── qdrant_retriever.py # Hybrid search + Rerank
│
├── agent/ # Module agent
│ ├── init.py
│ ├── legal_agent.py # Agent export
│ └── legal_agent_crossref.py # Agent với cross-reference
│
├── gd1_main.py # Chạy giai đoạn 1
├── gd2_main.py # Chạy giai đoạn 2 (CLI)
├── app.py # Ứng dụng Streamlit
│
├── nghi_dinh_168.pdf # File PDF Nghị định (cần có)
│
├── qdrant_legal_db/ # Qdrant database (tự tạo khi chạy)
├── metadata_qdrant/ # Metadata (tự tạo khi chạy)
├── ocr_cache/ # Cache OCR (tự tạo khi chạy)
│
└── NLP/ # Môi trường ảo Python


##  Kiến trúc hệ thống

### Giải thích các thư mục

| Thư mục/File | Chức năng |
|--------------|-----------|
| `data/` | Xử lý dữ liệu đầu vào: OCR, parse, chunking |
| `retrieval/` | Tìm kiếm và truy xuất thông tin từ database |
| `agent/` | Logic chính của chatbot, sinh câu trả lời |
| `qdrant_legal_db/` | Thư mục lưu vector database (tự tạo khi chạy GĐ1) |
| `metadata_qdrant/` | Lưu metadata và BM25 index |
| `ocr_cache/` | Lưu cache OCR để tăng tốc lần chạy sau |

---

## 🛠️ Công nghệ sử dụng

| Công nghệ | Vai trò |
|-----------|---------|
| **Python 3.10+** | Ngôn ngữ lập trình chính |
| **Streamlit** | Xây dựng giao diện web |
| **Qdrant** | Vector database, lưu trữ và tìm kiếm embeddings |
| **BM25** | Tìm kiếm từ khóa chính xác |
| **Sentence-BERT** | Tạo embeddings tiếng Việt |
| **Cross-Encoder** | Rerank kết quả tìm kiếm |
| **EasyOCR** | Nhận dạng chữ từ PDF scanned |
| **OpenCV** | Tiền xử lý ảnh (tăng contrast, nhị phân hóa) |
| **PyMuPDF** | Đọc và render PDF |
| **TinyLlama / Qwen** | LLM sinh câu trả lời |
| **LangChain** | Kết nối các thành phần |
| **Transformers** | Load và chạy mô hình Hugging Face |

---

##  Cài đặt và chạy

### Yêu cầu hệ thống

| Thành phần | Yêu cầu |
|------------|---------|
| Hệ điều hành | Windows / Linux / macOS |
| RAM | 8 GB (khuyến nghị 16 GB) |
| Python | 3.10 trở lên |
| Disk trống | 10 GB (cho model và database) |
| Internet | Cần để tải model lần đầu |

### Bước 1: Clone dự án

```bash
git clone https://github.com/yourusername/legal-agent.git
cd legal-agent

# Windows
python -m venv NLP
NLP\Scripts\activate

# Linux/Mac
python -m venv NLP
source NLP/bin/activate
Bước 2:Tạo môi trường ảo
# Windows
python -m venv NLP
NLP\Scripts\activate

# Linux/Mac
python -m venv NLP
source NLP/bin/activate

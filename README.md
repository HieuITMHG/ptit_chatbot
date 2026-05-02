# 🤖 PTIT Chatbot - Hệ thống RAG Chatbot cho PTIT

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Celery](https://img.shields.io/badge/celery-%23a9cc54.svg?style=for-the-badge&logo=celery&logoColor=f1f1f1)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

Hệ thống Chatbot RAG (Retrieval-Augmented Generation) được thiết kế đặc biệt dành riêng cho Học viện Công nghệ Bưu chính Viễn thông (PTIT). Hệ thống giúp sinh viên và người dùng tra cứu thông tin nhanh chóng, chính xác dựa trên cơ sở dữ liệu thực tế từ trang chủ của trường.

## ✨ Các tính năng nổi bật (Key Features)

* **Tự động thu thập dữ liệu (Web Scraping):** Cào và cập nhật dữ liệu từ các bài đăng chính thức trên cổng thông tin `ptithcm.edu.vn`.
* **Xử lý văn bản nâng cao:** Sử dụng kỹ thuật Semantic Chunking và Embedding với mô hình tối ưu `BAAI/bge-m3` (hoặc bga3).
* **Truy xuất ngữ cảnh chính xác:** Tích hợp bộ tìm kiếm Vector (Retrieve Context) và cơ chế đánh giá chéo (Cross-Encoder Rerank) sử dụng mô hình `ms-marco-MultiBERT-L-12`, giúp lọc ra các ngữ cảnh liên quan nhất.
* **Chống ảo giác (Anti-Hallucination):** Bot tuân thủ quy tắc nghiêm ngặt: *Chỉ trả lời dựa trên ngữ cảnh được cung cấp*. Nếu thông tin không có trong cơ sở dữ liệu, bot sẽ từ chối trả lời để đảm bảo tính xác thực.
* **Real-time Streaming:** Xử lý RAG dưới background và trả lời người dùng mượt mà theo thời gian thực thông qua **Websocket**.

## 🛠️ Công nghệ sử dụng (Tech Stack)

**Backend & AI Pipeline:**
* **FastAPI:** Xây dựng RESTful API và Websocket tốc độ cao.
* **Celery:** Xử lý hàng đợi, chạy các tác vụ RAG nặng dưới nền.
* **FlagEmbedding:** Load và chạy các mô hình AI (Embedding, Reranker).
* **BeautifulSoup4 & Trafilatura:** Trích xuất nội dung và metadata từ mã nguồn HTML.

**Cơ sở dữ liệu (Database):**
* **MongoDB:** Lưu trữ dữ liệu thô (plain text) và các chunk chưa embed.
* **Qdrant:** Vector Database hiệu năng cao để lưu trữ và tìm kiếm các chunk đã embed.
* **Redis:** Message Broker cho Celery và lưu trữ bộ nhớ đệm.

**Deploy & DevOps:**
* **Docker & Docker Compose:** Đóng gói và quản lý các service.
* **Nginx:** Web server, Reverse proxy và xử lý chứng chỉ SSL.

## 📸 Hình ảnh Demo (Screenshots)

<p align="center">
  <img src="./assets/login.png" alt="Chatbot Demo">
</p>

<p align="center">
  <img src="./assets/chatbox.png" alt="Chatbot Demo">
</p>

---

## 🚀 Hướng dẫn Cài đặt & Triển khai (Deployment)

Yêu cầu hệ thống: Đã cài đặt sẵn `Git`, `Docker` và `Docker Compose` trên Server/VPS.

### 1. Clone Project
Tải mã nguồn về máy tính hoặc máy chủ của bạn:
```bash
git clone [https://github.com/your-username/ptit_chatbot.git](https://github.com/your-username/ptit_chatbot.git)
cd ptit_chatbot
```

### 2. Tạo Docker Network (Bắt buộc)
Tạo mạng nội bộ để các container có thể giao tiếp với nhau:
```bash
docker network create chatbot_net
```

### 3. Cấu hình Biến môi trường (`.env.prod`)
Hệ thống yêu cầu file `.env.prod` để chạy môi trường Production. Hãy sửa các thông số hostname về tên của Docker Service như sau:

```ini
ENV=production

# Dự án này dùng openai api
OPENAI_KEY=your-openai-api-key

# Thiết lập URL kết nối qua tên service trong Docker
S3_ENDPOINT=http://minio:9000
MONGODB_URI=mongodb://admin:admin123@mongo:27017/PTITBOT?authSource=admin
QDRANT_ENDPOINT=http://qdrant:6333
REDIS_URL=redis://redis:6379/0

# Thông tin bảo mật hệ thống
SECRET_KEY=supersecretkey
TEST_USERNAME=admin
TEST_PASSWORD=123456
```

Đổi 2 giá trị trong frontend/.env thành domain của bạn:
```ini
VITE_API_BASE_URL=[https://your-domain.com/api](https://your-domain.com/api)
VITE_WS_BASE_URL=wss://[your-domain.com/api](https://your-domain.com/api)
```

### 4. Build Docker Image (Preload Model)
Tiến hành build image. Quá trình này sẽ bao gồm việc tải các mô hình AI và build frontend + backend.
> ⏳ *Lưu ý: Lần đầu tiên chạy sẽ mất một chút thời gian để tải model có dung lượng lớn.*
```bash
make build-prod
```

### 5. Chạy quá trình ETL (Chỉ chạy 1 lần duy nhất)
Tiến hành cào dữ liệu, làm sạch, phân mảnh (chunking), nhúng (embedding) và lưu vào cơ sở dữ liệu.
```bash
docker compose -f docker-compose.prod.yml run --rm etl
```

### 6. Khởi chạy toàn bộ hệ thống
Sau khi mọi thứ đã sẵn sàng, hãy khởi động toàn bộ các service:
```bash
make run
```
Hệ thống hiện đã hoạt động! Bạn có thể truy cập thông qua Domain của mình.

---

## 🤝 Đóng góp (Contributing)
Mọi ý kiến đóng góp, báo lỗi (issues) và pull requests đều được hoan nghênh để làm dự án hoàn thiện hơn.

## 📝 Giấy phép (License)
Dự án được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.
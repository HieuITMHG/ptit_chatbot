#PTIT CHATBOT

## Giới thiệu

Project phát triển một hệ thống chatbot dựa trên nền tảng RAG, tận dụng sức mạng của LLM để trả lời linh hoạt tự nhiên các thông tin publish của nhà trường. Giúp sinh viên tra cứu thông tin cần thiết một cách nhanh chóng và tiện lợi.

## Điểm đáng chú ý

## Tech List

## Mục tiêu

Tạo nên một hệ thống RAG hoàn chỉnh, có thể retrive đúng context. Một app hoàn chỉnh, có giao diện, có api, desploy lên server.

Những việc cần làm tiếp theo:
- Refac lại cấu trúc thư mục, đảm bảo dể hiểu, dể triển khai từ đó biết nên code gì tiếp theo, trong file viết class hay hàm
- Xác định các embedding model dùng để thử nghiệm -> bỏ vào file config
- Viết code để embed các quote vào qdrant, mỗi embedding model sẽ có một collection riêng
- Viết các file, mỗi file dùng các matric để khác nhau sử dụng ground truth và dữ liệu retrieve về để tính toán
- Viết pipeline để chạy các file eval trên và vẻ chart ra

- Sau khi xác định được embedding model ta sẽ viết code để embedding các chunk
- Sau đó sẽ xây pipeline cơ bản nhất của RAG
- Viết pipeline để eval RAG, và tiếp tục thử nghiệm các kiến trúc RAG khác nhau và viết lại báo cáo

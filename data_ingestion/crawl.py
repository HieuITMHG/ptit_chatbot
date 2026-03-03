import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    # Sử dụng context manager để tự động đóng crawler khi xong
    async with AsyncWebCrawler(verbose=True) as crawler:
        # Thực hiện crawl link
        result = await crawler.arun(url="https://ptithcm.edu.vn/sinh-vien/hoat-dong-ngoai-khoa/sinh-vien-hoc-vien-cn-bcvt-voi-dot-trai-cua-tap-doan-vnpt.html")
        
        # In nội dung đã được chuyển sang Markdown (rất gọn để nạp vào AI)
        print("\n--- NỘI DUNG MARKDOWN ---")
        print(result.markdown) # In 500 ký tự đầu tiên

if __name__ == "__main__":
    asyncio.run(main())
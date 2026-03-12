import json
from rapidfuzz import fuzz, process

context = """
Giới thiệu ngành Công nghệ phần mềm

**Phần mềm là gì?**

![](https://ptithcm.edu.vn/wp-content/uploads/2020/06/GioiThieuCNPM1-300x168.jpg)

*Phần mềm được coi là tập hợp mã lập trình thực thi, thư viện và tài liệu liên quan.*

Phần mềm là một, hay nhiều chương trình máy tính kết hợp với nhau, để cung cấp các chức năng và tiện ích cho người dùng.

**Phần mềm được đánh giá như thế nào?**

![](https://ptithcm.edu.vn/wp-content/uploads/2020/06/GioiThieuCNPM2-300x218.jpg)

*Một sản phẩm phần mềm có thể được đánh giá qua những gì nó cung cấp và mức độ sử dụng của nó.*

Một sản phẩm phần mềm được đánh giá thông qua các tính năng mà nó cung cấp cho người dùng và dễ sử dụng. Một ứng dụng phải đạt được các mặt sau:

1) Sẵn sàng để dùng: Phần mềm phải thỏa mãn điều kiện về ngân sách, tính khả dụng, hiệu quả, tính chính xác, chức năng, độ tin cậy, bảo mật và an toàn. Khía cạnh này cho chúng ta biết phần mềm hoạt động tốt như thế nào trong khi vận hành.

2) Chuyển tiếp: Phần mềm phải có tính di động, tái sử dụng và khả năng tích ứng để có chuyển từ nền tảng này sang nền tảng khác. Khía cạnh này rất quan trọng khi phần mềm được chuyển từ nền tảng này sang nền tảng khác.

3) Bảo trì: Phần mềm phải có tính mô đun, khả năng bảo trì, tính linh hoạt và khả năng mở rộng. Khía cạnh này cho biết phần mềm có khả năng tự duy trì tốt như thế nào trong môi trường luôn thay đổi.

**Công nghệ phần mềm là gì?**

![](https://ptithcm.edu.vn/wp-content/uploads/2020/06/GioiThieuCNPM3-300x150.jpg)

*Kết quả của công nghệ phần mềm là một sản phẩm phần mềm hiệu quả và đáng tin cậy.*

Công nghệ phần mềm là qui trình làm việc có hệ thống để thiết kế, phát triển, kiểm thử, vận hành và bảo trì hệ thống phần mềm.

Ngành học Công nghệ phần mềm nghiên cứu chi tiết về kỹ thuật để thiết kế, phát triển và bảo trì phần mềm; giải quyết các vấn đề của các dự án phần mềm, bảo đảm các ứng dụng được xây dựng nhất quán, chính xác, đúng thời gian, phù hợp ngân sách và trong phạm vi yêu cầu; thỏa mãn nhu cầu thay đổi nhanh chóng của người dùng và môi trường hoạt động của ứng dụng.

**Kỹ sư công nghệ phần mềm có những vị trí việc làm nào?**

![](https://ptithcm.edu.vn/wp-content/uploads/2020/06/GioiThieuCNPM4-300x161.jpg)

*Trí tuệ nhân tạo đang chuyển đổi Công nghệ phần mềm*

Các vị trí việc làm thuộc chuyên môn của kỹ sư công nghệ phần mềm:

- Xây dựng ứng dụng chạy trên máy tính (Applications developer)
- Quản trị cơ sở dữ liệu (Database administrator)
- Xây dựng phần mềm trò chơi (Game developer)
- Thiết kế và xây dựng website (Web designer and Web developer)
- Kiểm thử phần mềm (Software tester)

**Kỹ sư công nghệ phần mềm có thể làm việc ở đâu?**

Kỹ sư phần mềm làm việc trong các công ty chuyên về phát triển phần mềm hoặc các tổ chức, cơ quan, công ty, doanh nghiệp có ứng dụng công nghệ thông tin trong điều hành, hoạt động sản xuất, kinh doanh, cụ thể như:

- Doanh nghiệp chuyên kinh doanh về công nghệ thông tin
- Các tổ chức và doanh nghiệp cung cấp dịch vụ tài chính, ngân hàng
- Các tổ chức và doanh nghiệp về truyền thông đa phương tiện
- Các cơ quan chính quyền
- Các công ty cung cấp các dịch vụ tiện ích cho cộng đồng
- Các công ty thương mại
- Các công ty vận tải
- Bệnh viện và các cơ sở chăm sóc sức khỏe
- Các công ty, nhà máy chế tạo thuộc nhiều lĩnh vực

…

Một lựa chọn khác cho kỹ sư phần mềm là thành lập doanh nghiệp riêng hoặc tự hợp đồng nhận dự án như một freelancer, cung cấp phần mềm hoặc các dịch vụ liên quan đến công nghệ thông tin.
"""

def quote_match_score(context: str, quote: str):
    return fuzz.partial_ratio(quote, context)

# def get_best_quote(context: str, quote: str):
#     slide_window = len(quote) 
#     end = len(context)
#     best_score = 0
#     best_span = ""

#     for i in range(0, end, 1):
#         span = context[i: i + slide_window]
#         score = quote_match_score(span, quote)
        
#         if score >= best_score:
#             best_score = score
#             best_span = span
        
#     return best_span, best_score

def get_best_quote(context: str, quote: str):

    alignment = fuzz.partial_ratio_alignment(quote, context)

    score = alignment.score
    start = alignment.dest_start
    end = alignment.dest_end

    best_span = context[start:end]

    return best_span, score

if __name__ == "__main__":
    with open("embedding_eval/ds_gen/test_output.json", "r", encoding="utf-8") as f:
        res = json.load(f)

    for query in res:
        for quote in query["quotes"]:
            best_span, best_score = get_best_quote(context=context, quote=quote)
            print(f"Quote của LLM: {quote}")
            print(f"Quote ta tìm được: {best_span}")
            print(f"Score: {best_score}")
            print("===============================================")

            
        
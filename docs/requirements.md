# Phân tích yêu cầu — Quản lý văn bản cá nhân

Ngày: 23/09/2026. Trạng thái: bản nháp để trao đổi, chưa phải phạm vi đã được duyệt.

## 1. Mục tiêu và căn cứ

Giúp một người lưu thông tin văn bản, đính kèm tài liệu và tìm lại nhanh trên máy Windows, kể cả khi không có Internet.

**Đã xác định từ yêu cầu và câu trả lời của người dùng:**

- Sử dụng cá nhân, một người dùng, hoạt động offline, hỗ trợ Windows.
- Ứng dụng web đơn giản là một phương án đang cân nhắc, chưa phải lựa chọn triển khai cuối cùng.
- Phân loại theo loại văn bản: công văn, quyết định, thông báo…
- Tìm kiếm trong thông tin đã nhập: số văn bản, cơ quan, nội dung tóm tắt. Tìm chữ bên trong file và OCR không thuộc phạm vi hiện tại.
- Quy mô dự kiến dưới 10.000 văn bản.

**Đọc từ bản phác thảo:** bộ chọn loại công văn; ô tìm kiếm; bảng gồm Số CV, Ngày, CQBH, Nội dung, File. CQBH được chú thích là cơ quan ban hành. Ngày hiển thị theo ngày/tháng/năm. File gồm hình ảnh, Excel, Word, PDF.

Các nội dung dưới đây là đề xuất phân tích, không mặc nhiên coi là yêu cầu đã được người dùng xác nhận. Chưa chọn ngôn ngữ, framework hay bắt đầu xây dựng ứng dụng.

## 2. Các giả định cần xác nhận

| Điểm chưa rõ | Giả định cho bản nháp | Ảnh hưởng nếu khác |
| --- | --- | --- |
| Đính kèm | Một văn bản có thể có nhiều file, cũng được phép chưa có file | Ảnh hưởng biểu mẫu và quy tắc lưu |
| Dung lượng | Dùng 10.000 bản ghi làm mốc kiểm thử, bao phủ quy mô đã xác nhận | Cần biết thêm tổng dung lượng file và kích thước file lớn nhất |
| Máy sử dụng | Một máy Windows tại một thời điểm | Chuyển máy bằng sao lưu/khôi phục; đồng bộ nhiều máy là phạm vi khác |
| Phiên bản Windows | Chưa chốt phiên bản và kiến trúc CPU | Phải xác nhận trước khi chọn cách đóng gói và nghiệm thu |

Loại văn bản, hướng đến/đi và nhóm cá nhân là ba khái niệm khác nhau. Theo xác nhận hiện tại, chỉ đưa loại văn bản vào phạm vi; không thêm hướng đến/đi hay nhóm cá nhân.

## 3. Phạm vi bản đầu đề xuất

| Mã | Chức năng | Hành vi cần có |
| --- | --- | --- |
| FR-01 | Danh sách văn bản | Hiển thị các cột theo hình; có phân trang, số kết quả, sắp xếp theo ngày ban hành |
| FR-02 | Thêm và sửa | Nhập thông tin, chọn file, lưu; giữ thông tin đang nhập nếu xảy ra lỗi |
| FR-03 | Chi tiết | Xem đầy đủ trích yếu và danh sách file; chuyển sang sửa từ màn hình này |
| FR-04 | Phân loại | Chọn loại khi nhập và lọc theo loại; cho phép thêm, đổi tên loại |
| FR-05 | Tìm kiếm | Tra số/ký hiệu, cơ quan, trích yếu; hỗ trợ không phân biệt hoa thường và dấu tiếng Việt |
| FR-06 | Bộ lọc | Kết hợp loại, cơ quan và khoảng ngày ban hành; có nút xóa bộ lọc |
| FR-07 | File đính kèm | Thêm nhiều file, xem tên/dung lượng, lấy bản sao để mở, gỡ file khỏi bản ghi |
| FR-08 | Xóa và khôi phục | Chuyển văn bản vào thùng rác; khôi phục kèm file; xóa vĩnh viễn phải xác nhận |
| FR-09 | Sao lưu | Tạo một gói gồm cơ sở dữ liệu, file và thông tin phiên bản; hiển thị kết quả và thời điểm sao lưu thành công |
| FR-10 | Khôi phục bản sao lưu | Kiểm tra gói trước khi thay dữ liệu; sao lưu dữ liệu hiện tại; báo rõ phạm vi thay thế |
| FR-11 | Khởi chạy trên Windows | Bấm biểu tượng để mở ứng dụng; người dùng không phải tự khởi động từng thành phần |

Danh mục cơ quan nên có gợi ý từ dữ liệu đã nhập để giảm các cách viết khác nhau, đồng thời cho phép nhập cơ quan mới ngay trên biểu mẫu. Không được xóa một loại đang được sử dụng nếu chưa chuyển các văn bản sang loại khác.

**Để sau, nếu có nhu cầu:** nhập danh sách Excel có sẵn; xuất danh sách Excel; tìm chữ trong file; OCR ảnh/scan; đánh dấu yêu thích; nhãn cá nhân; nhắc sao lưu hoặc sao lưu tự động.

**Ngoài phạm vi hiện tại:** tìm chữ bên trong file và OCR; tài khoản và phân quyền nhiều người, phê duyệt văn bản, ký số, giao việc, gửi email, đồng bộ cloud, truy cập từ máy khác, trình soạn thảo Word/Excel tích hợp.

## 4. Dữ liệu và quy tắc nhập

| Trường | Đề xuất | Quy tắc |
| --- | --- | --- |
| Mã nội bộ | Tự sinh, không cần hiện trên bảng | Dùng để nhận diện bản ghi, độc lập với số văn bản |
| Loại văn bản | Bắt buộc | Chọn từ danh mục |
| Số/ký hiệu văn bản | Không bắt buộc | Dạng chữ, ví dụ `123/QĐ-ABC`; giữ số 0 đầu và dấu phân cách |
| Ngày ban hành | Bắt buộc | Nhập/chọn ngày hợp lệ; hiển thị `dd/MM/yyyy`; phân biệt với ngày nhập phần mềm |
| Cơ quan ban hành | Bắt buộc | Có gợi ý và cho nhập mới |
| Nội dung/trích yếu | Bắt buộc | Văn bản thuần nhiều dòng; bảng chỉ hiện tóm tắt, chi tiết hiện đầy đủ |
| File đính kèm | 0 đến nhiều file | PDF, DOC/DOCX, XLS/XLSX, JPG/JPEG, PNG là danh sách ban đầu đề xuất |
| Ngày tạo/cập nhật | Tự ghi | Không dùng thay cho ngày ban hành |

Các trường bắt buộc là đề xuất; nếu cần lưu hồ sơ thiếu thông tin, phải cho phép bản nháp hoặc giảm điều kiện bắt buộc trước khi triển khai.

Số văn bản không duy nhất trên toàn hệ thống: hai cơ quan hoặc hai năm có thể dùng cùng số. Đề xuất cảnh báo khi trùng số/ký hiệu, cơ quan và năm ban hành; người dùng vẫn có thể tiếp tục sau khi kiểm tra. Không tự ghi đè bản ghi cũ.

Tìm kiếm dùng bản chuẩn hóa phục vụ đối chiếu, vẫn giữ nguyên tiếng Việt để hiển thị. Ví dụ `quyet dinh` tìm được `Quyết định`; `don vi` tìm được `Đơn vị`. Đề xuất mỗi từ trong truy vấn phải xuất hiện ở ít nhất một trường được tìm; các bộ lọc áp dụng đồng thời. Danh sách mặc định không bao gồm thùng rác.

## 5. Quản lý file

1. Khi đính kèm, phần mềm **sao chép file vào kho dữ liệu do ứng dụng quản lý**. Không chỉ lưu đường dẫn đến Downloads, Desktop hoặc USB.
2. Di chuyển hoặc xóa file nguồn sau khi lưu thành công không làm mất file trong ứng dụng. Bản sao đã nhập không tự thay đổi khi file nguồn được sửa.
3. Giữ tên gốc để hiển thị nhưng lưu bằng định danh riêng, tránh ghi đè khi hai file trùng tên. Quan hệ tới file không phụ thuộc ký tự ổ đĩa của máy cũ.
4. Bản đầu phải lưu và lấy lại đúng file gốc. Xem trước PDF/ảnh có thể bổ sung; xem trước hay chỉnh sửa Word/Excel ngay trong giao diện chưa thuộc phạm vi bắt buộc.
5. Với giao diện web, nút tải/mở cung cấp một bản sao để người dùng mở bằng ứng dụng phù hợp trên Windows. Máy phải có phần mềm đọc định dạng đó. Sửa bản sao bên ngoài không tự cập nhật file đã lưu; người dùng đính kèm phiên bản mới nếu cần.
6. Thông báo rõ nếu file không được hỗ trợ, bị thiếu, vượt giới hạn hoặc ổ đĩa không đủ chỗ. Không báo lưu thành công khi thao tác sao chép chưa hoàn tất.
7. Giới hạn mỗi file và tổng mỗi lần thêm cần chốt từ mẫu dữ liệu thực tế. Khi thử nghiệm phải có file lớn, tên tiếng Việt, tên trùng và nhiều file cùng lúc.

Đề xuất khi sửa: gỡ file chỉ có hiệu lực sau khi bấm Lưu và xác nhận; Hủy giữ nguyên file. Khi xóa văn bản vào thùng rác, giữ nguyên toàn bộ file để có thể phục hồi. Bản đầu không cần hệ thống quản lý lịch sử phiên bản tài liệu.

## 6. Bố cục và luồng sử dụng

Màn hình chính bám theo hình: thanh chọn loại và ô tìm kiếm ở trên; bảng văn bản ở dưới. Bổ sung nút **Thêm văn bản**, bộ lọc ngày/cơ quan, chỉ báo số kết quả và phân trang. Cột File hiển thị số lượng file, ví dụ `3 file`, để bảng gọn.

Các màn hình/phần giao diện cần có:

- Danh sách và tìm kiếm.
- Biểu mẫu thêm/sửa và phần chi tiết văn bản.
- Danh mục loại văn bản.
- Thùng rác.
- Sao lưu/khôi phục và thông tin thư mục dữ liệu.

Luồng thường dùng: mở ứng dụng → thêm văn bản → nhập thông tin → chọn file → lưu → tìm/lọc → mở chi tiết → lấy file để xem. Khi đóng biểu mẫu có thay đổi chưa lưu, hỏi người dùng lưu hay bỏ thay đổi.

## 7. Phương án chạy offline trên Windows

**Đề xuất: ứng dụng web cục bộ, được đóng gói để khởi chạy bằng một biểu tượng.** Giao diện mở trong trình duyệt, còn chương trình xử lý và dữ liệu đều nằm trên máy người dùng.

```text
Biểu tượng ứng dụng trên Windows
              ↓
Giao diện trong trình duyệt ↔ Chương trình chạy cục bộ
                                      ├── SQLite: thông tin văn bản
                                      └── Kho file đính kèm
```

Đây là lựa chọn thiết kế đề xuất dựa trên nhu cầu một người và dữ liệu cục bộ. SQLite được thiết kế cho việc lưu dữ liệu trong ứng dụng/thiết bị và được dùng cho ứng dụng desktop; không cần vận hành một máy chủ cơ sở dữ liệu riêng. Nguồn: [SQLite — Appropriate Uses](https://www.sqlite.org/whentouse.html).

Không đặt bản lưu duy nhất trong bộ nhớ trình duyệt: dữ liệu web có các chính sách hạn mức và khả năng bị dọn, tùy cơ chế lưu trữ và trình duyệt. Thiết kế đề xuất lưu dữ liệu trong thư mục riêng trên ổ đĩa, để xóa dữ liệu trình duyệt không làm mất hồ sơ. Nguồn: [MDN — Storage quotas and eviction](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria).

Chưa cần quyết định framework ở giai đoạn này. Nếu người dùng muốn cửa sổ ứng dụng riêng thay cho tab trình duyệt, có thể đóng gói giao diện trong ứng dụng desktop; cần đánh giá thêm bộ cài và yêu cầu Windows trước khi chọn công nghệ.

## 8. Yêu cầu vận hành và bảo toàn dữ liệu

- **Offline đầy đủ:** bộ cài phải chứa các thành phần cần thiết; khởi chạy lần đầu sau khi cài, nhập liệu, tìm kiếm và sao lưu đều hoạt động khi ngắt mạng. Không phụ thuộc CDN, font trực tuyến, dịch vụ OCR online hay đăng nhập từ xa.
- **Giới hạn truy cập:** chương trình chỉ nhận kết nối từ chính máy đang chạy; không mở cho mạng LAN/Internet. Không cần màn hình đăng nhập riêng theo giả định một người sử dụng tài khoản Windows cá nhân. Mã hóa hoặc khóa ứng dụng là yêu cầu riêng nếu có dữ liệu nhạy cảm.
- **Lưu bền vững:** chỉ báo thành công sau khi dữ liệu và file đã được ghi; lỗi nhập file không để lại hồ sơ thể hiện đính kèm thành công nhưng file không tồn tại.
- **Vòng đời ứng dụng:** bấm biểu tượng nhiều lần không tạo nhiều tiến trình tranh cùng kho dữ liệu; có cách thoát rõ ràng; mở lại vẫn giữ dữ liệu. Đóng tab không đồng nghĩa xóa dữ liệu.
- **Nâng cấp:** kho dữ liệu tách khỏi thư mục chương trình; cài bản mới không xóa hồ sơ. Có sao lưu trước khi nâng cấp cấu trúc dữ liệu.
- **Sao lưu nhất quán:** tạm ngăn thay đổi hồ sơ/file khi tạo gói; tạo snapshot cơ sở dữ liệu bằng cơ chế phù hợp, rồi đóng gói đủ file liên quan. Không chỉ sao chép file cơ sở dữ liệu đang được ghi. SQLite cung cấp cơ chế snapshot phục vụ sao lưu: [SQLite Backup API](https://www.sqlite.org/backup.html).
- **Khôi phục:** kiểm tra phiên bản và tính đầy đủ của gói trước khi áp dụng; bao gồm cả danh mục, hồ sơ trong thùng rác và file. Bản đầu khôi phục bằng thay thế toàn bộ dữ liệu, chưa gộp hai kho. Nếu thất bại, giữ hoặc khôi phục được dữ liệu trước thao tác.
- **Vị trí sao lưu:** người dùng chọn được USB/ổ ngoài hoặc thư mục khác. Một bản sao trên cùng ổ giúp xử lý thao tác nhầm nhưng không bảo vệ khi ổ đó hỏng.
- **Hiệu năng đề xuất:** với 10.000 bản ghi thông tin trên máy tham chiếu SSD/RAM 8 GB, mục tiêu 95% thao tác tìm/lọc trả trang đầu trong 1 giây; chưa tính việc mở file trong phần mềm khác. Chốt máy, dữ liệu mẫu và phép đo trước nghiệm thu, không coi đây là hiệu năng đã kiểm chứng.

## 9. Tiêu chí nghiệm thu bản đầu

| Mã | Tình huống | Kết quả mong đợi |
| --- | --- | --- |
| AC-01 | Ngắt mạng trước lần chạy đầu sau khi cài | Mở được, thêm và tìm lại văn bản được |
| AC-02 | Lưu văn bản có số/ký hiệu, ngày, tiếng Việt và nhiều loại file; đóng mở lại | Thông tin giữ nguyên, lấy lại file đúng nội dung |
| AC-03 | Xóa hoặc di chuyển file nguồn sau khi lưu | File đã nhập trong ứng dụng vẫn sử dụng được |
| AC-04 | Tìm `quyet dinh` hoặc `don vi`, kết hợp loại và khoảng ngày | Đối chiếu đúng tiếng Việt có dấu, gồm cả Đ/đ; kết quả thỏa tất cả bộ lọc |
| AC-05 | Nhập ngày không hợp lệ hoặc gặp lỗi sao chép file | Không báo lưu thành công; chỉ rõ lỗi; giữ dữ liệu người dùng đang nhập |
| AC-06 | Hai văn bản cùng số nhưng khác cơ quan/năm; hai file cùng tên | Không ghi đè lẫn nhau; trường hợp nghi trùng có cảnh báo |
| AC-07 | Xóa vào thùng rác rồi khôi phục | Hồ sơ và file được khôi phục đầy đủ; danh sách thường ẩn hồ sơ đã xóa |
| AC-08 | Sao lưu rồi phục hồi vào kho trống ở vị trí khác | Đủ danh mục, số hồ sơ, trạng thái thùng rác và file; kiểm tra file bằng checksum |
| AC-09 | Dùng gói sao lưu hỏng hoặc thiếu file để khôi phục | Báo lỗi trước khi thay kho đang dùng; dữ liệu hiện tại còn nguyên |
| AC-10 | Xóa dữ liệu trình duyệt, hoặc nâng cấp ứng dụng | Kho văn bản vẫn tồn tại và truy cập được |
| AC-11 | Chạy bài đo hiệu năng với bộ dữ liệu/máy tham chiếu đã chốt | Đạt mục tiêu tìm/lọc đã thống nhất |

## 10. Những quyết định cần chốt trước triển khai

Đã xác nhận: phân loại theo loại văn bản; tìm trong thông tin đã nhập; quy mô dưới 10.000 văn bản.

Còn cần xác nhận phiên bản Windows thực tế; chấp nhận giao diện trong trình duyệt hay cần cửa sổ riêng; nhu cầu nhập dữ liệu cũ; các trường bắt buộc; mẫu file lớn nhất. Các quyết định này dùng để hoàn thiện phạm vi và ước lượng, chưa cần mở rộng thành hệ thống quản lý văn bản nhiều người dùng.

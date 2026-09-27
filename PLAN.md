### What we're doing

Làm ứng dụng cá nhân để em bạn lưu văn bản kèm nhiều tệp, tìm theo tên và lấy lại đúng tệp. Ứng dụng chạy hoàn toàn offline trên Windows 11, bấm biểu tượng để mở trong trình duyệt, có sao lưu và khôi phục. Mọi trường thông tin, kể cả tên văn bản, đều tùy chọn; phạm vi đã xác nhận này thay cho các đề xuất rộng hơn trong `docs/requirements.md`.

### Steps

1. [x] Dựng ứng dụng cục bộ với danh sách và biểu mẫu tiếng Việt; chỉ truy cập từ chính máy, dùng tài nguyên có sẵn để chạy offline.
2. [x] Lưu và sửa tên, số, loại, ngày, cơ quan, trích yếu trong kho riêng trên máy; cho phép để trống tất cả, hiển thị “Chưa đặt tên” khi thiếu tên; đóng mở lại vẫn giữ dữ liệu.
3. [x] Cho đính kèm nhiều PDF, Word, Excel hoặc ảnh; sao chép vào kho, tránh ghi đè file trùng tên, chỉ báo thành công khi lưu đủ; cho lấy bản sao để mở bằng phần mềm trên Windows.
4. [x] Tìm từ khóa trong tên văn bản đã nhập, không phân biệt hoa thường và dấu tiếng Việt, gồm Đ/đ; kết quả cho xem hồ sơ và lấy tệp, tìm rỗng hiện danh sách.
5. [x] Tạo gói sao lưu nhất quán gồm toàn bộ thông tin, tệp và phiên bản dữ liệu; người dùng chọn nơi lưu, kể cả USB hoặc ổ ngoài.
6. [x] Khôi phục bằng thay toàn bộ kho sau khi kiểm tra gói và sao lưu kho hiện tại; gói hỏng, thiếu tệp hoặc khôi phục thất bại phải giữ được dữ liệu cũ.
7. [ ] Đóng gói đầy đủ cho Windows 11, bấm biểu tượng để chạy và mở trình duyệt; tránh chạy trùng, có cách thoát rõ ràng; thử lần chạy đầu khi ngắt mạng. Đã kiểm tra bản đóng gói trên Mac; còn đóng gói và thử trên Windows 11.

### What we're NOT doing

- OCR, tìm chữ trong tệp, nhập/xuất danh sách Excel, xem trước hoặc sửa nội dung tệp trong ứng dụng.
- Tài khoản, nhiều người dùng, truy cập qua mạng, đồng bộ cloud hoặc cửa sổ desktop riêng.
- Xóa văn bản/thùng rác, bộ lọc nâng cao, màn hình quản lý danh mục riêng, lịch sử phiên bản và sao lưu tự động.

### How we'll know it works

1. Trên Windows 11 đã ngắt mạng trước lần chạy đầu: bấm biểu tượng, lưu được hồ sơ với các trường trống và hồ sơ có nhiều tệp; đóng mở lại vẫn còn, di chuyển file nguồn vẫn lấy được bản đã lưu.
2. Với hồ sơ thật: `nghi dinh` tìm thấy tên chứa “Nghị định”, `don vi` tìm thấy “Đơn vị”; mở đúng tệp từ kết quả, kể cả khi các tệp trùng tên.
3. Sao lưu rồi phục hồi vào kho trống cho đủ hồ sơ và tệp có nội dung nguyên vẹn; thử gói hỏng hoặc thiếu tệp thì bị từ chối và kho đang dùng không thay đổi.

# Kho văn bản cá nhân

Ứng dụng lưu văn bản và tệp đính kèm trên chính máy đang chạy. Giao diện mở trong trình duyệt; không cần Internet khi sử dụng.

## Thử trên Mac

Nếu có tệp `dist/KhoVanBanMac`, chạy tệp đó để thử ngay. Nếu chạy từ mã nguồn, máy cần Python 3.12: trong thư mục dự án, tạo môi trường và cài thư viện bằng `python3 -m venv .venv` rồi `.venv/bin/python -m pip install -r requirements.txt`; sau đó chạy `.venv/bin/python launcher.py`. Trình duyệt sẽ mở ứng dụng. Dùng nút **Thoát** trong giao diện để đóng ứng dụng. Dữ liệu thử nằm trong `~/Library/Application Support/KhoVanBan`.

## Tạo bản chạy cho Windows 11

Trên máy Windows có Python 3.12, mở PowerShell tại thư mục dự án và chạy `./build_windows.ps1`. Tệp chạy nằm ở `dist/KhoVanBan.exe`. Có thể sao chép tệp này sang máy Windows 11 khác; người dùng không cần cài Python để chạy. Dữ liệu được giữ trong `%LOCALAPPDATA%\KhoVanBan`, tách khỏi tệp chạy.

Trước khi giao cho người dùng, ngắt mạng trên Windows 11 và thử: chạy lần đầu, thêm văn bản kèm nhiều tệp, tìm tên bằng tiếng Việt không dấu, sao lưu, khôi phục và mở lại tệp. Có thể sao lưu vào USB bằng cách nhập đường dẫn thư mục USB trên trang **Sao lưu**.

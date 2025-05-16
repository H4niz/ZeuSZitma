# ZeuS/Zitmo Malware Research & Education

Repository mô phỏng phần mềm độc hại ZeuS và Zitmo phục vụ mục đích nghiên cứu và giáo dục.

## Cấu trúc thư mục

```
ZeuSZitma/
├── server/                     # Máy chủ C&C (Command & Control)
│   ├── zitmo_c2_server_improved.py    # Server cải tiến với giao diện quản trị
│   └── zitmo_c2_server_original.py    # Server gốc
├── EduZitmo/                   # Mã nguồn Android client
│   ├── AndroidManifest.xml     # Cấu hình ứng dụng Android
│   ├── ZitmoAndroidClient.java # Mã nguồn chính
│   ├── activity_main.xml       # Layout giao diện
│   ├── ic_secure.xml          # Icon ứng dụng
│   ├── strings.xml            # Chuỗi ngôn ngữ
│   ├── build_steps.md         # Hướng dẫn build APK
│   ├── src/                   # Mã nguồn đã tổ chức
│   └── README.md              # Hướng dẫn sử dụng client
├── docs/                      # Tài liệu
│   ├── server_client_guide.md # Hướng dẫn sử dụng hệ thống
│   └── zitmo_client_configuration.md # Cấu hình client
├── BRD.md                     # Phân tích kỹ thuật ZeuS/Zitmo
├── CLAUDE.md                  # Hướng dẫn cho AI
├── LICENSE                    # Giấy phép MIT
└── README.md                  # File này
```

## Tính năng chính

### Server C&C (zitmo_c2_server_improved.py)
- Giao diện quản trị web trực quan
- Quản lý thiết bị bị nhiễm
- Thu thập SMS bị chặn (đặc biệt mã OTP/mTAN)
- Gửi lệnh điều khiển từ xa
- Theo dõi lịch sử thực thi lệnh
- Tự động phát hiện mã xác thực

### Android Client (EduZitmo)
- Giả mạo ứng dụng bảo mật ngân hàng
- Chặn và chuyển tiếp SMS
- Thực thi lệnh từ xa (đọc danh bạ, gửi SMS, v.v.)
- Duy trì kết nối với server C&C
- Tự khởi động và duy trì hoạt động

## Cài đặt và sử dụng

### 1. Khởi động Server C&C
```bash
cd server
python zitmo_c2_server_improved.py
```
Truy cập bảng điều khiển tại: http://localhost:5000/admin

### 2. Build Android Client
Xem hướng dẫn chi tiết trong `EduZitmo/build_steps.md`

### 3. Cấu hình kết nối
Cập nhật IP server trong client trước khi build:
```java
private static final String SERVER_URL_DEFAULT = "http://YOUR_SERVER_IP:5000";
```

## API Endpoints

| Endpoint | Method | Mô tả |
|----------|---------|-------|
| `/register` | POST | Đăng ký thiết bị mới |
| `/intercepted_sms` | POST | Gửi SMS bị chặn |
| `/ping` | POST | Ping và nhận lệnh mới |
| `/command_executed` | POST | Báo cáo kết quả thực thi |
| `/admin` | GET | Giao diện quản trị web |

## Lưu ý quan trọng

⚠️ **CẢNH BÁO**: Mã nguồn này **CHỈ** phục vụ mục đích nghiên cứu và giáo dục.

- KHÔNG sử dụng với mục đích độc hại hoặc bất hợp pháp
- KHÔNG cài đặt trên thiết bị không thuộc sở hữu của bạn
- Tuân thủ luật pháp và quy định về an ninh mạng
- Xóa ngay sau khi hoàn thành mục đích nghiên cứu

## Tài liệu tham khảo

- [Phân tích kỹ thuật ZeuS/Zitmo](BRD.md)
- [Hướng dẫn sử dụng hệ thống](docs/server_client_guide.md)
- [Cấu hình client](docs/zitmo_client_configuration.md)

## Giấy phép

MIT License - Xem file [LICENSE](LICENSE) để biết chi tiết.

## Thực hiện

- Nguyễn Lê Quốc Anh - haniz.cons@gmail.com
- Tô Duy Hinh

## Đóng góp

Vui lòng tạo issue hoặc pull request nếu bạn muốn đóng góp vào dự án.
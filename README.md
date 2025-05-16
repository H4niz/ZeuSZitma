# ZeuS/Zitmo Malware Research & Education

Repository mô phỏng phần mềm độc hại ZeuS và Zitmo phục vụ mục đích nghiên cứu và giáo dục.

## 🎯 Mục tiêu dự án

Dự án này cung cấp mô phỏng hoạt động của malware Zeus/Zitmo cho mục đích:
- Nghiên cứu kỹ thuật tấn công ngân hàng di động
- Giáo dục về bảo mật và phòng chống malware
- Thực hành phân tích mã độc trong môi trường an toàn
- Hiểu biết về cách thức hoạt động của banking trojans

## 🏗️ Cấu trúc dự án

```
ZeuSZitma/
├── server/                     # Máy chủ C&C (Command & Control)
│   ├── zitmo_c2_server.py     # Server với giao diện quản trị
│   └── README.md              # Tài liệu server
├── EduZitmo/                  # Mã nguồn Android client
│   ├── AndroidManifest.xml    # Cấu hình ứng dụng Android
│   ├── ZitmoAndroidClient.java # Mã nguồn chính
│   ├── activity_main.xml      # Layout giao diện
│   ├── ic_secure.xml         # Icon ứng dụng
│   ├── strings.xml           # Chuỗi ngôn ngữ
│   ├── build_steps.md        # Hướng dẫn build APK
│   ├── src/                  # Mã nguồn đã tổ chức
│   └── README.md             # Hướng dẫn sử dụng client
├── docs/                     # Tài liệu chi tiết
│   ├── architecture.md       # Kiến trúc hệ thống
│   ├── api_reference.md      # Tham khảo API
│   ├── security_analysis.md  # Phân tích bảo mật
│   ├── deployment_guide.md   # Hướng dẫn triển khai
│   └── troubleshooting.md    # Xử lý sự cố
├── BRD.md                    # Phân tích kỹ thuật ZeuS/Zitmo
├── CLAUDE.md                 # Hướng dẫn cho AI
├── LICENSE                   # Giấy phép MIT
└── README.md                 # File này
```

## 🚀 Tính năng chính

### Server C&C (Command & Control)
- **Giao diện quản trị web** - Dashboard trực quan, dễ sử dụng
- **Quản lý thiết bị** - Theo dõi trạng thái online/offline real-time
- **Thu thập SMS** - Tự động phát hiện và highlight mã OTP/mTAN
- **Điều khiển từ xa** - 5 loại lệnh cơ bản với giao diện trực quan
- **Lịch sử hoạt động** - Theo dõi toàn bộ hoạt động của hệ thống
- **Auto-refresh** - Cập nhật dữ liệu mỗi 30 giây

### Android Client (EduZitmo)
- **Giao diện giả mạo** - Làm giả ứng dụng bảo mật ngân hàng
- **Chặn SMS** - Lọc và chuyển tiếp SMS chứa mã xác thực
- **Thực thi lệnh** - Nhận và thực hiện lệnh từ server
- **Duy trì kết nối** - Ping định kỳ mỗi 15 phút
- **Khởi động tự động** - Tự khởi động khi thiết bị boot
- **Foreground Service** - Đảm bảo hoạt động liên tục

## 📋 Yêu cầu hệ thống

### Server
- Python 3.6+
- Flask framework
- SQLite3
- Kết nối mạng ổn định

### Client
- Android 5.0 (API 21) trở lên
- Android Studio để build
- JDK 8+
- Quyền cần thiết: SMS, Contacts, Internet

## 🔧 Cài đặt nhanh

### 1. Khởi động Server
```bash
cd server
pip install flask
python zitmo_c2_server.py
```
Truy cập: http://localhost:5000/admin

### 2. Build Android Client
```bash
cd EduZitmo
# Mở project trong Android Studio
# Cập nhật SERVER_URL_DEFAULT trong ZitmoUtils.java
# Build > Build APK
```

### 3. Cấu hình kết nối
Trong file `ZitmoUtils.java`:
```java
private static final String SERVER_URL_DEFAULT = "http://YOUR_SERVER_IP:5000";
```

## 📡 API Reference

### Client APIs
| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/register` | POST | Đăng ký thiết bị mới |
| `/intercepted_sms` | POST | Gửi SMS bị chặn |
| `/ping` | POST | Ping và nhận lệnh mới |
| `/command_executed` | POST | Báo cáo kết quả thực thi |

### Admin APIs
| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/admin` | GET | Giao diện quản trị web |
| `/admin/devices` | GET | Lấy danh sách thiết bị |
| `/admin/intercepted_sms` | GET | Lấy SMS đã chặn |
| `/admin/add_command` | POST | Thêm lệnh mới |

## 🛡️ Bảo mật & Pháp lý

### ⚠️ CẢNH BÁO QUAN TRỌNG
Mã nguồn này **CHỈ** dành cho mục đích nghiên cứu và giáo dục:

- **KHÔNG** sử dụng với mục đích độc hại hoặc bất hợp pháp
- **KHÔNG** cài đặt trên thiết bị không thuộc sở hữu của bạn
- **KHÔNG** triển khai trên môi trường production
- **TUÂN THỦ** luật pháp và quy định về an ninh mạng

### Khuyến nghị bảo mật
1. Chỉ chạy trong môi trường lab cô lập
2. Sử dụng firewall để giới hạn truy cập
3. Không expose server ra internet công cộng
4. Xóa toàn bộ sau khi hoàn thành nghiên cứu

## 📚 Tài liệu chi tiết

- [Kiến trúc hệ thống](docs/architecture.md)
- [Tham khảo API](docs/api_reference.md)
- [Phân tích bảo mật](docs/security_analysis.md)
- [Hướng dẫn triển khai](docs/deployment_guide.md)
- [Xử lý sự cố](docs/troubleshooting.md)
- [Phân tích kỹ thuật ZeuS/Zitmo](BRD.md)

## 📈 Roadmap

- [ ] Thêm mã hóa end-to-end
- [ ] Hỗ trợ nhiều ngôn ngữ
- [ ] Cải thiện UI/UX admin panel
- [ ] Thêm tính năng export dữ liệu
- [ ] Docker container hóa

## 👥 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng:
1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 Giấy phép

Dự án này được phát hành dưới giấy phép MIT. Xem file [LICENSE](LICENSE) để biết chi tiết.

## 👨‍💻 Tác giả

- **Nguyễn Lê Quốc Anh** - haniz.cons@gmail.com
- **Tô Duy Hinh**

## 🙏 Lời cảm ơn

- Cộng đồng nghiên cứu bảo mật
- Các nhà phát triển đã đóng góp
- Tài liệu tham khảo từ các nguồn mở
- Đặc biệt, ChatGPT, Claude, Grok, Gemini

## 📞 Liên hệ

Nếu có câu hỏi hoặc cần hỗ trợ:
- Email: haniz.cons@gmail.com
- Issues: [GitHub Issues](https://github.com/yourusername/ZeuSZitma/issues)

---

⚡ **Lưu ý**: Repository này chỉ phục vụ mục đích giáo dục. Người sử dụng hoàn toàn chịu trách nhiệm về việc sử dụng mã nguồn.
# EduZitmo - Mã nguồn mô phỏng Android Zitmo cho mục đích giáo dục

Thư mục này chứa mã nguồn mô phỏng Zitmo (Zeus-in-the-Mobile) cho nền tảng Android. Mã nguồn này **CHỈ** được tạo ra với mục đích giáo dục và nghiên cứu để hiểu cách thức hoạt động của phần mềm độc hại trên thiết bị di động.

## Nội dung thư mục

- `ZitmoAndroidClient.java` - Mã nguồn Java chính của client
- `AndroidManifest.xml` - File khai báo cấu hình ứng dụng
- `activity_main.xml` - Layout cho giao diện chính
- `ic_secure.xml` - Icon bảo mật sử dụng trong ứng dụng
- `zitmo_client_configuration.md` - Hướng dẫn cấu hình kết nối với máy chủ C&C
- `server_client_guide.md` - Hướng dẫn sử dụng hệ thống C&C server và client
- `build_steps.md` - Các bước xây dựng APK từ mã nguồn

## Tính năng mô phỏng

Client Zitmo này mô phỏng các tính năng chính của phần mềm độc hại ngân hàng di động:

1. Giả mạo ứng dụng bảo mật ngân hàng hợp pháp
2. Yêu cầu và sử dụng các quyền nguy hiểm
3. Chặn tin nhắn SMS chứa mã OTP/mTAN
4. Gửi dữ liệu đánh cắp về máy chủ C&C
5. Thực thi lệnh từ xa (đọc danh bạ, đọc/gửi SMS)
6. Duy trì hoạt động bền bỉ và tự khởi động khi thiết bị khởi động

## Các thành phần quan trọng

1. **MainActivity**: Giao diện người dùng và xin quyền
2. **SMSReceiver**: Thành phần chặn tin nhắn SMS
3. **ZitmoService**: Dịch vụ nền chính xử lý kết nối với máy chủ C&C
4. **BootReceiver**: Thành phần tự khởi động khi thiết bị khởi động
5. **ZitmoUtils**: Các tiện ích hỗ trợ

## Kết nối với máy chủ C&C

Client được thiết kế để giao tiếp với máy chủ qua các endpoints:
- `/register`: Đăng ký thiết bị
- `/intercepted_sms`: Gửi SMS bị chặn
- `/ping`: Ping và nhận lệnh mới
- `/command_executed`: Báo cáo thực thi lệnh

## Cách xây dựng và sử dụng

Xem chi tiết trong file `build_steps.md` để biết cách xây dựng APK từ mã nguồn này.

## Lưu ý quan trọng

- **Mục đích giáo dục**: Mã nguồn này CHỈ được cung cấp để phục vụ nghiên cứu, giáo dục và nâng cao hiểu biết về bảo mật di động.
- **Sử dụng có trách nhiệm**: KHÔNG sử dụng mã nguồn này với mục đích độc hại hoặc bất hợp pháp.
- **Chỉ sử dụng trên thiết bị của bạn**: Chỉ cài đặt và sử dụng trên thiết bị bạn sở hữu hoặc được phép sử dụng.

Việc sử dụng mã nguồn này với mục đích độc hại là vi phạm pháp luật và điều khoản sử dụng.
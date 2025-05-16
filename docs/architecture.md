# Kiến trúc hệ thống Zitmo

## Tổng quan

Hệ thống Zitmo được thiết kế theo mô hình client-server với kiến trúc phân tán, mô phỏng cách hoạt động của malware banking thực tế. Hệ thống bao gồm hai thành phần chính:

1. **Server C&C (Command & Control)** - Máy chủ điều khiển trung tâm
2. **Android Client** - Ứng dụng độc hại trên thiết bị di động

## Sơ đồ kiến trúc

```
┌─────────────────┐           ┌──────────────────┐
│  Admin Panel    │           │  Android Client  │
│   (Web UI)      │           │    (EduZitmo)    │
└────────┬────────┘           └────────┬─────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐  HTTP/JSON  ┌──────────────────┐
│  C&C Server     ├────────────►│  API Gateway     │
│  (Flask App)    │◄────────────┤  (RESTful)       │
└────────┬────────┘             └──────────────────┘
         │                              ▲
         ▼                              │
┌─────────────────┐                     │
│  Database       │                     │
│  (SQLite)       │                     │
└─────────────────┘                     │
                               ┌────────┴─────────┐
                               │  SMS Interceptor │
                               │  Service         │
                               └──────────────────┘
```

## 1. Server C&C

### Công nghệ sử dụng
- **Framework**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **API**: RESTful JSON

### Thành phần chính

#### 1.1 Web Application
```python
app = Flask(__name__)
```
- Xử lý HTTP requests
- Routing cho API endpoints
- Render giao diện admin

#### 1.2 Database Layer
```python
DB_PATH = 'zitmo_data.db'
```
- 3 bảng chính: devices, intercepted_sms, commands
- Quan hệ foreign key
- Transaction management

#### 1.3 Admin Interface
```html
ADMIN_TEMPLATE = '''...'''
```
- Single-page application
- 4 tab chức năng
- Auto-refresh mechanism

#### 1.4 API Endpoints

**Client APIs:**
- `/register` - Đăng ký thiết bị
- `/intercepted_sms` - Nhận SMS
- `/ping` - Heartbeat & lệnh mới
- `/command_executed` - Kết quả lệnh

**Admin APIs:**
- `/admin/devices` - Quản lý thiết bị
- `/admin/intercepted_sms` - Xem SMS
- `/admin/add_command` - Gửi lệnh
- `/admin/command_history` - Lịch sử

### Luồng xử lý

1. **Device Registration**
```
Client → POST /register → Server → Database → Response
```

2. **SMS Interception**
```
SMS → Client → POST /intercepted_sms → Server → Database
```

3. **Command Execution**
```
Admin → Add Command → Database
Client → POST /ping → Get Commands
Client → Execute → POST /command_executed
```

## 2. Android Client

### Công nghệ sử dụng
- **Language**: Java
- **Min SDK**: API 21 (Android 5.0)
- **Architecture**: Service-based

### Thành phần chính

#### 2.1 MainActivity
```java
public class MainActivity extends AppCompatActivity
```
- UI giả mạo ngân hàng
- Xin quyền hệ thống
- Khởi động services

#### 2.2 ZitmoService
```java
class ZitmoService extends Service
```
- Service chính chạy background
- Quản lý kết nối C&C
- Thực thi lệnh từ xa

#### 2.3 SMSReceiver
```java
class SMSReceiver extends BroadcastReceiver
```
- Lắng nghe SMS đến
- Lọc mã OTP/mTAN
- Chuyển tiếp đến server

#### 2.4 BootReceiver
```java
class BootReceiver extends BroadcastReceiver
```
- Tự khởi động khi boot
- Đảm bảo persistence

### Cơ chế hoạt động

#### 2.5.1 Permission Model
```xml
<uses-permission android:name="android.permission.RECEIVE_SMS" />
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.SEND_SMS" />
```

#### 2.5.2 Service Lifecycle
```java
@Override
public int onStartCommand(Intent intent, int flags, int startId) {
    return START_STICKY;
}
```

#### 2.5.3 SMS Filtering
```java
private boolean containsSensitiveContent(String message) {
    // Kiểm tra keywords và patterns
}
```

## 3. Communication Protocol

### 3.1 Data Format
Tất cả communication sử dụng JSON over HTTP:

```json
{
    "device_id": "unique_identifier",
    "timestamp": "2023-12-01 10:30:00",
    "data": { ... }
}
```

### 3.2 Security Measures
- Device ID generation using UUID
- Timestamp validation
- JSON schema validation

### 3.3 Network Layer
```java
HttpURLConnection connection = (HttpURLConnection) url.openConnection();
connection.setRequestMethod("POST");
connection.setRequestProperty("Content-Type", "application/json");
```

## 4. Data Flow

### 4.1 Registration Flow
```
1. App Install → Generate UUID
2. Request Permissions
3. POST /register with device info
4. Server creates device record
5. Return pending commands
```

### 4.2 SMS Interception Flow
```
1. SMS Received → BroadcastReceiver
2. Check if contains OTP/mTAN
3. Extract sender & message
4. POST /intercepted_sms
5. Optional: Hide from inbox
```

### 4.3 Command Execution Flow
```
1. Client ping every 15 minutes
2. Server returns pending commands
3. Client executes commands
4. Report results back
5. Server marks as executed
```

## 5. Database Schema

### 5.1 Devices Table
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

### 5.2 Intercepted SMS Table
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

### 5.3 Commands Table
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

## 6. Scalability Considerations

### 6.1 Current Limitations
- SQLite for single-server deployment
- Synchronous HTTP requests
- No load balancing

### 6.2 Potential Improvements
- PostgreSQL/MySQL for production
- WebSocket for real-time communication
- Redis for caching
- Nginx as reverse proxy

## 7. Security Architecture

### 7.1 Client Security
- Foreground service for persistence
- WakeLock for continuous operation
- High priority SMS receiver

### 7.2 Server Security
- Input validation
- SQL injection prevention
- Rate limiting (not implemented)
- Authentication (not implemented)

### 7.3 Future Enhancements
- HTTPS encryption
- API key authentication
- Data encryption at rest
- Obfuscation techniques

## 8. Monitoring & Logging

### 8.1 Server Logging
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='zitmo_cnc.log'
)
```

### 8.2 Client Logging
```java
Log.d(TAG, "Device registered successfully");
```

### 8.3 Admin Dashboard
- Real-time device status
- SMS visualization
- Command history
- Auto-refresh every 30s

## 9. Educational Features

### 9.1 Code Documentation
- Extensive comments in Vietnamese
- Function documentation
- Architecture explanations

### 9.2 Security Warnings
- Clear disclaimers
- Educational purpose only
- Legal compliance reminders

### 9.3 Simplified Implementation
- No encryption (for readability)
- Basic authentication
- Clear code structure

## 10. Deployment Architecture

### 10.1 Development
```
Local Machine → Flask Dev Server → Android Emulator
```

### 10.2 Testing
```
VM/Container → Flask Production → Physical Device
```

### 10.3 Educational Lab
```
Isolated Network → Dedicated Server → Test Devices
```

## Kết luận

Kiến trúc này được thiết kế để:
1. Dễ hiểu cho mục đích giáo dục
2. Mô phỏng realistic malware behavior
3. An toàn cho môi trường lab
4. Có thể mở rộng cho nghiên cứu

**Lưu ý quan trọng**: Đây là kiến trúc đơn giản hóa cho mục đích giáo dục. Malware thực tế sẽ phức tạp hơn nhiều với các kỹ thuật ẩn mình, mã hóa, và anti-analysis.
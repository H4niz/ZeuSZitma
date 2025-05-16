# ZeuS Zitmo Technical Details

This document provides technical information about the ZeuS Zitmo simulation code for educational purposes.

## C&C Server Architecture

The Command & Control (C&C) server is built using Flask and SQLite. It simulates how real banking malware communicates with infected devices.

### Database Schema

The server uses three main tables:

1. **Devices Table**: Stores information about infected devices
    - `id`: Auto-incremented unique identifier
    - `device_id`: Unique device identifier
    - `device_info`: Device information (model, OS, etc.)
    - `phone_number`: Phone number of the device
    - `operator`: Mobile network operator
    - `first_seen`: Timestamp of first registration
    - `last_seen`: Timestamp of last communication

2. **Intercepted SMS Table**: Stores SMS messages intercepted from devices
    - `id`: Auto-incremented unique identifier
    - `device_id`: Device that intercepted the SMS
    - `sender`: Sender of the SMS
    - `message`: Content of the SMS
    - `timestamp`: When the SMS was received
    - `processed`: Flag indicating if the SMS has been processed

3. **Commands Table**: Stores commands sent to devices
    - `id`: Auto-incremented unique identifier
    - `device_id`: Target device
    - `command_type`: Type of command
    - `command_data`: Additional command data (JSON)
    - `timestamp`: When the command was issued
    - `executed`: Flag indicating if the command has been executed
    - `result`: Result of command execution

### Communication Protocol

The server communicates with clients using JSON over HTTP/HTTPS:

#### Device Registration
- **Endpoint**: `/register`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "device_id": "unique_device_identifier",
    "device_info": "device information",
    "phone_number": "device phone number",
    "operator": "mobile network operator"
  }
  ```
- **Response**:
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

#### Intercepted SMS
- **Endpoint**: `/intercepted_sms`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "device_id": "unique_device_identifier",
    "sender": "SMS sender",
    "message": "SMS content",
    "timestamp": "YYYY-MM-DD HH:MM:SS"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success"
  }
  ```

#### Device Ping
- **Endpoint**: `/ping`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "device_id": "unique_device_identifier"
  }
  ```
- **Response**:
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

#### Command Execution Report
- **Endpoint**: `/command_executed`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "device_id": "unique_device_identifier",
    "command_id": command_id,
    "result": "execution result"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success"
  }
  ```

## Android Client Architecture

The Android client simulates a banking trojan that masquerades as a security app.

### Key Components

1. **MainActivity**: User interface that requests necessary permissions
2. **SMSReceiver**: Intercepts SMS messages, particularly targeting OTP/mTAN codes
3. **ZitmoService**: Background service that maintains communication with the C&C server
4. **BootReceiver**: Starts the service when the device boots
5. **ZitmoUtils**: Utility functions for device identification and configuration

### Capabilities

The Android client demonstrates several typical banking malware capabilities:

1. **SMS Interception**: Capturing SMS messages containing OTPs and mTANs
2. **Contact Theft**: Extracting contact information from the device
3. **SMS Reading**: Accessing stored SMS messages
4. **Command Execution**: Executing commands received from the C&C server
5. **Persistence**: Maintaining operation after device reboots
6. **Stealth**: Masquerading as a legitimate banking security app

### Supported Commands

The client can execute several types of commands:

1. `get_contacts`: Retrieves contacts from the device
2. `get_sms`: Retrieves SMS messages
3. `send_sms`: Sends SMS messages from the infected device
4. `update`: Simulates updating the malware
5. `uninstall`: Simulates self-removal

### SMS mTAN Detection

The client uses keyword matching and regular expressions to identify potential mTANs in SMS messages:

1. Checks for banking and authentication keywords
2. Scans for numeric patterns that match standard OTP formats (4-8 digits)
3. Prioritizes messages from banking institution numbers

## Security Features in Real Malware (Not Implemented)

For educational purposes, the following features of real malware are discussed but not implemented:

1. **Encryption**: Real malware encrypts communications with C&C servers
2. **Anti-detection**: Techniques to avoid detection by antivirus software
3. **Anti-emulation**: Methods to detect if running in an emulator or sandbox
4. **Data exfiltration**: Stealing credentials and financial information
5. **Self-protection**: Preventing uninstallation or disabling by the user
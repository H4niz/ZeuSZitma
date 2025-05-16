# ZeuS Zitmo Setup Guide

This document provides instructions for setting up and running the educational simulation of ZeuS/Zitmo banking malware.

## Overview

The repository contains two main components:

1. **C&C Server**: A Python-based server that simulates the command and control infrastructure
2. **Android Client**: Java code that demonstrates how Zitmo would operate on Android devices

## Requirements

### Server Requirements
- Python 3.6+
- Flask
- SQLite3

### Android Client Requirements
- Android Studio
- Android SDK (min API level 21)
- Java Development Kit (JDK) 8+

## Server Setup

1. Install dependencies:
```
pip install flask
```

2. Navigate to the server directory:
```
cd server
```

3. Run the server:
```
python zitmo_c2_server.py
```

The server will start on port 5000. Access the admin dashboard at:
```
http://localhost:5000/admin
```

## Android Client Setup

For educational purposes, the repository includes the Android client source code. The client can be built in Android Studio.

1. Import the EduZitmo directory into Android Studio
2. Configure the server address in the client code (`ZitmoUtils.java` - `SERVER_URL_DEFAULT` variable)
3. Build the APK using Android Studio

## Security Considerations

This simulation is for educational purposes only. When running the code:

1. Always use an isolated network environment
2. Never deploy to internet-facing servers
3. Only install the client on test devices that you own
4. Never use the code to intercept actual banking or sensitive information

## Server API Endpoints

The C&C server exposes several API endpoints:

- `/register` - Register a new device
- `/intercepted_sms` - Receive intercepted SMS
- `/ping` - Receive pings from devices and send pending commands
- `/command_executed` - Process command execution reports
- `/admin/add_command` - Add a new command for a device
- `/admin/devices` - Get a list of registered devices
- `/admin/intercepted_sms` - Get a list of intercepted SMS messages
- `/admin/commands` - Get a list of commands (history)

## Directory Structure

```
ZeuSZitma/
├── README.md - Project overview
├── LICENSE - License information
├── BRD.md - Technical analysis of ZeuS and Zitmo
├── docs/ - Documentation files
│   ├── setup_guide.md - Setup instructions
│   └── technical_details.md - Technical documentation
├── server/ - C&C server implementation
│   ├── zitmo_c2_server.py - Main server code
│   ├── data/ - Database directory
│   └── templates/ - Web interface templates
└── EduZitmo/ - Android client code
    ├── README.md - Client information
    ├── ZitmoAndroidClient.java - Main client code
    ├── AndroidManifest.xml - Android app configuration
    └── other resources - UI and configuration files
```
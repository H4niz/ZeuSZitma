# ZeuSZitma: Banking Malware Analysis & Simulation

<p align="center">
  <img src="https://raw.githubusercontent.com/anhnlq/ZeuSZitma/main/assets/zeus-zitmo-logo.png" alt="ZeuSZitma Logo" width="200"/>
  <br>
  <em>Educational Analysis of Banking Malware Infrastructure</em>
</p>

[![Research Paper](https://img.shields.io/badge/Research-IEEE-blue)](https://ieeexplore.ieee.org/document/7345443)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6+-yellow.svg)](https://www.python.org/)
[![Educational](https://img.shields.io/badge/Purpose-Educational-red.svg)](https://github.com/anhnlq/ZeuSZitma)

## ⚠️ Educational Purpose Only

This repository contains simulation code that demonstrates how banking malware like ZeuS and Zitmo operate. It is strictly for **educational and research purposes** to help understand cybersecurity threats. Using this code for malicious purposes is illegal and unethical.

## Overview

ZeuS and Zitmo (ZeuS-in-the-Mobile) are two prominent financial malware families that have posed significant threats to banking organizations. This repository analyzes their techniques and provides simulation code to illustrate their operation methods.

### ZeuS Malware

First discovered in 2007, ZeuS was a banking trojan targeting Windows systems to steal financial information. It was responsible for:

- 44% of financial malware infections
- ~90% of global banking fraud (2009-2010)
- Infected approximately 3.6 million computers in the US

### Zitmo Malware

Detected in September 2010, Zitmo is the mobile version of ZeuS targeting Android, Symbian, BlackBerry, and Windows Mobile platforms. Its primary goal was to steal mobile Transaction Authentication Numbers (mTANs) sent via SMS by banks.

## Technical Details

### ZeuS Techniques

- **Information Theft**:
  - Keystroke logging
  - Form grabbing
  - Man-in-the-browser attacks
  - Data exfiltration via IM and email

- **Evasion**:
  - Polymorphic and metamorphic encoding
  - Packer usage for code obfuscation

- **C&C Infrastructure**:
  - Initially centralized C&C servers
  - Later evolved to P2P network (GameoverZeuS)
  - Domain Generation Algorithms (DGA)

### Zitmo Techniques

- **Social Engineering**:
  - Fake SMS messages with malicious download links
  - Banking security app disguises

- **mTAN Theft**:
  - SMS interception based on sender or content patterns
  - Forwarding to C&C servers

## Repository Contents

- `zitmo-cnc-server.py`: Python simulation of a Zitmo Command & Control server
- `zitmo-reference-code.java`: Java code simulating how Zitmo operates on Android
- `BRD.md`: Detailed analysis of ZeuS and Zitmo techniques (in Vietnamese)

## Running the C&C Server Simulation

```bash
# Install dependencies
pip install flask

# Run the server
python zitmo-cnc-server.py
```

The server runs on port 5000. Access the admin dashboard at `http://localhost:5000/admin`.

## API Endpoints

The simulated C&C server implements these endpoints:

- `/register` - Register new devices or update existing ones
- `/intercepted_sms` - Receive intercepted SMS from devices
- `/ping` - Receive device pings and send pending commands
- `/command_executed` - Process command execution reports
- `/admin/add_command` - Add new commands for devices
- `/admin/devices` - Get list of registered devices
- `/admin/intercepted_sms` - Get list of intercepted SMS messages

## Authors

- Nguyễn Lê Quốc Anh - haniz.cons@gmail.com
- Tô Duy Hinh

## References

This analysis is based on the IEEE research paper "[From ZeuS to Zitmo: Trends in Banking Malware](https://ieeexplore.ieee.org/document/7345443)".

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
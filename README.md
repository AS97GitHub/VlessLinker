# VlessLinker

A simple Python tool for converting between **VLESS URLs**, **VPN URLs**, and **JSON configurations** for Xray-core.

## Features

- **VLESS URL ↔ JSON**: Convert VLESS links to Xray config and back
- **VPN URL decoding**: Convert AmneziaVPN links to VLESS or JSON format
- **Reality protocol support**: Full support for all Reality parameters
- **Cross-platform**: Works on Windows, Linux, and macOS
- **No dependencies**: Uses only Python standard library
- **Interactive interface**: Simple prompts guide you through conversion

## Installation

### Option 1: Windows Executable (Easiest)
Download the ready-to-use `vlesslinker.exe` file - no Python installation required!
Just download and run the .exe file directly.

### Option 2: Python Script (All Platforms)

### 1. Download the file
Download the `vlesslinker.py` file to your computer.

### 2. Install Python (if not installed)
- **Windows**: Download from [python.org](https://www.python.org/downloads/) and install
- **Linux/macOS**: Usually pre-installed

### 3. Make executable (Linux/macOS - Optional)
Only needed if you want to run the script as `./vlesslinker.py`:

```bash
chmod +x vlesslinker.py
```

## Usage

### Windows
Try one of these commands:

```cmd
python vlesslinker.py
```

or

```cmd
py vlesslinker.py
```

### Linux/macOS

```bash
python3 vlesslinker.py
```

**Alternative** (if you made it executable with `chmod +x`):

```bash
./vlesslinker.py
```

### What you can convert:

1. **VLESS URL** → Get complete Xray JSON config
2. **JSON config** → Get VLESS URL
3. **AmneziaVPN URL** → Choose to get VLESS URL or JSON config

### Exit the program:
- Type `exit`, `quit`, or `q`
- Press `Ctrl+C`

## Examples

### VLESS to JSON
**Input:**
```
vless://550e8400-e29b-41d4-a716-446655440000@example.com:443?security=reality&sni=www.google.com&fp=chrome&pbk=publickey123&sid=shortid&type=tcp
```

**Output:** Complete Xray configuration with SOCKS proxy on port 10808

### JSON to VLESS
**Input:** Xray JSON configuration (paste directly or provide file path)
**Output:** `vless://` URL ready to use

### AmneziaVPN URL conversion
**Input:** `vpn://base64data...`
**Output:** Choose between VLESS URL or JSON format

## Supported Parameters

| Parameter | URL Key | Description |
|-----------|---------|-------------|
| UUID | - | User identifier (in URL path) |
| Address | - | Server hostname/IP (in URL) |
| Port | - | Server port (in URL) |
| Flow | `flow` | Flow control (e.g., `xtls-rprx-vision`) |
| Security | `security` | Security protocol (`reality`, `tls`, `none`) |
| Network Type | `type` | Transport protocol (`tcp`, `ws`, `grpc`, etc.) |
| Server Name | `sni` | TLS/Reality server name indication |
| Fingerprint | `fp` | TLS fingerprint (`chrome`, `firefox`, etc.) |
| Public Key | `pbk` | Reality public key |
| Short ID | `sid` | Reality short identifier |
| SpiderX | `spx` | Reality SpiderX parameter |

## Requirements

- Python 3.6 or higher
- No additional packages needed

## Notes

- Creates SOCKS5 proxy on `127.0.0.1:10808` in generated configs
- AmneziaVPN URLs use base64 encoding (sometimes compressed)
- Program will ask for connection name when creating VLESS URLs
- JSON files with `.json` extension are auto-detected

## Troubleshooting

**Common errors:**
- "Base64 decode error" → AmneziaVPN URL is corrupted or incomplete
- "JSON decode error" → Invalid JSON format
- "File not found" → Check file path

**Tips:**
- VLESS URLs must start with `vless://`
- AmneziaVPN URLs must start with `vpn://`
- JSON can be pasted directly or loaded from file

## License

MIT License

## Disclaimer

This tool is for legitimate networking purposes only. Users are responsible for compliance with local laws and regulations.

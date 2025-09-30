#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import base64
import zlib
import os
from urllib.parse import urlparse, parse_qs

PROGRAM_NAME = "VlessLinker"
PROGRAM_VERSION = "1.0"
PROGRAM_DESC = "VLess ↔ Json Converter (with VPN:// support)"

def decode_vpn_url(vpn_url):
    """Decode vpn:// URL to JSON configuration"""
    if not vpn_url.startswith("vpn://"):
        raise ValueError("Invalid VPN URL format")
    
    # Extract and prepare base64 data
    encoded_data = vpn_url[6:].strip()  # Remove "vpn://" prefix
    
    # Add padding if needed
    missing_padding = len(encoded_data) % 4
    if missing_padding:
        encoded_data += '=' * (4 - missing_padding)
    
    try:
        # Decode base64
        raw_data = base64.urlsafe_b64decode(encoded_data)
    except Exception as e:
        raise ValueError(f"Base64 decode error: {e}")
    
    # Try zlib decompression first
    try:
        # First 4 bytes contain original data length
        if len(raw_data) >= 4:
            expected_length = int.from_bytes(raw_data[:4], 'big')
            decompressed = zlib.decompress(raw_data[4:])
            
            if len(decompressed) == expected_length:
                json_data = json.loads(decompressed.decode('utf-8'))
            else:
                raise ValueError("Length mismatch after decompression")
        else:
            raise ValueError("Data too short for zlib format")
            
    except (zlib.error, ValueError):
        # Fallback: try as plain JSON
        try:
            json_data = json.loads(raw_data.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"JSON decode error: {e}")
    
    # Extract nested configuration if present
    if isinstance(json_data, dict) and "containers" in json_data:
        containers = json_data["containers"]
        if isinstance(containers, list) and len(containers) > 0:
            container = containers[0]
            if isinstance(container, dict) and "xray" in container:
                xray_config = container["xray"]
                if isinstance(xray_config, dict) and "last_config" in xray_config:
                    return json.loads(xray_config["last_config"])
    
    return json_data

def from_vless_url(vless_url):
    parsed = urlparse(vless_url)
    uuid = parsed.username
    address = parsed.hostname
    port = int(parsed.port)

    params = parse_qs(parsed.query)

    network = params.get("type", ["tcp"])[0]
    security = params.get("security", ["none"])[0]
    public_key = params.get("pbk", [""])[0]
    server_name = params.get("sni", [""])[0]
    fingerprint = params.get("fp", [""])[0]
    short_id = params.get("sid", [""])[0]
    flow = params.get("flow", [""])[0]
    spiderx = params.get("spx", [""])[0]

    return {
        "inbounds": [
            {
                "listen": "127.0.0.1",
                "port": 10808,
                "protocol": "socks",
                "settings": {"udp": True}
            }
        ],
        "log": {"loglevel": "error"},
        "outbounds": [
            {
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": address,
                            "port": port,
                            "users": [
                                {
                                    "id": uuid,
                                    "encryption": "none",
                                    "flow": flow
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": network,
                    "security": security,
                    "realitySettings": {
                        "serverName": server_name,
                        "fingerprint": fingerprint,
                        "publicKey": public_key,
                        "shortId": short_id,
                        "spiderX": spiderx
                    }
                }
            }
        ]
    }

def get_vless_name(address):
    """Ask user for VLESS name or use server address as default"""
    try:
        name = input(f"Enter VLESS name (leave empty to use '{address}'): ").strip()
        return name if name else address
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Using server address as name.")
        return address

def to_vless_url(data):
    try:
        out = data["outbounds"][0]
        vnext = out["settings"]["vnext"][0]
        user = vnext["users"][0]
        stream = out["streamSettings"]

        uuid = user["id"]
        address = vnext["address"]
        port = vnext["port"]

        flow = user.get("flow", "")
        network = stream.get("network", "tcp")
        security = stream.get("security", "none")

        rs = stream.get("realitySettings", {})
        server_name = rs.get("serverName", "")
        fingerprint = rs.get("fingerprint", "")
        public_key = rs.get("publicKey", "")
        short_id = rs.get("shortId", "")
        spiderx = rs.get("spiderX", "")

        url = f"vless://{uuid}@{address}:{port}?encryption=none"
        if flow:
            url += f"&flow={flow}"
        if security:
            url += f"&security={security}"
        if server_name:
            url += f"&sni={server_name}"
        if fingerprint:
            url += f"&fp={fingerprint}"
        if public_key:
            url += f"&pbk={public_key}"
        if short_id:
            url += f"&sid={short_id}"
        if spiderx:
            url += f"&spx={spiderx}"
        if network:
            url += f"&type={network}"

        # Ask user for custom name
        custom_name = get_vless_name(address)
        url += f"#{custom_name}"
        return url

    except Exception as e:
        sys.exit(f"Error generating VLESS URL: {e}")

def main():
    """Main interactive loop"""
    print(f"{PROGRAM_NAME} v{PROGRAM_VERSION}")
    print(f"{PROGRAM_DESC}")
    print("=" * 60)
    
    while True:
        print("\nEnter 'exit' or 'quit' (or press Ctrl+C) to close the program.")
        try:
            src = input("Enter VLESS URL, VPN URL, JSON, or JSON file path: ").strip()
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye!")
            break
        
        # Check for exit commands
        if src.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        
        if not src:
            print("Empty input. Please try again.")
            continue

        try:
            if src.startswith("vless://"):
                # vless:// to json
                result = from_vless_url(src)
                print("\n" + "="*60 + "\n")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
            elif src.startswith("vpn://"):
                # Ask user what to do with vpn:// URL
                print("\nChoose conversion type:")
                print("1. vpn:// to vless://")
                print("2. vpn:// to json")
                
                while True:
                    try:
                        choice = input("Enter choice (1 or 2): ").strip()
                    except KeyboardInterrupt:
                        print("\n\nProgram interrupted by user. Goodbye!")
                        return
                    
                    if choice in ["1", "2"]:
                        break
                    print("Invalid choice. Please enter 1 or 2.")
                
                config = decode_vpn_url(src)
                print("\n" + "="*60 + "\n")
                
                if choice == "1":
                    # Convert to vless://
                    vless_url = to_vless_url(config)
                    print(vless_url)
                else:
                    # Convert to json
                    print(json.dumps(config, indent=2, ensure_ascii=False))
                    
            else:
                # json to vless:// (either inline JSON or file path)
                # Check if input is a file path
                if os.path.exists(src) and src.lower().endswith('.json'):
                    with open(src, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    # Try to parse as inline JSON
                    data = json.loads(src)
                
                print("\n" + "="*60 + "\n")
                print(to_vless_url(data))
                
        except ValueError as e:
            print(f"Error: {e}")
        except json.JSONDecodeError:
            print("Error: Input data is neither valid JSON, VLESS URL, nor VPN URL.")
        except FileNotFoundError:
            print(f"Error: File '{src}' not found.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--version", "-v"):
        print(f"{PROGRAM_NAME} v{PROGRAM_VERSION} - {PROGRAM_DESC}")
        sys.exit(0)
    
    main()

#!/usr/bin/env python3
"""Test network binding capabilities."""

import socket
import sys
import time

def log_to_file(message):
    """Simple file logging."""
    try:
        with open("/Applications/SpeedRay/.cursor/debug-853f04.log", "a") as f:
            timestamp = int(time.time() * 1000)
            f.write(f'{{"sessionId":"853f04","timestamp":{timestamp},"message":"network_test: {message}"}}\n')
    except Exception:
        pass

def test_port_binding(host, port):
    """Test if we can bind to a specific host:port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        
        print(f"✓ Successfully bound to {host}:{port}")
        log_to_file(f"Successfully bound to {host}:{port}")
        
        # Test if we can accept connections
        sock.settimeout(1.0)
        print(f"  Listening for connections on {host}:{port}...")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to bind to {host}:{port}: {e}")
        log_to_file(f"Failed to bind to {host}:{port}: {str(e)}")
        return False

def main():
    print("=== NETWORK BINDING TEST ===")
    log_to_file("Network binding test started")
    
    # Test different binding configurations
    test_configs = [
        ("127.0.0.1", 8000),
        ("0.0.0.0", 8000),
        ("127.0.0.1", 8001),
        ("0.0.0.0", 8001),
        ("127.0.0.1", 9000),  # Different port entirely
    ]
    
    successful_binds = 0
    for host, port in test_configs:
        if test_port_binding(host, port):
            successful_binds += 1
    
    print(f"\nSummary: {successful_binds}/{len(test_configs)} binding tests successful")
    log_to_file(f"Network test summary: {successful_binds}/{len(test_configs)} successful")
    
    if successful_binds == 0:
        print("WARNING: No ports can be bound - possible firewall/permission issue")
        log_to_file("WARNING: No ports can be bound - possible firewall/permission issue")
    
    # Check what's currently listening
    print("\n=== CHECKING CURRENT LISTENERS ===")
    import subprocess
    try:
        result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
        print("Current listening ports:")
        for line in result.stdout.split('\n'):
            if ':8000' in line or ':8001' in line:
                print(f"  {line}")
                log_to_file(f"Listening port found: {line}")
    except Exception as e:
        print(f"Could not check listening ports: {e}")
        log_to_file(f"Could not check listening ports: {str(e)}")

if __name__ == "__main__":
    main()
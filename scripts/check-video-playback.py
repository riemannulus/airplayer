#!/usr/bin/env python3
"""Verify direct hlsurl playback with Apple's public HLS fixture on a test receiver."""
import argparse
import socket
import plistlib
import subprocess
import time
import uuid

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--serial', required=True)
args = parser.parse_args()
adb = ['adb', '-s', args.serial]
port = 17001
session = str(uuid.uuid4())
subprocess.run(adb + ['forward', f'tcp:{port}', 'tcp:7000'], check=True, capture_output=True)

# Keep the sender control connection alive: UxPlay ends playback when it disconnects.
# AirPlay uses empty control responses without Content-Length, so parse their framing directly.
conn = socket.create_connection(('127.0.0.1', port), timeout=5)
reader = conn.makefile('rb')

def request(method, path, data=None):
    data = data or b''
    headers = (f'{method} {path} HTTP/1.1\r\nHost: localhost\r\n'
               f'Content-Type: application/x-apple-binary-plist\r\n'
               f'X-Apple-Session-ID: {session}\r\nContent-Length: {len(data)}\r\n\r\n')
    conn.sendall(headers.encode() + data)
    status = int(reader.readline().split()[1])
    length = 0
    while line := reader.readline():
        if line == b'\r\n':
            break
        key, value = line.split(b':', 1)
        if key.lower() == b'content-length':
            length = int(value)
    return status, reader.read(length)

try:
    body = plistlib.dumps({'uuid': str(uuid.uuid4()), 'clientProcName': 'SyntheticRegression',
                          'Content-Location': 'hlsurl://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_4x3/bipbop_4x3_variant.m3u8',
                          'Start-Position-Seconds': 0.0}, fmt=plistlib.FMT_BINARY)
    status, _ = request('POST', '/play', body)
    assert status == 200, f'play status={status}'
    for _ in range(45):
        time.sleep(1)
        status, body = request('GET', '/playback-info')
        if body:
            state = plistlib.loads(body)
            if state.get('readyToPlay') and state.get('rate', 0) > 0 and state.get('position', -1) >= 0:
                print('PASS synthetic hlsurl playback: ready, playing, position available')
                break
    else:
        raise AssertionError('No playing state within 45 seconds')
finally:
    try:
        request('POST', '/stop')
    finally:
        reader.close()
        conn.close()
        subprocess.run(adb + ['forward', '--remove', f'tcp:{port}'], capture_output=True)

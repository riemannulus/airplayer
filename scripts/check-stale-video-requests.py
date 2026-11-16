#!/usr/bin/env python3
"""Replay synthetic late video requests against a connected test Android device."""
import argparse
import http.client
import plistlib
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--serial', required=True)
parser.add_argument('--package', default='io.github.riemannulus.airplayer')
parser.add_argument('--port', type=int, default=17000)
args = parser.parse_args()
adb = ['adb', '-s', args.serial]

def shell(*cmd):
    return subprocess.run(adb + ['shell', *cmd], capture_output=True, text=True)

payload = plistlib.dumps({'type': 'playlistInsert'}, fmt=plistlib.FMT_BINARY)
failed = 0
subprocess.run(adb + ['forward', f'tcp:{args.port}', 'tcp:7000'], check=True, capture_output=True)
try:
    for method, path, expected_status in [('POST', '/action', 400), ('PUT', '/setProperty?selectedMediaArray', 400), ('GET', '/master.m3u8', 404)]:
        shell('am', 'force-stop', args.package)
        shell('am', 'start', '-n', f'{args.package}/io.github.seancheung.airplayer.MainActivity')
        # A cold app launch can take several seconds on a TV. Wait for its actual listener.
        for attempt in range(30):
            probe = http.client.HTTPConnection('127.0.0.1', args.port, timeout=1)
            try:
                probe.request('GET', '/server-info', headers={'X-Apple-Session-ID': 'synthetic-stale-session'})
                result = probe.getresponse()
                result.read()
                if result.status == 200:
                    break
            except (OSError, http.client.HTTPException):
                pass
            finally:
                probe.close()
            time.sleep(.5)
        else:
            raise RuntimeError('Receiver did not become ready after launch')
        conn = http.client.HTTPConnection('127.0.0.1', args.port, timeout=5)
        try:
            conn.request(method, path, body=payload if method in ('POST', 'PUT') else None,
                         headers={'Content-Type': 'application/x-apple-binary-plist',
                                  **({'X-Apple-Session-ID': 'synthetic-stale-session'} if method != 'GET' else {})})
            response = conn.getresponse()
            response.read()
            time.sleep(.5)
            alive = shell('pidof', args.package).returncode == 0
            assert response.status == expected_status and alive, f'status={response.status}, alive={alive}'
            print(f'PASS {method} {path}: {expected_status}, receiver survives')
        except (OSError, http.client.HTTPException, AssertionError) as error:
            failed += 1
            print(f'FAIL {method} {path}: {type(error).__name__}: {error}')
        finally:
            conn.close()
finally:
    subprocess.run(adb + ['forward', '--remove', f'tcp:{args.port}'], capture_output=True)
raise SystemExit(1 if failed else 0)

#!/usr/bin/env python3
"""
Test TX operations for Evil Crow RF V2
"""

import serial
import json
import time
import sys

def test_tx(port='/dev/ttyUSB0', baud=115200):
    print(f"🔌 Connecting to {port} @ {baud} baud...")

    try:
        ser = serial.Serial(port, baud, timeout=2)
        time.sleep(2)

        ser.reset_input_buffer()
        print("✅ Connected!")

        # Wait for ready event
        print("\n📡 Waiting for 'ready' event...")
        line = ser.readline().decode().strip()
        if line:
            print(f"← {line}")

        print("\n🧪 Testing TX operations...\n")

        # Test 1: Simple TX test with example timings
        print("📤 Test 1: Transmit simple signal (3 repeats)")
        print("   Example timings: 450us HIGH, 1200us LOW, repeated pattern")

        # Simple pattern: short-long-short-long (like a basic remote control)
        timings = [450, 1200, 450, 1200, 450, 1200, 450, 1200,
                   450, 450, 450, 450, 1200, 1200, 1200, 1200]

        cmd = {
            "cmd": "tx_send",
            "id": 1,
            "params": {
                "module": 1,
                "timings_us": timings,
                "repeat": 3
            }
        }

        ser.write((json.dumps(cmd) + '\n').encode())
        response = ser.readline().decode().strip()
        print(f"📥 Response: {response}")

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ TX completed!")
                print(f"   📻 Module: {data['data']['module']}")
                print(f"   🔢 Timings sent: {data['data']['count']}")
                print(f"   🔁 Repeats: {data['data']['repeat']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

        # Test 2: Check status
        print("📤 Test 2: Check status after TX")
        cmd = {"cmd": "get_status", "id": 2}
        ser.write((json.dumps(cmd) + '\n').encode())
        response = ser.readline().decode().strip()
        print(f"📥 Response: {response}")

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ Status OK")
                print(f"   🔵 TX Active: {data['data']['tx_active']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n✅ TX tests completed!")
        print("\n📝 Note: To test replay, first capture a real signal with test_rx.py,")
        print("   then use those timings in the tx_send command.")

        ser.close()

    except serial.SerialException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    test_tx(port)

#!/usr/bin/env python3
"""
Test Jammer operations for Evil Crow RF V2

WARNING: Use jammer only in authorized environments!
Jamming unauthorized frequencies is illegal in most countries.
"""

import serial
import json
import time
import sys

def test_jammer(port='/dev/ttyUSB0', baud=115200):
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

        print("\n⚠️  WARNING: Jamming Test")
        print("   Use only in authorized environments!")
        print("   Jamming unauthorized frequencies is illegal!\n")

        print("🧪 Testing Jammer operations...\n")

        # Test 1: Start Jammer
        print("📤 Test 1: Start Jammer (433.92 MHz, 10 dBm)")
        cmd = {
            "cmd": "jammer_start",
            "id": 1,
            "params": {
                "module": 1,
                "frequency_mhz": 433.92,
                "power_dbm": 10
            }
        }

        ser.write((json.dumps(cmd) + '\n').encode())
        response = ser.readline().decode().strip()
        print(f"📥 Response: {response}")

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ Jammer started!")
                print(f"   📻 Module: {data['data']['module']}")
                print(f"   📡 Frequency: {data['data']['frequency_mhz']} MHz")
                print(f"   ⚡ Power: {data['data']['power_dbm']} dBm")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()
        print("⏱️  Jammer active for 5 seconds...")
        print("   This will block 433.92 MHz communications in range")
        print()

        for i in range(5):
            time.sleep(1)
            print(f"   {5-i} seconds remaining...")

        # Test 2: Check status while jamming
        print("\n📤 Test 2: Check status while jamming")
        cmd = {"cmd": "get_status", "id": 2}
        ser.write((json.dumps(cmd) + '\n').encode())
        response = ser.readline().decode().strip()
        print(f"📥 Response: {response}")

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ Status OK")
                print(f"   ⚡ Jammer Active: {data['data']['jammer_active']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

        # Test 3: Stop Jammer
        print("📤 Test 3: Stop Jammer")
        cmd = {"cmd": "jammer_stop", "id": 3}
        ser.write((json.dumps(cmd) + '\n').encode())
        response = ser.readline().decode().strip()
        print(f"📥 Response: {response}")

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ Jammer stopped!")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n✅ Jammer tests completed!")
        print("\n⚠️  Legal Notice:")
        print("   - Use only in authorized testing environments")
        print("   - Jamming unauthorized frequencies is illegal")
        print("   - May interfere with emergency communications")
        print("   - Use responsibly!")

        ser.close()

    except serial.SerialException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'

    # Ask for confirmation
    print("\n⚠️  WARNING: You are about to test RF jamming!")
    print("This should ONLY be used in authorized testing environments.")
    print("Jamming unauthorized frequencies is ILLEGAL in most countries.\n")

    confirm = input("Type 'I UNDERSTAND' to continue: ")
    if confirm != 'I UNDERSTAND':
        print("Test cancelled.")
        sys.exit(0)

    test_jammer(port)

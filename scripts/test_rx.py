#!/usr/bin/env python3
"""
Test RX operations for Evil Crow RF V2
"""

import serial
import json
import time
import sys

def test_rx(port='/dev/ttyUSB0', baud=115200):
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

        print("\n🧪 Testing RX operations...\n")

        # Test 1: RX Config
        print("📤 Test 1: Configure RX (433.92 MHz, Module 1)")
        cmd = {
            "cmd": "rx_config",
            "id": 1,
            "params": {
                "module": 1,
                "frequency_mhz": 433.92
            }
        }
        ser.write((json.dumps(cmd) + '\n').encode())
        response = ser.readline().decode().strip()
        print(f"📥 Response: {response}")

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ RX configured!")
                print(f"   📻 Module: {data['data']['module']}")
                print(f"   📡 Frequency: {data['data']['frequency_mhz']} MHz")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

        # Test 2: Start RX
        print("📤 Test 2: Start RX")
        cmd = {"cmd": "rx_start", "id": 2}
        ser.write((json.dumps(cmd) + '\n').encode())
        response = ser.readline().decode().strip()
        print(f"📥 Response: {response}")

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ RX started!")
                print(f"   🎧 Listening for signals...")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()
        print("⏱️  RX active for 10 seconds...")
        print("📻 Press a 433.92 MHz remote control now!")
        print()

        # Wait and check for signal_received events
        for i in range(10):
            time.sleep(1)
            print(f"   {10-i} seconds remaining...")

            # Check for events
            while ser.in_waiting:
                line = ser.readline().decode().strip()
                if line:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'event' and data.get('event') == 'signal_received':
                            print(f"\n🎉 Signal received!")
                            print(f"   📊 Sample count: {data['data']['sample_count']}")
                            print(f"   🔢 Samples per symbol: {data['data']['samples_per_symbol']}us")
                            if 'raw_timings_us' in data['data']:
                                timings = data['data']['raw_timings_us']
                                print(f"   ⏱️  First timings: {timings[:10]}...")
                            if 'analysis' in data['data']:
                                print(f"   📝 Analysis: {data['data']['analysis'][:100]}...")
                    except:
                        pass

        # Test 3: Stop RX
        print("\n📤 Test 3: Stop RX")
        cmd = {"cmd": "rx_stop", "id": 3}
        ser.write((json.dumps(cmd) + '\n').encode())

        # Read response and possible signal_received event
        for _ in range(3):
            if ser.in_waiting:
                line = ser.readline().decode().strip()
                if line:
                    print(f"📥 {line}")
                    try:
                        data = json.loads(line)
                        if data.get('status') == 'ok':
                            print(f"   ✅ RX stopped!")
                        elif data.get('event') == 'signal_received':
                            print(f"   🎉 Final signal captured!")
                    except:
                        pass

        print("\n✅ RX tests completed!")
        ser.close()

    except serial.SerialException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    test_rx(port)

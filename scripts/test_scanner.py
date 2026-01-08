#!/usr/bin/env python3
"""
Test Scanner & Spectrum operations for Evil Crow RF V2
"""

import serial
import json
import time
import sys

def test_scanner(port='/dev/ttyUSB0', baud=115200):
    print(f"🔌 Connecting to {port} @ {baud} baud...")

    try:
        ser = serial.Serial(port, baud, timeout=10)  # Longer timeout for scanning
        time.sleep(2)

        ser.reset_input_buffer()
        print("✅ Connected!")

        # Wait for ready event
        print("\n📡 Waiting for 'ready' event...")
        line = ser.readline().decode().strip()
        if line:
            print(f"← {line}")

        print("\n🧪 Testing Scanner & Spectrum operations...\n")

        # Test 1: Frequency Scanner
        print("📤 Test 1: Frequency Scanner (433-434 MHz, 100 kHz steps)")
        cmd = {
            "cmd": "scan_start",
            "id": 1,
            "params": {
                "module": 1,
                "start_mhz": 433.0,
                "end_mhz": 434.0,
                "step_khz": 100.0,
                "threshold_dbm": -80
            }
        }

        ser.write((json.dumps(cmd) + '\n').encode())

        print("   ⏱️  Scanning... (this may take a moment)")
        response = ser.readline().decode().strip()
        print(f"📥 Response: {response[:200]}...")  # Truncate for readability

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ Scan completed!")
                print(f"   📻 Range: {data['data']['start_mhz']}-{data['data']['end_mhz']} MHz")
                print(f"   🔍 Step: {data['data']['step_khz']} kHz")
                print(f"   📊 Threshold: {data['data']['threshold_dbm']} dBm")
                print(f"   🎯 Signals found: {data['data']['results_count']}")

                if data['data']['results_count'] > 0:
                    print("\n   Detected Frequencies:")
                    for i in range(min(data['data']['results_count'], 5)):  # Show first 5
                        freq = data['data']['frequencies_mhz'][i]
                        rssi = data['data']['rssi_dbm'][i]
                        print(f"     • {freq:.2f} MHz at {rssi} dBm")

                    if data['data']['results_count'] > 5:
                        print(f"     ... and {data['data']['results_count'] - 5} more")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

        # Test 2: Spectrum Analyzer
        print("📤 Test 2: Spectrum Analyzer (433.92 MHz center, 5 MHz span, 25 points)")
        cmd = {
            "cmd": "get_spectrum",
            "id": 2,
            "params": {
                "module": 1,
                "center_mhz": 433.92,
                "span_mhz": 5.0,
                "points": 25
            }
        }

        ser.write((json.dumps(cmd) + '\n').encode())

        print("   ⏱️  Analyzing spectrum...")
        response = ser.readline().decode().strip()
        print(f"📥 Response: {response[:200]}...")  # Truncate for readability

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ Spectrum captured!")
                print(f"   📻 Center: {data['data']['center_mhz']} MHz")
                print(f"   📏 Span: {data['data']['span_mhz']} MHz")
                print(f"   📊 Points: {data['data']['points']}")

                # Find peak
                rssi_values = data['data']['rssi_dbm']
                freqs = data['data']['frequencies_mhz']

                if rssi_values:
                    max_rssi = max(rssi_values)
                    max_idx = rssi_values.index(max_rssi)
                    print(f"   🎯 Peak: {freqs[max_idx]:.2f} MHz at {max_rssi} dBm")

                    # Simple ASCII visualization
                    print("\n   Spectrum (simplified):")
                    for i in range(0, len(rssi_values), max(1, len(rssi_values) // 10)):
                        freq = freqs[i]
                        rssi = rssi_values[i]
                        # Normalize to 0-20 chars
                        bars = int((rssi + 100) / 5)  # Assuming -100 to 0 dBm range
                        bars = max(0, min(20, bars))
                        print(f"     {freq:6.1f} MHz {'█' * bars} {rssi} dBm")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n✅ Scanner & Spectrum tests completed!")
        print("\n💡 Tips:")
        print("   - Use scanner to find active frequencies")
        print("   - Use spectrum for detailed analysis around a frequency")
        print("   - Adjust threshold_dbm to filter weak signals")

        ser.close()

    except serial.SerialException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    test_scanner(port)

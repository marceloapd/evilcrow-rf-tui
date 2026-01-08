#!/usr/bin/env python3
"""
Teste rápido do protocolo serial do Evil Crow RF V2
"""

import serial
import json
import time
import sys

def test_serial(port='/dev/ttyUSB0', baud=115200):
    print(f"🔌 Conectando em {port} @ {baud} baud...")

    try:
        ser = serial.Serial(port, baud, timeout=2)
        time.sleep(2)  # Wait for device to be ready

        # Clear buffer
        ser.reset_input_buffer()

        print("✅ Conectado!")
        print("\n📡 Aguardando evento 'ready'...")

        # Read ready event
        line = ser.readline().decode().strip()
        if line:
            print(f"← {line}")
            try:
                data = json.loads(line)
                if data.get('event') == 'ready':
                    print(f"✅ Device ready! Firmware: {data['data']['firmware_version']}")
            except:
                pass

        print("\n🧪 Testando comandos...\n")

        # Test 1: Ping
        print("📤 Enviando: ping")
        cmd = {"cmd": "ping", "id": 1}
        ser.write((json.dumps(cmd) + '\n').encode())

        response = ser.readline().decode().strip()
        print(f"📥 Resposta: {response}")

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ Status: OK")
                print(f"   📊 Uptime: {data['data']['uptime_ms']} ms")
                print(f"   💾 Free Heap: {data['data']['free_heap']} bytes")
                print(f"   📦 Firmware: {data['data']['firmware_version']}")
        except Exception as e:
            print(f"   ❌ Erro ao parsear: {e}")

        print()

        # Test 2: Get Status
        print("📤 Enviando: get_status")
        cmd = {"cmd": "get_status", "id": 2}
        ser.write((json.dumps(cmd) + '\n').encode())

        response = ser.readline().decode().strip()
        print(f"📥 Resposta: {response}")

        try:
            data = json.loads(response)
            if data['status'] == 'ok':
                print(f"   ✅ Status: OK")
                print(f"   📻 Frequency: {data['data']['frequency_mhz']} MHz")
                print(f"   🔴 RX Active: {data['data']['rx_active']}")
                print(f"   🔵 TX Active: {data['data']['tx_active']}")
                print(f"   ⚡ Jammer: {data['data']['jammer_active']}")
        except Exception as e:
            print(f"   ❌ Erro ao parsear: {e}")

        print("\n✅ Testes concluídos!")

        ser.close()

    except serial.SerialException as e:
        print(f"❌ Erro: {e}")
        print("\nDicas:")
        print("  - Certifique-se que o Evil Crow está conectado")
        print("  - Verifique se a porta está correta (ls /dev/ttyUSB*)")
        print("  - Você está no grupo uucp? (groups)")
        sys.exit(1)

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    test_serial(port)

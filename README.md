# Evil Crow RF V2 - TUI Edition

A modern TUI (Text User Interface) to control the Evil Crow RF V2 via USB serial, featuring advanced attacks and compatibility with Flipper Zero and URH.

## 📊 Project Status

### ✅ Implemented (Phase 1)
- [x] Project structure (mono-repo)
- [x] PlatformIO configured
- [x] CC1101 driver migrated (1308 lines)
- [x] JSON Lines serial protocol
- [x] Basic commands: `ping`, `get_status`, `reboot`
- [x] Flash and test scripts
- [x] Compilation working (RAM: 11.6%, Flash: 22.0%)
- [x] Serial protocol tests passing

### ✅ Implemented (Phase 2 - RX & TX)
- [x] RX Operations (signal capture with interrupt handler)
- [x] Signal analysis (timing patterns, binary representation)
- [x] RX commands: `rx_config`, `rx_start`, `rx_stop`
- [x] Asynchronous `signal_received` events
- [x] CC1101 initialization and configuration
- [x] TX Operations (signal transmission/replay)
- [x] TX command: `tx_send` with timing array and repeat count
- [x] Automatic TX pin toggling with microsecond precision

### 🚧 In Development (Phase 2)
- [ ] Jammer (frequency blocking)
- [ ] Scanner & Spectrum Analyzer

### 📋 Planned (Phases 3-4)
- [ ] Advanced attacks (Rolljam, Rollback, Bruteforce)
- [ ] Python TUI with Textual
- [ ] File formats (RAW, BIN, SUB, URH)
- [ ] Storage manager (~/.evilcrow/)
- [ ] 12 interactive screens
- [ ] Visual spectrum analyzer

## 🎯 Planned Features

### RF Operations
- **Record**: RF signal capture with real-time spectrum analyzer
- **Transmit**: Captured signal replay
- **Jammer**: Specific frequency blocking
- **Scanner**: Automatic frequency sweep (300-928 MHz)

### Advanced Attacks
- **Rolljam**: Rolling code attack
- **Rollback**: Replay old codes
- **Bruteforce**: Brute force on DIP switches and fixed codes

### Supported Formats
- **RAW**: JSON with timings
- **BIN**: Compact binary format
- **SUB**: Flipper Zero compatible (.sub)
- **URH**: Universal Radio Hacker compatible

## 📋 Requirements

### Hardware
- Evil Crow RF V2
- USB Cable

### Software
- **PlatformIO** (to compile firmware)
- **Python 3.8+** (for TUI - not yet implemented)
- **Linux** (tested on Arch Linux)

## 🔧 Installation

### 1. Install PlatformIO

```bash
# Arch Linux - via pipx (recommended)
sudo pacman -S python-pipx
pipx install platformio

# Or on other distros
pip install --user platformio
```

### 2. Configure USB Permissions

```bash
# Arch Linux - add to uucp group
sudo usermod -a -G uucp $USER

# Other distros - add to dialout group
sudo usermod -a -G dialout $USER

# Install PlatformIO udev rules (recommended)
curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core/develop/platformio/assets/system/99-platformio-udev.rules | sudo tee /etc/udev/rules.d/99-platformio-udev.rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# IMPORTANT: Logout/login to apply group changes
```

### 3. Clone and Compile Firmware

```bash
# Clone repository
git clone https://github.com/you/evilcrow-rf-tui.git
cd evilcrow-rf-tui/firmware

# Compile
pio run

# Flash to Evil Crow
pio run --target upload

# Or use the script
cd ..
./scripts/flash_firmware.sh
```

## 🧪 Testing the Firmware

### Method 1: Python Script

```bash
python scripts/test_serial.py
```

**Expected output:**
```
🔌 Connecting to /dev/ttyUSB0 @ 115200 baud...
✅ Connected!
📡 Waiting for 'ready' event...
← {"type":"event","event":"ready","timestamp":123,"data":{"firmware_version":"2.0.0-tui"}}
✅ Device ready! Firmware: 2.0.0-tui

🧪 Testing commands...

📤 Sending: ping
📥 Response: {"status":"ok","cmd":"ping","id":1,"data":{"firmware_version":"2.0.0-tui","uptime_ms":84073,"free_heap":350660}}
   ✅ Status: OK
   📊 Uptime: 84073 ms
   💾 Free Heap: 350660 bytes
   📦 Firmware: 2.0.0-tui
```

### Method 2: Serial Monitor

```bash
# Terminal 1: Monitor
cd firmware
pio device monitor

# Terminal 2: Send commands
echo '{"cmd":"ping","id":1}' > /dev/ttyUSB0
echo '{"cmd":"get_status","id":2}' > /dev/ttyUSB0
```

## 📁 Current Project Structure

```
evilcrow-rf-tui/
├── firmware/              # ESP32 firmware (PlatformIO)
│   ├── src/
│   │   ├── main.cpp              ✅ Implemented
│   │   ├── config.h              ✅ Implemented
│   │   ├── serial_protocol.cpp/h ✅ Implemented
│   │   ├── cc1101_driver.cpp/h   ✅ Implemented (1308 lines)
│   │   ├── rf_operations.cpp/h   🚧 Next
│   │   └── signal_analysis.cpp/h 🚧 Next
│   ├── platformio.ini        ✅ Configured
│   └── .gitignore           ✅ Configured
│
├── tui/                   # Python TUI
│   └── (not yet implemented)
│
├── scripts/
│   ├── flash_firmware.sh  ✅ Implemented
│   └── test_serial.py     ✅ Implemented
│
├── docs/                  📋 Planned
├── .gitignore            ✅ Configured
└── README.md             ✅ Updated
```

## 🔌 Serial Protocol (Implemented)

The firmware uses **JSON Lines** (one JSON object per line) for serial communication at 115200 baud.

### Available Commands

#### 1. ping
Tests communication and returns device information.

**Command:**
```json
{"cmd":"ping","id":1}
```

**Response:**
```json
{
  "status":"ok",
  "cmd":"ping",
  "id":1,
  "data":{
    "firmware_version":"2.0.0-tui",
    "uptime_ms":84073,
    "free_heap":350660
  }
}
```

#### 2. get_status
Returns current device state.

**Command:**
```json
{"cmd":"get_status","id":2}
```

**Response:**
```json
{
  "status":"ok",
  "cmd":"get_status",
  "id":2,
  "data":{
    "rx_active":false,
    "tx_active":false,
    "jammer_active":false,
    "module":1,
    "frequency_mhz":433.92,
    "free_heap":350660,
    "uptime_ms":84123
  }
}
```

#### 3. reboot
Restarts the ESP32.

**Command:**
```json
{"cmd":"reboot","id":3}
```

**Response:**
```json
{"status":"ok","cmd":"reboot","id":3}
```

#### 4. rx_config
Configure RX parameters (frequency, module, modulation, etc.).

**Command:**
```json
{
  "cmd":"rx_config",
  "id":4,
  "params":{
    "module":1,
    "frequency_mhz":433.92,
    "modulation":2,
    "rx_bandwidth_khz":812.5
  }
}
```

**Response:**
```json
{
  "status":"ok",
  "cmd":"rx_config",
  "id":4,
  "data":{
    "module":1,
    "frequency_mhz":433.92
  }
}
```

#### 5. rx_start
Start receiving RF signals.

**Command:**
```json
{"cmd":"rx_start","id":5}
```

**Response:**
```json
{
  "status":"ok",
  "cmd":"rx_start",
  "id":5,
  "data":{
    "module":1,
    "frequency_mhz":433.92
  }
}
```

#### 6. rx_stop
Stop receiving. Triggers signal analysis if signal was captured.

**Command:**
```json
{"cmd":"rx_stop","id":6}
```

**Response:**
```json
{"status":"ok","cmd":"rx_stop","id":6}
```

#### 7. tx_send
Transmit RF signal using captured timings.

**Command:**
```json
{
  "cmd":"tx_send",
  "id":7,
  "params":{
    "module":1,
    "timings_us":[450,1200,450,1200,450,450],
    "repeat":5
  }
}
```

**Response:**
```json
{
  "status":"ok",
  "cmd":"tx_send",
  "id":7,
  "data":{
    "module":1,
    "count":6,
    "repeat":5
  }
}
```

### Asynchronous Events

The firmware sends events without request:

**'ready' event** (on boot):
```json
{
  "type":"event",
  "event":"ready",
  "timestamp":0,
  "data":{
    "firmware_version":"2.0.0-tui"
  }
}
```

**'signal_received' event** (when signal captured):
```json
{
  "type":"event",
  "event":"signal_received",
  "timestamp":12345,
  "data":{
    "sample_count":245,
    "samples_per_symbol":450,
    "raw_timings_us":[450,1200,450,1200,...],
    "total_samples":245,
    "analysis":"Binary: 01010101... Samples/Symbol: 450us Smoothed count: 120"
  }
}
```

## 🛠️ Development

### Compile

```bash
cd firmware
pio run
```

### Upload

```bash
pio run --target upload
```

### Serial Monitor

```bash
pio device monitor
```

### Clean Build

```bash
pio run --target clean
```

## 🐛 Troubleshooting

### Port busy or permission denied

```bash
# Check port
ls -l /dev/ttyUSB*

# Add to correct group
# Arch Linux
sudo usermod -a -G uucp $USER

# Ubuntu/Debian
sudo usermod -a -G dialout $USER

# Apply changes (logout/login or)
newgrp uucp  # or newgrp dialout
```

### PlatformIO not found

```bash
# Check installation
pio --version

# If it doesn't work, check PATH
echo $PATH | grep .local/bin

# Add to PATH if needed
export PATH=$PATH:~/.local/bin
```

### Compilation fails

```bash
# Clean and recompile
cd firmware
pio run --target clean
pio run
```

## 📈 Roadmap

### Phase 1: Basic Firmware ✅ (Complete)
- Project setup
- CC1101 driver
- Serial protocol
- Basic commands

### Phase 2: RF Operations 🚧 (In progress)
- RX (signal capture)
- TX (transmission)
- Jammer
- Scanner & Spectrum

### Phase 3: Advanced Attacks 📋 (Planned)
- Rolljam
- Rollback
- Bruteforce
- Protocol detection

### Phase 4: Python TUI 📋 (Planned)
- Python serial client
- Textual interface
- Storage manager
- File formats (RAW, BIN, SUB, URH)
- 12 interactive screens

### Phase 5: Advanced Features 📋 (Future)
- Spectrum waterfall
- Protocol decoder
- Cloud signal library
- Multi-device support

## 📊 Firmware Statistics

- **RAM Usage**: 11.6% (38,136 / 327,680 bytes)
- **Flash Usage**: 22.1% (289,821 / 1,310,720 bytes)
- **Build Time**: ~4 seconds
- **Upload Speed**: 921600 baud

## ⚠️ Legal Disclaimer

This device is intended **exclusively** for:
- Authorized security testing
- Research in controlled environments
- Educational purposes

**NEVER** use this device for:
- Interfering with unauthorized communications
- Illegal jamming
- Any activity prohibited by law

Misuse may result in legal penalties. Use responsibly!

## 📝 License

GPL-3.0 - See LICENSE for details.

## 🙏 Credits

- **Original Firmware**: Joel Serna (@JoelSernaMoreno)
- **CC1101 Driver**: ELECHOUSE & Little Satan
- **TUI Edition**: Developed with ❤️ for the community

## 📞 Support

- **Discord**: https://discord.gg/evilcrowrf
- **Issues**: https://github.com/you/evilcrow-rf-tui/issues
- **Original Repo**: https://github.com/joelsernamoreno/EvilCrowRF-V2

---

**Last Update**: January 2025
**Firmware Version**: 2.0.0-tui
**Status**: 🚧 Phase 1 complete, Phase 2 RX/TX complete, Jammer/Scanner in development

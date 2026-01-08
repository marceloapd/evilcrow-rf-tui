# Evil Crow RF V2 - TUI Edition

Uma interface TUI (Text User Interface) moderna para controlar o Evil Crow RF V2 via serial USB, com ataques avançados e compatibilidade com Flipper Zero e URH.

## 🚀 Features

### RF Operations
- **Record**: Captura sinais RF com spectrum analyzer em tempo real
- **Transmit**: Replay de sinais capturados
- **Jammer**: Bloqueio de frequências específicas
- **Scanner**: Varredura automática de frequências (300-928 MHz)

### Ataques Avançados
- **Rolljam**: Ataque a rolling codes
- **Rollback**: Replay de códigos antigos
- **Bruteforce**: Força bruta em DIP switches e códigos fixos

### Formatos Suportados
- **RAW**: JSON com timings
- **BIN**: Formato binário compacto
- **SUB**: Compatível com Flipper Zero (.sub)
- **URH**: Compatível com Universal Radio Hacker

## 📋 Requisitos

### Hardware
- Evil Crow RF V2
- Cabo USB

### Software
- Python 3.8+
- PlatformIO (para compilar firmware)
- Linux (testado em Arch Linux)

## 🔧 Instalação

### 1. Instalar PlatformIO

```bash
# Arch Linux
sudo pacman -S platformio

# Ou via pipx
pipx install platformio
```

### 2. Compilar e Flashear Firmware

```bash
cd firmware
pio run --target upload
```

### 3. Instalar TUI

```bash
cd tui
pip install -e .
```

## 🎮 Uso

### Executar TUI

```bash
evilcrow
```

### Atalhos de Teclado

- `h` - Home
- `r` - Record (RX)
- `t` - Transmit (TX)
- `j` - Jammer
- `s` - Scanner
- `v` - Saved Signals
- `b` - Bruteforce
- `1` - Rolljam Attack
- `2` - Rollback Attack
- `c` - CC1101 Settings
- `e` - ECRF Settings
- `l` - Logs
- `q` - Quit
- `Space` - Start/Stop (context-aware)
- `Ctrl+S` - Save signal
- `Ctrl+C` - Emergency stop

## 📁 Estrutura do Projeto

```
evilcrow-rf-tui/
├── firmware/              # ESP32 firmware (PlatformIO)
│   ├── src/
│   │   ├── main.cpp
│   │   ├── cc1101_driver.cpp/h
│   │   ├── serial_protocol.cpp/h
│   │   ├── rf_operations.cpp/h
│   │   ├── signal_analysis.cpp/h
│   │   └── config.h
│   └── platformio.ini
│
├── tui/                   # Python TUI
│   ├── src/evilcrow_tui/
│   │   ├── app.py
│   │   ├── serial_client.py
│   │   ├── storage.py
│   │   ├── signal_formats.py
│   │   ├── widgets/
│   │   └── screens/
│   └── pyproject.toml
│
├── docs/
├── scripts/
└── README.md
```

## 🔌 Protocolo Serial

O firmware e a TUI se comunicam via JSON Lines (um objeto JSON por linha):

**Comando (Host → Device)**:
```json
{"cmd": "rx_config", "id": 1, "params": {"module": 1, "frequency_mhz": 433.92, "modulation": "ASK"}}
```

**Resposta (Device → Host)**:
```json
{"status": "ok", "cmd": "rx_config", "id": 1, "data": {...}}
```

**Evento (Device → Host)**:
```json
{"type": "event", "event": "signal_received", "timestamp": 123456, "data": {"raw_timings_us": [...]}}
```

## 📊 Armazenamento

Todos os sinais são salvos em `~/.evilcrow/`:

```
~/.evilcrow/
├── signals/
│   ├── raw/         # JSON
│   ├── bin/         # Binário
│   ├── sub/         # Flipper Zero
│   └── urh/         # URH
├── logs/
├── presets/
└── config.json
```

## 🛠️ Desenvolvimento

### Compilar Firmware

```bash
cd firmware
pio run
```

### Monitorar Serial

```bash
pio device monitor
```

### Testar Protocolo

```bash
# Terminal 1: Monitor serial
pio device monitor

# Terminal 2: Enviar comando
echo '{"cmd":"ping","id":1}' > /dev/ttyUSB0
```

## ⚠️ Avisos Legais

Este dispositivo é destinado **exclusivamente** para:
- Testes de segurança autorizados
- Pesquisa em ambientes controlados
- Fins educacionais

**NUNCA** use este dispositivo para:
- Interferir em comunicações não autorizadas
- Jamming ilegal
- Qualquer atividade proibida por lei

O uso indevido pode resultar em penalidades legais. Use com responsabilidade!

## 📝 Licença

GPL-3.0 - Veja LICENSE para mais detalhes.

## 🙏 Créditos

- **Firmware Original**: Joel Serna (@JoelSernaMoreno)
- **CC1101 Driver**: ELECHOUSE & Little Satan
- **TUI Edition**: Desenvolvido com ❤️ para a comunidade

## 📞 Suporte

- Discord: https://discord.gg/evilcrowrf
- Issues: https://github.com/you/evilcrow-rf-tui/issues

---

**Status do Projeto**: 🚧 Em desenvolvimento ativo - Fase 1 (Firmware básico) completa

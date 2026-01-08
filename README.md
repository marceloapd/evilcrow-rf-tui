# Evil Crow RF V2 - TUI Edition

Uma interface TUI (Text User Interface) moderna para controlar o Evil Crow RF V2 via serial USB, com ataques avançados e compatibilidade com Flipper Zero e URH.

## 📊 Status do Projeto

### ✅ Implementado (Fase 1)
- [x] Estrutura do projeto (mono-repo)
- [x] PlatformIO configurado
- [x] Driver CC1101 migrado (1308 linhas)
- [x] Protocolo serial JSON Lines
- [x] Comandos básicos: `ping`, `get_status`, `reboot`
- [x] Scripts de flash e teste
- [x] Compilação funcionando (RAM: 6.6%, Flash: 21.1%)
- [x] Testes de protocolo serial passando

### 🚧 Em Desenvolvimento (Fase 2)
- [ ] RX Operations (captura de sinais)
- [ ] TX Operations (transmissão/replay)
- [ ] Jammer (bloqueio de frequências)
- [ ] Scanner & Spectrum Analyzer

### 📋 Planejado (Fases 3-4)
- [ ] Ataques avançados (Rolljam, Rollback, Bruteforce)
- [ ] TUI Python com Textual
- [ ] Formatos de arquivo (RAW, BIN, SUB, URH)
- [ ] Storage manager (~/.evilcrow/)
- [ ] 12 telas interativas
- [ ] Spectrum analyzer visual

## 🎯 Features Planejadas

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
- **PlatformIO** (para compilar firmware)
- **Python 3.8+** (para TUI - ainda não implementada)
- **Linux** (testado em Arch Linux)

## 🔧 Instalação

### 1. Instalar PlatformIO

```bash
# Arch Linux - via pipx (recomendado)
sudo pacman -S python-pipx
pipx install platformio

# Ou em outras distros
pip install --user platformio
```

### 2. Configurar Permissões USB

```bash
# Arch Linux - adicionar ao grupo uucp
sudo usermod -a -G uucp $USER

# Outras distros - adicionar ao grupo dialout
sudo usermod -a -G dialout $USER

# Instalar regras udev do PlatformIO (recomendado)
curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core/develop/platformio/assets/system/99-platformio-udev.rules | sudo tee /etc/udev/rules.d/99-platformio-udev.rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# IMPORTANTE: Fazer logout/login para aplicar mudanças de grupo
```

### 3. Clonar e Compilar Firmware

```bash
# Clonar repositório
git clone https://github.com/you/evilcrow-rf-tui.git
cd evilcrow-rf-tui/firmware

# Compilar
pio run

# Flashear no Evil Crow
pio run --target upload

# Ou usar o script
cd ..
./scripts/flash_firmware.sh
```

## 🧪 Testando o Firmware

### Método 1: Script Python

```bash
python scripts/test_serial.py
```

**Saída esperada:**
```
🔌 Conectando em /dev/ttyUSB0 @ 115200 baud...
✅ Conectado!
📡 Aguardando evento 'ready'...
← {"type":"event","event":"ready","timestamp":123,"data":{"firmware_version":"2.0.0-tui"}}
✅ Device ready! Firmware: 2.0.0-tui

🧪 Testando comandos...

📤 Enviando: ping
📥 Resposta: {"status":"ok","cmd":"ping","id":1,"data":{"firmware_version":"2.0.0-tui","uptime_ms":84073,"free_heap":350660}}
   ✅ Status: OK
   📊 Uptime: 84073 ms
   💾 Free Heap: 350660 bytes
   📦 Firmware: 2.0.0-tui
```

### Método 2: Monitor Serial

```bash
# Terminal 1: Monitor
cd firmware
pio device monitor

# Terminal 2: Enviar comandos
echo '{"cmd":"ping","id":1}' > /dev/ttyUSB0
echo '{"cmd":"get_status","id":2}' > /dev/ttyUSB0
```

## 📁 Estrutura Atual do Projeto

```
evilcrow-rf-tui/
├── firmware/              # ESP32 firmware (PlatformIO)
│   ├── src/
│   │   ├── main.cpp              ✅ Implementado
│   │   ├── config.h              ✅ Implementado
│   │   ├── serial_protocol.cpp/h ✅ Implementado
│   │   ├── cc1101_driver.cpp/h   ✅ Implementado (1308 linhas)
│   │   ├── rf_operations.cpp/h   🚧 Próximo
│   │   └── signal_analysis.cpp/h 🚧 Próximo
│   ├── platformio.ini        ✅ Configurado
│   └── .gitignore           ✅ Configurado
│
├── tui/                   # Python TUI
│   └── (ainda não implementado)
│
├── scripts/
│   ├── flash_firmware.sh  ✅ Implementado
│   └── test_serial.py     ✅ Implementado
│
├── docs/                  📋 Planejado
├── .gitignore            ✅ Configurado
└── README.md             ✅ Atualizado
```

## 🔌 Protocolo Serial (Implementado)

O firmware usa **JSON Lines** (um objeto JSON por linha) para comunicação serial a 115200 baud.

### Comandos Disponíveis

#### 1. ping
Testa comunicação e retorna informações do device.

**Comando:**
```json
{"cmd":"ping","id":1}
```

**Resposta:**
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
Retorna o estado atual do dispositivo.

**Comando:**
```json
{"cmd":"get_status","id":2}
```

**Resposta:**
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
Reinicia o ESP32.

**Comando:**
```json
{"cmd":"reboot","id":3}
```

**Resposta:**
```json
{"status":"ok","cmd":"reboot","id":3}
```

### Eventos Assíncronos

O firmware envia eventos sem solicitar:

**Evento 'ready'** (ao iniciar):
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

## 🛠️ Desenvolvimento

### Compilar

```bash
cd firmware
pio run
```

### Upload

```bash
pio run --target upload
```

### Monitor Serial

```bash
pio device monitor
```

### Limpar Build

```bash
pio run --target clean
```

## 🐛 Troubleshooting

### Porta ocupada ou sem permissão

```bash
# Verificar porta
ls -l /dev/ttyUSB*

# Adicionar ao grupo correto
# Arch Linux
sudo usermod -a -G uucp $USER

# Ubuntu/Debian
sudo usermod -a -G dialout $USER

# Aplicar mudanças (logout/login ou)
newgrp uucp  # ou newgrp dialout
```

### PlatformIO não encontrado

```bash
# Verificar instalação
pio --version

# Se não funcionar, verificar PATH
echo $PATH | grep .local/bin

# Adicionar ao PATH se necessário
export PATH=$PATH:~/.local/bin
```

### Compilação falha

```bash
# Limpar e recompilar
cd firmware
pio run --target clean
pio run
```

## 📈 Roadmap

### Fase 1: Firmware Básico ✅ (Completa)
- Setup do projeto
- Driver CC1101
- Protocolo serial
- Comandos básicos

### Fase 2: Operações RF 🚧 (Em andamento)
- RX (captura de sinais)
- TX (transmissão)
- Jammer
- Scanner & Spectrum

### Fase 3: Ataques Avançados 📋 (Planejado)
- Rolljam
- Rollback
- Bruteforce
- Protocol detection

### Fase 4: TUI Python 📋 (Planejado)
- Cliente serial Python
- Interface Textual
- Storage manager
- Formatos de arquivo (RAW, BIN, SUB, URH)
- 12 telas interativas

### Fase 5: Features Avançadas 📋 (Futuro)
- Spectrum waterfall
- Protocol decoder
- Cloud signal library
- Multi-device support

## 📊 Estatísticas do Firmware

- **RAM Usage**: 6.6% (21.488 / 327.680 bytes)
- **Flash Usage**: 21.1% (276.625 / 1.310.720 bytes)
- **Build Time**: ~8 segundos
- **Upload Speed**: 921600 baud

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

- **Discord**: https://discord.gg/evilcrowrf
- **Issues**: https://github.com/you/evilcrow-rf-tui/issues
- **Original Repo**: https://github.com/joelsernamoreno/EvilCrowRF-V2

---

**Última Atualização**: Janeiro 2025
**Versão Firmware**: 2.0.0-tui
**Status**: 🚧 Fase 1 completa, Fase 2 em desenvolvimento

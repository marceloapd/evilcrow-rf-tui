"""
Main TUI Application for Evil Crow RF V2
Hacker-style interface
"""
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Label, Button, ListView, ListItem
from textual.binding import Binding
from .serial_client import SerialClient
from .screens import RecordScreen, TransmitScreen, JammerScreen


class StatusBar(Static):
    """Hacker-style status bar"""

    def __init__(self):
        super().__init__()
        self.connected = False
        self.device_status = {}

    def on_mount(self):
        self.set_interval(1.0, self.update_status)  # Reduzido de 0.5s para 1s

    def update_status(self):
        if self.connected:
            status = "[●] ONLINE"
        else:
            status = "[○] OFFLINE"

        rx_state = "[RX:OFF]"
        tx_state = "[TX:OFF]"
        jam_state = "[JAM:OFF]"

        if self.device_status:
            if self.device_status.get('rx_active'):
                rx_state = "[RX:ON]"
            if self.device_status.get('tx_active'):
                tx_state = "[TX:ON]"
            if self.device_status.get('jammer_active'):
                jam_state = "[JAM:ACTIVE]"

        freq = self.device_status.get('frequency_mhz', 0.0)
        heap = self.device_status.get('free_heap', 0)

        self.update(
            f" {status}  {rx_state} {tx_state} {jam_state}  "
            f"FREQ:{freq:.2f}MHz  MEM:{heap//1024}KB"
        )


class HomeScreen(Container):
    """Hacker-style home screen"""

    def compose(self) -> ComposeResult:
        yield Static("""
  ███████╗██╗   ██╗██╗██╗      ██████╗██████╗  ██████╗ ██╗    ██╗
  ██╔════╝██║   ██║██║██║     ██╔════╝██╔══██╗██╔═══██╗██║    ██║
  █████╗  ██║   ██║██║██║     ██║     ██████╔╝██║   ██║██║ █╗ ██║
  ██╔══╝  ╚██╗ ██╔╝██║██║     ██║     ██╔══██╗██║   ██║██║███╗██║
  ███████╗ ╚████╔╝ ██║███████╗╚██████╗██║  ██║╚██████╔╝╚███╔███╔╝
  ╚══════╝  ╚═══╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝
            RF PENETRATION TESTING FRAMEWORK  [ v2.0 ]
""", id="banner")

        yield Static("")  # Espaçamento

        with Horizontal():
            # Coluna esquerda - Menu principal
            with Vertical(id="left-column"):
                yield Static("┌─ DEVICE ───────────────────────────────────────┐", classes="section")
                yield Label(id="device-info", classes="device-info")
                yield Static("└─────────────────────────────────────────────────┘", classes="section")

                yield Static("")  # Espaçamento

                yield Static("┌─ OPERATIONS (↑↓ arrows / hotkeys) ────────────┐", classes="section")
                with ListView(id="menu-list"):
                    yield ListItem(Label("RECORD      • Capture RF signals"), id="item-record")
                    yield ListItem(Label("TRANSMIT    • Replay captured signals"), id="item-transmit")
                    yield ListItem(Label("JAMMER      • Block target frequency"), id="item-jammer")
                    yield ListItem(Label("SCANNER     • Sweep frequency range"), id="item-scanner")
                    yield ListItem(Label("VAULT       • Manage saved signals"), id="item-vault")
                    yield ListItem(Label("ATTACKS     • RollJam, Bruteforce, Rollback"), id="item-attacks")
                    yield ListItem(Label("CONFIG      • CC1101 settings"), id="item-config")
                    yield ListItem(Label("LOGS        • View activity logs"), id="item-logs")
                yield Static("└─────────────────────────────────────────────────┘", classes="section")

            # Coluna direita - Live Status
            with Vertical(id="right-column"):
                yield Static("┌─ LIVE STATUS ──────┐", classes="section")
                yield Label(id="live-status", classes="live-status")
                yield Static("└─────────────────────┘", classes="section")

        yield Static("")  # Espaçamento
        yield Static("┌─ KEYBOARD SHORTCUTS ────────────────────────────────────────┐", classes="section")
        yield Static("│ R:Record  T:Transmit  J:Jammer  S:Scanner  V:Vault         │", classes="shortcuts")
        yield Static("│ A:Attacks  C:Config  L:Logs  Q:Quit  H:Help  ^C:Emergency  │", classes="shortcuts")
        yield Static("└──────────────────────────────────────────────────────────────┘", classes="section")


class EvilCrowApp(App):
    """Evil Crow RF V2 TUI - Hacker Edition"""

    CSS = """
    Screen {
        background: #000000;
        color: #00ff00;
    }

    StatusBar {
        dock: top;
        height: 1;
        background: #003300;
        color: #00ff00;
        text-style: bold;
    }

    #banner {
        color: #00ff00;
        text-align: center;
        text-style: bold;
    }

    .section {
        color: #00aa00;
    }

    #left-column {
        width: 70%;
        padding: 0 1;
    }

    #right-column {
        width: 30%;
        padding: 0 1;
    }

    #menu-list {
        height: 8;
        border: none;
        background: #000000;
        padding: 0 1;
    }

    #menu-list > ListItem {
        height: 1;
        background: #000000;
        color: #00ff00;
        padding: 0;
    }

    #menu-list > ListItem > Label {
        background: #000000;
        color: #00ff00;
    }

    #menu-list > ListItem:hover, #menu-list > .list--highlight {
        background: #004400 !important;
    }

    #menu-list > ListItem:hover > Label, #menu-list > .list--highlight > Label {
        background: #004400;
        color: #00ffff;
        text-style: bold reverse;
        border: solid #00ff00;
    }

    #menu-list:focus {
        border: solid #00ff00;
    }

    .live-status {
        color: #00ff00;
        height: auto;
    }

    .shortcuts {
        color: #00ff00;
    }

    .device-info {
        color: #00ff00;
    }

    .footer-help {
        color: #00aa00;
        text-align: center;
    }

    Label {
        color: #00ff00;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("h", "help", "Help"),
        Binding("r", "record", "Record"),
        Binding("t", "transmit", "Transmit"),
        Binding("v", "vault", "Vault"),
        Binding("j", "jammer", "Jammer"),
        Binding("s", "scanner", "Scanner"),
        Binding("a", "attacks", "Attacks"),
        Binding("c", "config", "Config"),
        Binding("l", "logs", "Logs"),
        Binding("ctrl+c", "emergency_stop", "Emergency Stop", priority=True),
    ]

    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 115200):
        super().__init__()
        self.title = "EVIL CROW RF V2"
        self.port = port
        self.baud = baud
        self.client: SerialClient = None
        self.status_bar: StatusBar = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app"""
        self.status_bar = StatusBar()
        yield self.status_bar
        yield HomeScreen()

    def on_mount(self):
        """Called when app is mounted"""
        # Focar lista para navegação funcionar
        self.set_timer(0.1, lambda: self.query_one("#menu-list").focus())
        # Conectar em background para não travar a UI
        self.set_timer(0.5, self.connect_device)
        # Update live status panel
        self.set_interval(1.0, self.update_live_status)

    def connect_device(self):
        """Connect to Evil Crow device"""
        try:
            self.client = SerialClient(self.port, self.baud)
            if self.client.connect():
                self.status_bar.connected = True

                # Register event handlers
                self.client.on_event('signal_received', self.on_signal_received)
                self.client.on_event('scan_result', self.on_scan_result)
                self.client.on_event('spectrum_data', self.on_spectrum_data)

                # Get initial status
                self.update_device_status()
                self.set_interval(5.0, self.update_device_status)  # Reduzido frequência
            else:
                self.status_bar.connected = False
        except Exception as e:
            self.status_bar.connected = False

    def update_device_status(self):
        """Update device status from firmware"""
        if self.client:
            # Check if still connected
            if not self.client.is_connected():
                if self.status_bar.connected:
                    # Device was disconnected
                    self.status_bar.connected = False
                    self.status_bar.device_status = {}
                else:
                    # Try to reconnect
                    try:
                        if self.client.connect():
                            self.status_bar.connected = True
                            # Register event handlers again
                            self.client.on_event('signal_received', self.on_signal_received)
                            self.client.on_event('scan_result', self.on_scan_result)
                            self.client.on_event('spectrum_data', self.on_spectrum_data)
                    except:
                        pass
                return

            response = self.client.get_status()
            if response and response.get('status') == 'ok':
                if not self.status_bar.connected:
                    # Device reconnected
                    self.status_bar.connected = True
                self.status_bar.device_status = response.get('data', {})
                self.update_device_info_display()
            else:
                # No response, might be disconnected
                if self.client.is_connected():
                    # Still connected but no response (might be busy)
                    pass
                else:
                    # Disconnected
                    self.status_bar.connected = False
                    self.status_bar.device_status = {}

    def update_device_info_display(self):
        """Update device info display on home screen"""
        info_widget = self.query_one("#device-info", Label)
        data = self.status_bar.device_status

        if data:
            fw_ver = data.get('firmware_version', 'UNKNOWN')
            freq = data.get('frequency_mhz', 0.0)
            mod = data.get('modulation', 'UNKNOWN')
            rx = "ACTIVE" if data.get('rx_active') else "IDLE"
            tx = "ACTIVE" if data.get('tx_active') else "IDLE"
            jam = "ACTIVE" if data.get('jammer_active') else "IDLE"
            heap = data.get('free_heap', 0)
            uptime = data.get('uptime_ms', 0) / 1000

            info_text = f"""│ FIRMWARE ....... {fw_ver}  │  FREQUENCY .... {freq:.2f} MHz
│ MODULATION ..... {mod}     │  FREE HEAP .... {heap//1024} KB
│ RX MODE ........ {rx}      │  UPTIME ....... {uptime:.0f}s"""
            info_widget.update(info_text)
        else:
            info_widget.update("│ [ NO DATA AVAILABLE ]")

    def update_live_status(self):
        """Update live status panel with real-time info"""
        try:
            live_widget = self.query_one("#live-status", Label)
            data = self.status_bar.device_status

            # Connection indicator with blinking effect
            import time
            blink = "●" if int(time.time() * 2) % 2 else "○"

            if self.status_bar.connected and data:
                # Device is connected and responding
                rx_indicator = "▶" if data.get('rx_active') else "□"
                tx_indicator = "▶" if data.get('tx_active') else "□"
                jam_indicator = "▶" if data.get('jammer_active') else "□"

                freq = data.get('frequency_mhz', 0.0)
                rssi = data.get('rssi_dbm', -100)
                uptime = data.get('uptime_ms', 0) / 1000

                # Format uptime as HH:MM:SS
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                seconds = int(uptime % 60)

                status_text = f"""│ CONNECTION
│ {blink} ONLINE
│
│ ACTIVITY
│ RX  {rx_indicator}
│ TX  {tx_indicator}
│ JAM {jam_indicator}
│
│ SIGNAL
│ FREQ: {freq:.2f}MHz
│ RSSI: {rssi}dBm
│
│ UPTIME
│ {hours:02d}:{minutes:02d}:{seconds:02d}"""

                live_widget.update(status_text)
            elif self.status_bar.connected:
                # Connected but no data yet
                status_text = f"""│ CONNECTION
│ {blink} CONNECTING...
│
│ Waiting for
│ device data..."""
                live_widget.update(status_text)
            else:
                # Not connected
                status_text = f"""│ CONNECTION
│ ○ OFFLINE
│
│ Device not found
│ at {self.port}
│
│ Check:
│ • USB cable
│ • Port name
│ • Permissions"""
                live_widget.update(status_text)
        except Exception as e:
            # Widget might not exist yet
            pass

    # Event handlers
    def on_signal_received(self, data: dict):
        """Handle signal received event"""
        samples = len(data.get('raw_timings_us', []))
        self.notify(f"[ SIGNAL CAPTURED: {samples} SAMPLES ]", severity="information", timeout=2)

    def on_scan_result(self, data: dict):
        """Handle scan result event"""
        freq = data.get('frequency_mhz', 0.0)
        rssi = data.get('rssi_dbm', -100)
        self.notify(f"[ SIGNAL DETECTED: {freq:.2f} MHz @ {rssi} dBm ]", severity="information", timeout=2)

    def on_spectrum_data(self, data: dict):
        """Handle spectrum data event"""
        pass

    # Action handlers
    def action_help(self):
        """Show help"""
        self.notify("[ HELP: Use keyboard shortcuts to navigate ]", timeout=2)

    def action_record(self):
        """Go to record screen"""
        if self.client:
            self.push_screen(RecordScreen(self.client))
        else:
            self.notify("[ ERROR: Device not connected ]", severity="error", timeout=2)

    def action_transmit(self):
        """Go to transmit screen"""
        if self.client:
            self.push_screen(TransmitScreen(self.client))
        else:
            self.notify("[ ERROR: Device not connected ]", severity="error", timeout=2)

    def action_vault(self):
        """Go to saved signals screen"""
        self.notify("[ VAULT - NOT IMPLEMENTED YET ]", severity="warning", timeout=2)

    def action_jammer(self):
        """Go to jammer screen"""
        if self.client:
            self.push_screen(JammerScreen(self.client))
        else:
            self.notify("[ ERROR: Device not connected ]", severity="error", timeout=2)

    def action_scanner(self):
        """Go to scanner screen"""
        self.notify("[ SCANNER - NOT IMPLEMENTED YET ]", severity="warning", timeout=2)

    def action_attacks(self):
        """Go to attacks menu"""
        self.notify("[ ATTACKS - NOT IMPLEMENTED YET ]", severity="warning", timeout=2)

    def action_config(self):
        """Go to config screen"""
        self.notify("[ CONFIG - NOT IMPLEMENTED YET ]", severity="warning", timeout=2)

    def action_logs(self):
        """Go to logs screen"""
        self.notify("[ LOGS - NOT IMPLEMENTED YET ]", severity="warning", timeout=2)

    def action_emergency_stop(self):
        """Emergency stop all RF operations"""
        if self.client:
            if self.status_bar.device_status.get('rx_active'):
                self.client.rx_stop()
            if self.status_bar.device_status.get('jammer_active'):
                self.client.jammer_stop()
            self.notify("[ EMERGENCY STOP EXECUTED ]", severity="error", timeout=2)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection (Enter key or click)"""
        item_id = event.item.id

        if item_id == "item-record":
            self.action_record()
        elif item_id == "item-transmit":
            self.action_transmit()
        elif item_id == "item-jammer":
            self.action_jammer()
        elif item_id == "item-scanner":
            self.action_scanner()
        elif item_id == "item-vault":
            self.action_vault()
        elif item_id == "item-attacks":
            self.action_attacks()
        elif item_id == "item-config":
            self.action_config()
        elif item_id == "item-logs":
            self.action_logs()

    def on_shutdown_request(self):
        """Called when app is shutting down"""
        if self.client:
            # Stop all operations
            if self.status_bar.device_status.get('jammer_active'):
                self.client.jammer_stop()
            if self.status_bar.device_status.get('rx_active'):
                self.client.rx_stop()
            # Disconnect
            self.client.disconnect()

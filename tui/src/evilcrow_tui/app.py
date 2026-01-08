"""
Main TUI Application for Evil Crow RF V2
Hacker-style interface
"""
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Label, Button, ListView, ListItem
from textual.binding import Binding
from .serial_client import SerialClient


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

        yield Static("┌─ DEVICE ────────────────────────────────────────────────────┐", classes="section")
        yield Label(id="device-info", classes="device-info")
        yield Static("└──────────────────────────────────────────────────────────────┘", classes="section")

        yield Static("┌─ OPERATIONS (Use ↑↓ arrows or hotkeys) ────────────────────┐", classes="section")
        with ListView(id="menu-list"):
            yield ListItem(Label("[R] RECORD      • Capture RF signals"), id="item-record")
            yield ListItem(Label("[T] TRANSMIT    • Replay captured signals"), id="item-transmit")
            yield ListItem(Label("[J] JAMMER      • Block target frequency"), id="item-jammer")
            yield ListItem(Label("[S] SCANNER     • Sweep frequency range"), id="item-scanner")
            yield ListItem(Label("[V] VAULT       • Manage saved signals"), id="item-vault")
            yield ListItem(Label("[A] ATTACKS     • RollJam, Bruteforce, Rollback"), id="item-attacks")
            yield ListItem(Label("[C] CONFIG      • CC1101 settings"), id="item-config")
            yield ListItem(Label("[L] LOGS        • View activity logs"), id="item-logs")
        yield Static("└──────────────────────────────────────────────────────────────┘", classes="section")

        yield Static("  [Q] Quit  [H] Help  [CTRL+C] Emergency Stop", classes="footer-help")


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
        background: #003300 !important;
    }

    #menu-list > ListItem:hover > Label, #menu-list > .list--highlight > Label {
        background: #003300;
        color: #00ffff;
        text-style: bold;
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

    def connect_device(self):
        """Connect to Evil Crow device"""
        try:
            self.client = SerialClient(self.port, self.baud)
            if self.client.connect():
                self.status_bar.connected = True
                self.notify("[ CONNECTION ESTABLISHED ]", severity="information", timeout=2)

                # Register event handlers
                self.client.on_event('signal_received', self.on_signal_received)
                self.client.on_event('scan_result', self.on_scan_result)
                self.client.on_event('spectrum_data', self.on_spectrum_data)

                # Get initial status
                self.update_device_status()
                self.set_interval(5.0, self.update_device_status)  # Reduzido frequência
            else:
                self.status_bar.connected = False
                self.notify(f"[ CONNECTION FAILED: {self.port} ]", severity="error", timeout=3)
        except Exception as e:
            self.status_bar.connected = False
            self.notify(f"[ ERROR: {e} ]", severity="error", timeout=3)

    def update_device_status(self):
        """Update device status from firmware"""
        if self.client:
            response = self.client.get_status()
            if response and response.get('status') == 'ok':
                self.status_bar.device_status = response.get('data', {})
                self.update_device_info_display()

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
        self.notify("[ RECORD MODE - NOT IMPLEMENTED YET ]", severity="warning", timeout=2)

    def action_transmit(self):
        """Go to transmit screen"""
        self.notify("[ TRANSMIT MODE - NOT IMPLEMENTED YET ]", severity="warning", timeout=2)

    def action_vault(self):
        """Go to saved signals screen"""
        self.notify("[ VAULT - NOT IMPLEMENTED YET ]", severity="warning", timeout=2)

    def action_jammer(self):
        """Go to jammer screen"""
        self.notify("[ JAMMER - NOT IMPLEMENTED YET ]", severity="warning", timeout=2)

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

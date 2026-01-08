"""
Main TUI Application for Evil Crow RF V2
"""
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Label
from textual.binding import Binding
from .serial_client import SerialClient
import time


class StatusBar(Static):
    """Status bar showing connection and device state"""

    def __init__(self):
        super().__init__()
        self.connected = False
        self.device_status = {}

    def on_mount(self):
        self.set_interval(0.5, self.update_status)

    def update_status(self):
        if self.connected:
            status_icon = "🟢"
            status_text = "CONNECTED"
        else:
            status_icon = "🔴"
            status_text = "DISCONNECTED"

        rx_state = "RX: ⚪"
        tx_state = "TX: ⚪"
        jammer_state = "JAM: ⚪"

        if self.device_status:
            if self.device_status.get('rx_active'):
                rx_state = "RX: 🟢"
            if self.device_status.get('tx_active'):
                tx_state = "TX: 🟢"
            if self.device_status.get('jammer_active'):
                jammer_state = "JAM: 🔴"

        freq = self.device_status.get('frequency_mhz', 0.0)

        self.update(
            f"{status_icon} {status_text}  |  "
            f"{rx_state}  {tx_state}  {jammer_state}  |  "
            f"Freq: {freq:.2f} MHz"
        )


class HomeScreen(Container):
    """Main home screen"""

    def compose(self) -> ComposeResult:
        yield Static("╔══════════════════════════════════════════════════════════╗", classes="banner")
        yield Static("║          Evil Crow RF V2 - TUI Edition                   ║", classes="banner")
        yield Static("╚══════════════════════════════════════════════════════════╝", classes="banner")
        yield Static("")
        yield Static("Device Information:", classes="section-title")
        yield Label(id="device-info")
        yield Static("")
        yield Static("Quick Actions:", classes="section-title")
        yield Horizontal(
            Button("Record (R)", id="btn-record", variant="primary"),
            Button("Transmit (T)", id="btn-transmit", variant="success"),
            Button("Jammer (J)", id="btn-jammer", variant="error"),
            classes="button-row"
        )
        yield Horizontal(
            Button("Scanner (S)", id="btn-scanner", variant="default"),
            Button("Saved Signals (V)", id="btn-saved", variant="default"),
            Button("Settings (E)", id="btn-settings", variant="default"),
            classes="button-row"
        )
        yield Static("")
        yield Static("Press 'q' to quit | 'h' for help", classes="help-text")


class EvilCrowApp(App):
    """Evil Crow RF V2 TUI Application"""

    CSS = """
    Screen {
        background: $surface;
    }

    StatusBar {
        dock: top;
        height: 1;
        background: $accent;
        color: $text;
        content-align: center middle;
        text-style: bold;
    }

    .banner {
        color: $accent;
        text-align: center;
        text-style: bold;
    }

    .section-title {
        color: $primary;
        text-style: bold;
        margin: 1 0;
    }

    .button-row {
        height: 3;
        align: center middle;
        margin: 1 0;
    }

    Button {
        margin: 0 1;
    }

    .help-text {
        color: $text-muted;
        text-align: center;
        margin: 1 0;
    }

    #device-info {
        margin: 0 4;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("h", "goto_home", "Home"),
        Binding("r", "goto_record", "Record"),
        Binding("t", "goto_transmit", "Transmit"),
        Binding("v", "goto_saved", "Saved"),
        Binding("j", "goto_jammer", "Jammer"),
        Binding("s", "goto_scanner", "Scanner"),
        Binding("e", "goto_settings", "Settings"),
        Binding("l", "goto_logs", "Logs"),
        Binding("ctrl+c", "emergency_stop", "Emergency Stop"),
    ]

    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 115200):
        super().__init__()
        self.title = "Evil Crow RF V2 - TUI"
        self.port = port
        self.baud = baud
        self.client: SerialClient = None
        self.status_bar: StatusBar = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app"""
        yield Header()
        self.status_bar = StatusBar()
        yield self.status_bar
        yield HomeScreen()
        yield Footer()

    def on_mount(self):
        """Called when app is mounted"""
        self.connect_device()

    def connect_device(self):
        """Connect to Evil Crow device"""
        try:
            self.client = SerialClient(self.port, self.baud)
            if self.client.connect():
                self.status_bar.connected = True
                self.notify("Connected to Evil Crow RF V2", severity="information")

                # Register event handlers
                self.client.on_event('signal_received', self.on_signal_received)
                self.client.on_event('scan_result', self.on_scan_result)
                self.client.on_event('spectrum_data', self.on_spectrum_data)

                # Get initial status
                self.update_device_status()
                self.set_interval(2.0, self.update_device_status)
            else:
                self.status_bar.connected = False
                self.notify(f"Failed to connect to {self.port}", severity="error")
        except Exception as e:
            self.status_bar.connected = False
            self.notify(f"Connection error: {e}", severity="error")

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
            info_text = f"""
  Firmware: {data.get('firmware_version', 'Unknown')}
  Frequency: {data.get('frequency_mhz', 0.0):.2f} MHz
  Modulation: {data.get('modulation', 'Unknown')}
  RX Active: {'Yes' if data.get('rx_active') else 'No'}
  TX Active: {'Yes' if data.get('tx_active') else 'No'}
  Jammer Active: {'Yes' if data.get('jammer_active') else 'No'}
  Free Heap: {data.get('free_heap', 0)} bytes
  Uptime: {data.get('uptime_ms', 0) / 1000:.1f}s
"""
            info_widget.update(info_text.strip())
        else:
            info_widget.update("  No device data available")

    # Event handlers
    def on_signal_received(self, data: dict):
        """Handle signal received event"""
        self.notify(f"Signal received: {len(data.get('raw_timings_us', []))} samples",
                   severity="information")

    def on_scan_result(self, data: dict):
        """Handle scan result event"""
        freq = data.get('frequency_mhz', 0.0)
        rssi = data.get('rssi_dbm', -100)
        self.notify(f"Signal found: {freq:.2f} MHz ({rssi} dBm)",
                   severity="information")

    def on_spectrum_data(self, data: dict):
        """Handle spectrum data event"""
        # Will be used by spectrum analyzer widget
        pass

    # Action handlers
    def action_goto_home(self):
        """Go to home screen"""
        self.notify("Home screen (not yet implemented)", severity="warning")

    def action_goto_record(self):
        """Go to record screen"""
        self.notify("Record screen (not yet implemented)", severity="warning")

    def action_goto_transmit(self):
        """Go to transmit screen"""
        self.notify("Transmit screen (not yet implemented)", severity="warning")

    def action_goto_saved(self):
        """Go to saved signals screen"""
        self.notify("Saved signals screen (not yet implemented)", severity="warning")

    def action_goto_jammer(self):
        """Go to jammer screen"""
        self.notify("Jammer screen (not yet implemented)", severity="warning")

    def action_goto_scanner(self):
        """Go to scanner screen"""
        self.notify("Scanner screen (not yet implemented)", severity="warning")

    def action_goto_settings(self):
        """Go to settings screen"""
        self.notify("Settings screen (not yet implemented)", severity="warning")

    def action_goto_logs(self):
        """Go to logs screen"""
        self.notify("Logs screen (not yet implemented)", severity="warning")

    def action_emergency_stop(self):
        """Emergency stop all RF operations"""
        if self.client:
            if self.status_bar.device_status.get('rx_active'):
                self.client.rx_stop()
            if self.status_bar.device_status.get('jammer_active'):
                self.client.jammer_stop()
            self.notify("Emergency stop executed", severity="error")

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

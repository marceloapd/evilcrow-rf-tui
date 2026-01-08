"""
Record Screen - RF Signal Capture
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input
from textual.binding import Binding


class RecordScreen(Screen):
    """Screen for recording RF signals"""

    CSS = """
    RecordScreen {
        background: #000000;
        color: #00ff00;
    }

    #record-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    #control-panel {
        width: 40%;
        padding: 0 1;
    }

    #signal-display {
        width: 60%;
        padding: 0 1;
    }

    .panel-border {
        color: #00aa00;
    }

    .input-group {
        height: 3;
        margin: 1 0;
    }

    Input {
        background: #001100;
        color: #00ff00;
        border: solid #00aa00;
    }

    Input:focus {
        border: solid #00ff00;
        background: #003300;
        color: #00ffff;
        text-style: bold;
    }

    Button {
        background: #003300;
        color: #00ff00;
        border: solid #00aa00;
        min-width: 16;
        margin: 0 1;
    }

    Button:hover {
        background: #004400;
        color: #00ffff;
        text-style: bold;
    }

    Button:focus {
        background: #004400;
        color: #00ffff;
        border: solid #00ff00;
        text-style: bold reverse;
    }

    Button.danger {
        background: #330000;
        border: solid #aa0000;
        color: #ff0000;
    }

    Button.danger:hover {
        background: #440000;
        color: #ff3333;
    }

    Button.danger:focus {
        background: #440000;
        color: #ff3333;
        border: solid #ff0000;
        text-style: bold reverse;
    }

    #signal-info {
        height: auto;
        color: #00ff00;
        margin: 1 0;
    }

    #capture-log {
        height: 100%;
        color: #00ff00;
        overflow-y: scroll;
    }

    .status-active {
        color: #00ffff;
        text-style: bold;
    }

    .status-idle {
        color: #00aa00;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back to Home"),
        Binding("space", "toggle_record", "Start/Stop"),
        Binding("ctrl+s", "save_signal", "Save"),
        Binding("down", "focus_next", "Next", show=False),
        Binding("up", "focus_previous", "Previous", show=False),
    ]

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.recording = False
        self.last_signal = None
        self.log_messages = []

    def compose(self) -> ComposeResult:
        with Container(id="record-container"):
            yield Static("┌─ RECORD MODE ──────────────────────────────────────────────┐", classes="panel-border")

            with Horizontal():
                # Control panel
                with Vertical(id="control-panel"):
                    yield Static("┌─ CONFIGURATION ────────────────┐", classes="panel-border")

                    with Container(classes="input-group"):
                        yield Label("Frequency (MHz):")
                        yield Input(value="433.92", id="freq-input")

                    with Container(classes="input-group"):
                        yield Label("Modulation:")
                        yield Input(value="ASK", id="mod-input")

                    with Container(classes="input-group"):
                        yield Label("RX Bandwidth (kHz):")
                        yield Input(value="812", id="bw-input")

                    yield Static("└────────────────────────────────┘", classes="panel-border")
                    yield Static("")

                    # Control buttons
                    yield Static("┌─ CONTROLS ─────────────────────┐", classes="panel-border")
                    with Horizontal():
                        yield Button("START RX", id="btn-start", variant="success")
                        yield Button("STOP", id="btn-stop", classes="danger")
                    yield Static("")
                    with Horizontal():
                        yield Button("SAVE", id="btn-save")
                        yield Button("CLEAR", id="btn-clear")
                    yield Static("└────────────────────────────────┘", classes="panel-border")

                    # Status
                    yield Static("")
                    yield Static("┌─ STATUS ───────────────────────┐", classes="panel-border")
                    yield Label("IDLE", id="rx-status", classes="status-idle")
                    yield Static("└────────────────────────────────┘", classes="panel-border")

                # Signal display
                with Vertical(id="signal-display"):
                    yield Static("┌─ CAPTURED SIGNALS ─────────────────────────────┐", classes="panel-border")
                    yield Label(id="signal-info")
                    yield Static("├────────────────────────────────────────────────┤", classes="panel-border")
                    yield Label(id="capture-log", classes="capture-log")
                    yield Static("└────────────────────────────────────────────────┘", classes="panel-border")

            yield Static("└────────────────────────────────────────────────────────────┘", classes="panel-border")
            yield Static("↑↓:Navigate  SPACE:Start/Stop  CTRL+S:Save  ESC:Back", classes="panel-border")

    def on_mount(self) -> None:
        """Focus first button when screen opens"""
        self.query_one("#btn-start", Button).focus()

    def action_focus_next(self) -> None:
        """Move focus to next focusable widget"""
        self.focus_next()

    def action_focus_previous(self) -> None:
        """Move focus to previous focusable widget"""
        self.focus_previous()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "btn-start":
            self.action_toggle_record()
        elif button_id == "btn-stop":
            self.stop_recording()
        elif button_id == "btn-save":
            self.action_save_signal()
        elif button_id == "btn-clear":
            self.clear_log()

    def action_toggle_record(self):
        """Toggle recording on/off"""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start RX recording"""
        freq_input = self.query_one("#freq-input", Input)
        mod_input = self.query_one("#mod-input", Input)
        bw_input = self.query_one("#bw-input", Input)

        try:
            freq = float(freq_input.value)

            # Configure RX
            self.client.rx_config(
                module=1,
                frequency_mhz=freq,
                modulation=2  # ASK/OOK
            )

            # Start RX
            self.client.rx_start(module=1)

            self.recording = True
            status = self.query_one("#rx-status", Label)
            status.update(f"● RECORDING @ {freq:.2f} MHz")
            status.set_classes("status-active")

            self.add_log(f"[RX STARTED] {freq:.2f} MHz")

        except Exception as e:
            self.add_log(f"[ERROR] {e}")

    def stop_recording(self):
        """Stop RX recording"""
        if self.recording:
            self.client.rx_stop()
            self.recording = False

            status = self.query_one("#rx-status", Label)
            status.update("IDLE")
            status.set_classes("status-idle")

            self.add_log("[RX STOPPED]")

    def action_save_signal(self):
        """Save last captured signal"""
        if self.last_signal:
            # TODO: Implement save to file
            self.add_log("[SAVED] signal_001.raw")
        else:
            self.add_log("[ERROR] No signal to save")

    def clear_log(self):
        """Clear capture log"""
        self.log_messages = []
        log = self.query_one("#capture-log", Label)
        log.update("")

    def add_log(self, message: str):
        """Add message to capture log"""
        self.log_messages.append(message)
        log = self.query_one("#capture-log", Label)
        log.update("\n".join(self.log_messages[-20:]))  # Keep last 20 messages

    def on_signal_received(self, data: dict):
        """Handle signal received event from serial client"""
        samples = len(data.get('raw_timings_us', []))
        rssi = data.get('rssi_dbm', -100)

        self.last_signal = data

        # Update signal info
        info = self.query_one("#signal-info", Label)
        info.update(f"""Last Signal:
  Samples: {samples}
  RSSI: {rssi} dBm
  Protocol: {data.get('protocol', 'Unknown')}""")

        self.add_log(f"[SIGNAL] {samples} samples @ {rssi} dBm")

    def action_back(self):
        """Return to home screen"""
        self.stop_recording()
        self.app.pop_screen()

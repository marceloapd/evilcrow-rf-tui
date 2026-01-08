"""
Transmit Screen - Replay captured signals
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input, ListView, ListItem
from textual.binding import Binding


class TransmitScreen(Screen):
    """Screen for transmitting RF signals"""

    CSS = """
    TransmitScreen {
        background: #000000;
        color: #00ff00;
    }

    #transmit-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    #left-panel {
        width: 50%;
        padding: 0 1;
    }

    #right-panel {
        width: 50%;
        padding: 0 1;
    }

    .panel-border {
        color: #00aa00;
    }

    #saved-signals {
        height: 10;
        border: none;
        background: #000000;
    }

    #saved-signals > ListItem {
        height: 1;
        background: #000000;
        color: #00ff00;
    }

    #saved-signals > ListItem:hover, #saved-signals > .list--highlight {
        background: #003300 !important;
        color: #00ffff;
        text-style: bold reverse;
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
        min-width: 12;
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

    Button.primary {
        background: #003300;
        border: solid #00ff00;
        color: #00ffff;
        text-style: bold;
    }

    Button.primary:hover {
        background: #004400;
        text-style: bold;
    }

    Button.primary:focus {
        background: #004400;
        border: solid #00ff00;
        text-style: bold reverse;
    }

    #signal-info {
        height: auto;
        color: #00ff00;
    }

    #tx-log {
        height: 100%;
        color: #00ff00;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back to Home"),
        Binding("space", "transmit", "Transmit"),
        Binding("ctrl+l", "load", "Load"),
        Binding("down", "focus_next", "Next", show=False),
        Binding("up", "focus_previous", "Previous", show=False),
    ]

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.selected_signal = None
        self.signal_data = None
        self.log_messages = []

    def compose(self) -> ComposeResult:
        with Container(id="transmit-container"):
            yield Static("┌─ TRANSMIT MODE ────────────────────────────────────────────┐", classes="panel-border")

            with Horizontal():
                # Left panel - Signals and controls
                with Vertical(id="left-panel"):
                    yield Static("┌─ SAVED SIGNALS ────────────────┐", classes="panel-border")
                    with ListView(id="saved-signals"):
                        # TODO: Load from storage
                        yield ListItem(Label("keyfob_001.raw   433.92 MHz"))
                        yield ListItem(Label("garage_door.raw  315.00 MHz"))
                        yield ListItem(Label("car_unlock.raw   433.92 MHz"))
                        yield ListItem(Label("remote_001.raw   868.00 MHz"))
                    yield Static("└────────────────────────────────┘", classes="panel-border")

                    yield Static("")
                    with Horizontal():
                        yield Button("LOAD", id="btn-load")
                        yield Button("DELETE", id="btn-delete")

                    yield Static("")
                    yield Static("┌─ TX CONFIG ────────────────────┐", classes="panel-border")

                    with Container(classes="input-group"):
                        yield Label("Repeat Count:")
                        yield Input(value="5", id="repeat-input")

                    with Container(classes="input-group"):
                        yield Label("Power (dBm):")
                        yield Input(value="10", id="power-input")

                    yield Static("└────────────────────────────────┘", classes="panel-border")

                    yield Static("")
                    yield Static("┌─ CONTROLS ─────────────────────┐", classes="panel-border")
                    with Horizontal():
                        yield Button("TRANSMIT", id="btn-transmit", classes="primary")
                        yield Button("TEST", id="btn-test")
                    yield Static("└────────────────────────────────┘", classes="panel-border")

                # Right panel - Signal info and log
                with Vertical(id="right-panel"):
                    yield Static("┌─ LOADED SIGNAL ────────────────┐", classes="panel-border")
                    yield Label("No signal loaded", id="signal-info")
                    yield Static("└────────────────────────────────┘", classes="panel-border")

                    yield Static("")
                    yield Static("┌─ TX LOG ───────────────────────┐", classes="panel-border")
                    yield Label("", id="tx-log")
                    yield Static("└────────────────────────────────┘", classes="panel-border")

            yield Static("└────────────────────────────────────────────────────────────┘", classes="panel-border")
            yield Static("↑↓:Navigate  SPACE:Transmit  CTRL+L:Load  ESC:Back", classes="panel-border")

    def on_mount(self) -> None:
        """Focus signal list when screen opens"""
        self.query_one("#saved-signals", ListView).focus()

    def action_focus_next(self) -> None:
        """Move focus to next focusable widget"""
        self.focus_next()

    def action_focus_previous(self) -> None:
        """Move focus to previous focusable widget"""
        self.focus_previous()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "btn-load":
            self.action_load()
        elif button_id == "btn-delete":
            self.delete_signal()
        elif button_id == "btn-transmit":
            self.action_transmit()
        elif button_id == "btn-test":
            self.test_signal()

    def action_load(self):
        """Load selected signal"""
        # TODO: Load from storage
        self.selected_signal = "keyfob_001.raw"
        self.signal_data = {
            'frequency_mhz': 433.92,
            'timings_us': [450, 1200, 450, 1200, 450, 900, 450, 900] * 10,
            'protocol': 'Unknown'
        }

        # Update info
        info = self.query_one("#signal-info", Label)
        info.update(f"""Signal: {self.selected_signal}
Frequency: {self.signal_data['frequency_mhz']} MHz
Samples: {len(self.signal_data['timings_us'])}""")

        self.add_log(f"[LOADED] {self.selected_signal}")

    def action_transmit(self):
        """Transmit loaded signal"""
        if not self.signal_data:
            self.add_log("[ERROR] No signal loaded")
            return

        repeat_input = self.query_one("#repeat-input", Input)

        try:
            repeat = int(repeat_input.value)

            # Send TX command
            self.client.tx_send(
                timings_us=self.signal_data['timings_us'],
                module=1,
                repeat=repeat
            )

            self.add_log(f"[TX] Sent {repeat}x @ {self.signal_data['frequency_mhz']} MHz")

        except Exception as e:
            self.add_log(f"[ERROR] {e}")

    def test_signal(self):
        """Test signal with single transmission"""
        if not self.signal_data:
            self.add_log("[ERROR] No signal loaded")
            return

        try:
            self.client.tx_send(
                timings_us=self.signal_data['timings_us'],
                module=1,
                repeat=1
            )

            self.add_log("[TEST] Sent 1x")

        except Exception as e:
            self.add_log(f"[ERROR] {e}")

    def delete_signal(self):
        """Delete selected signal"""
        # TODO: Implement delete from storage
        self.add_log("[TODO] Delete not implemented yet")

    def add_log(self, message: str):
        """Add message to TX log"""
        self.log_messages.append(message)
        log = self.query_one("#tx-log", Label)
        log.update("\n".join(self.log_messages[-15:]))  # Keep last 15 messages

    def action_back(self):
        """Return to home screen"""
        self.app.pop_screen()

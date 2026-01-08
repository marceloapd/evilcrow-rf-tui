"""
Jammer Screen - RF Jamming
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, Center
from textual.widgets import Static, Label, Button, Input
from textual.binding import Binding


class JammerScreen(Screen):
    """Screen for RF jamming operations"""

    CSS = """
    JammerScreen {
        background: #000000;
        color: #00ff00;
    }

    #jammer-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
        overflow-y: auto;
    }

    .panel-border {
        color: #00aa00;
    }

    .warning {
        color: #ffaa00;
    }

    .input-group {
        height: auto;
        margin: 0 0 1 2;
    }

    Input {
        background: #001100;
        color: #00ff00;
        border: solid #00aa00;
        width: 30;
        margin: 0 0 0 2;
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
        text-style: bold;
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

    Button.preset {
        background: #002200;
        border: solid #00aa00;
        min-width: 10;
        margin: 0 1;
    }

    Button.preset:hover {
        background: #003300;
        color: #00ffff;
    }

    Button.preset:focus {
        background: #003300;
        color: #00ffff;
        border: solid #00ff00;
        text-style: bold reverse;
    }

    #jammer-status {
        height: auto;
        color: #00ff00;
        margin: 0 2;
    }

    .status-active {
        color: #ff0000;
        text-style: bold;
    }

    .status-idle {
        color: #00aa00;
    }

    #preset-buttons {
        width: 100%;
        height: auto;
        padding: 0 2;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back to Home"),
        Binding("space", "toggle_jammer", "Start/Stop"),
        Binding("ctrl+c", "emergency_stop", "Emergency Stop"),
        Binding("down", "focus_next", "Next", show=False),
        Binding("up", "focus_previous", "Previous", show=False),
    ]

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.jamming = False

    def compose(self) -> ComposeResult:
        with Container(id="jammer-container"):
            yield Static("┌─ JAMMER MODE ──────────────────────────────────────────────┐", classes="panel-border")
            yield Static("│ ⚠️  WARNING: RF jamming may be illegal! Use only in       │", classes="warning")
            yield Static("│     authorized environments for testing purposes!         │", classes="warning")
            yield Static("└────────────────────────────────────────────────────────────┘", classes="panel-border")

            yield Static("")
            yield Static("┌─ CONFIGURATION ────────────────────────────────────────────┐", classes="panel-border")

            with Container(classes="input-group"):
                yield Label("  Target Frequency (MHz):")
                yield Input(value="433.92", id="freq-input")

            with Container(classes="input-group"):
                yield Label("  Power Level (dBm):")
                yield Input(value="10", id="power-input")

            yield Static("")
            yield Static("  Common Frequencies:", classes="panel-border")

            with Horizontal(id="preset-buttons"):
                yield Button("315", id="preset-315", classes="preset")
                yield Button("433", id="preset-433", classes="preset")
                yield Button("868", id="preset-868", classes="preset")
                yield Button("915", id="preset-915", classes="preset")

            yield Static("└────────────────────────────────────────────────────────────┘", classes="panel-border")

            yield Static("")
            yield Static("┌─ STATUS ───────────────────────────────────────────────────┐", classes="panel-border")
            yield Label("  IDLE", id="jammer-status", classes="status-idle")
            yield Static("└────────────────────────────────────────────────────────────┘", classes="panel-border")

            yield Static("")
            yield Static("┌─ CONTROLS ─────────────────────────────────────────────────┐", classes="panel-border")

            with Horizontal():
                yield Button("START JAMMING", id="btn-start")
                yield Button("STOP", id="btn-stop", classes="danger")

            yield Static("└────────────────────────────────────────────────────────────┘", classes="panel-border")
            yield Static("↑↓:Navigate  SPACE:Start/Stop  CTRL+C:Emergency  ESC:Back", classes="panel-border")

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
            self.action_toggle_jammer()
        elif button_id == "btn-stop":
            self.stop_jammer()
        elif button_id.startswith("preset-"):
            freq = button_id.split("-")[1]
            freq_input = self.query_one("#freq-input", Input)
            freq_input.value = f"{freq}.00"

    def action_toggle_jammer(self):
        """Toggle jammer on/off"""
        if not self.jamming:
            self.start_jammer()
        else:
            self.stop_jammer()

    def start_jammer(self):
        """Start RF jammer"""
        freq_input = self.query_one("#freq-input", Input)
        power_input = self.query_one("#power-input", Input)

        try:
            freq = float(freq_input.value)
            power = int(power_input.value)

            # Start jammer
            self.client.jammer_start(
                frequency_mhz=freq,
                module=1,
                power_dbm=power
            )

            self.jamming = True
            status = self.query_one("#jammer-status", Label)
            status.update(f"  ● JAMMING ACTIVE @ {freq:.2f} MHz (Power: {power} dBm)")
            status.set_classes("status-active")

        except Exception as e:
            status = self.query_one("#jammer-status", Label)
            status.update(f"ERROR: {e}")

    def stop_jammer(self):
        """Stop RF jammer"""
        if self.jamming:
            self.client.jammer_stop()
            self.jamming = False

            status = self.query_one("#jammer-status", Label)
            status.update("  IDLE")
            status.set_classes("status-idle")

    def action_emergency_stop(self):
        """Emergency stop jammer"""
        self.stop_jammer()
        self.app.notify("[ EMERGENCY STOP EXECUTED ]", severity="error", timeout=2)

    def action_back(self):
        """Return to home screen"""
        self.stop_jammer()
        self.app.pop_screen()

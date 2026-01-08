"""
Serial client for communicating with Evil Crow RF V2
"""
import serial
import json
import threading
import queue
import time
from typing import Callable, Optional, Dict, Any


class SerialClient:
    """Serial client for Evil Crow RF V2"""

    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 115200):
        self.port = port
        self.baud = baud
        self.ser: Optional[serial.Serial] = None
        self.running = False
        self.read_thread: Optional[threading.Thread] = None
        self.command_id = 0
        self.callbacks: Dict[int, Callable] = {}
        self.event_callbacks: Dict[str, list] = {}
        self.response_queue = queue.Queue()

    def connect(self) -> bool:
        """Connect to device"""
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.5)
            time.sleep(0.5)  # Wait for device to be ready (reduzido de 2s)
            self.ser.reset_input_buffer()

            # Start read thread
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()

            return True
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from device"""
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=2)
        if self.ser:
            self.ser.close()

    def is_connected(self) -> bool:
        """Check if device is still connected"""
        return self.running and self.ser is not None and self.ser.is_open

    def _read_loop(self):
        """Background thread to read serial data"""
        while self.running and self.ser:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        self._handle_message(line)
            except (serial.SerialException, OSError) as e:
                # Device disconnected
                print(f"Device disconnected: {e}")
                self.running = False
                if self.ser:
                    try:
                        self.ser.close()
                    except:
                        pass
                self.ser = None
                break
            except Exception as e:
                print(f"Read error: {e}")
                time.sleep(0.1)

    def _handle_message(self, message: str):
        """Handle incoming message"""
        try:
            data = json.loads(message)

            # Check if it's an event
            if data.get('type') == 'event':
                event_name = data.get('event')
                if event_name and event_name in self.event_callbacks:
                    for callback in self.event_callbacks[event_name]:
                        callback(data.get('data', {}))
            else:
                # It's a command response
                cmd_id = data.get('id')
                if cmd_id and cmd_id in self.callbacks:
                    callback = self.callbacks.pop(cmd_id)
                    callback(data)
                else:
                    # Put in queue for synchronous calls
                    self.response_queue.put(data)

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")

    def send_command(self, cmd: str, params: Optional[Dict] = None,
                    callback: Optional[Callable] = None) -> Optional[Dict]:
        """
        Send command to device

        Args:
            cmd: Command name
            params: Command parameters
            callback: Optional callback for async response

        Returns:
            Response dict if no callback provided, None otherwise
        """
        if not self.ser:
            return None

        self.command_id += 1
        cmd_id = self.command_id

        # Build command
        command = {"cmd": cmd, "id": cmd_id}
        if params:
            command["params"] = params

        # Register callback if provided
        if callback:
            self.callbacks[cmd_id] = callback

        # Send command
        try:
            self.ser.write((json.dumps(command) + '\n').encode('utf-8'))
        except (serial.SerialException, OSError) as e:
            # Device disconnected during send
            print(f"Device disconnected during send: {e}")
            self.running = False
            if self.ser:
                try:
                    self.ser.close()
                except:
                    pass
            self.ser = None
            return None
        except Exception as e:
            print(f"Send error: {e}")
            return None

        # If no callback, wait for response
        if not callback:
            try:
                response = self.response_queue.get(timeout=5)
                return response
            except queue.Empty:
                return None

        return None

    def on_event(self, event_name: str, callback: Callable):
        """Register event callback"""
        if event_name not in self.event_callbacks:
            self.event_callbacks[event_name] = []
        self.event_callbacks[event_name].append(callback)

    # Convenience methods for common commands
    def ping(self) -> Optional[Dict]:
        """Send ping command"""
        return self.send_command('ping')

    def get_status(self) -> Optional[Dict]:
        """Get device status"""
        return self.send_command('get_status')

    def rx_config(self, module: int = 1, frequency_mhz: float = 433.92,
                  modulation: int = 2) -> Optional[Dict]:
        """Configure RX"""
        return self.send_command('rx_config', {
            'module': module,
            'frequency_mhz': frequency_mhz,
            'modulation': modulation
        })

    def rx_start(self, module: int = 1) -> Optional[Dict]:
        """Start RX"""
        return self.send_command('rx_start', {'module': module})

    def rx_stop(self) -> Optional[Dict]:
        """Stop RX"""
        return self.send_command('rx_stop')

    def tx_send(self, timings_us: list, module: int = 1, repeat: int = 1) -> Optional[Dict]:
        """Transmit signal"""
        return self.send_command('tx_send', {
            'module': module,
            'timings_us': timings_us,
            'repeat': repeat
        })

    def jammer_start(self, frequency_mhz: float = 433.92, module: int = 1,
                     power_dbm: int = 10) -> Optional[Dict]:
        """Start jammer"""
        return self.send_command('jammer_start', {
            'module': module,
            'frequency_mhz': frequency_mhz,
            'power_dbm': power_dbm
        })

    def jammer_stop(self) -> Optional[Dict]:
        """Stop jammer"""
        return self.send_command('jammer_stop')

    def scan_start(self, start_mhz: float = 300.0, end_mhz: float = 928.0,
                   step_khz: float = 100.0, threshold_dbm: int = -80,
                   module: int = 1) -> Optional[Dict]:
        """Start frequency scan"""
        return self.send_command('scan_start', {
            'module': module,
            'start_mhz': start_mhz,
            'end_mhz': end_mhz,
            'step_khz': step_khz,
            'threshold_dbm': threshold_dbm
        })

    def get_spectrum(self, center_mhz: float = 433.92, span_mhz: float = 10.0,
                     points: int = 50, module: int = 1) -> Optional[Dict]:
        """Get spectrum data"""
        return self.send_command('get_spectrum', {
            'module': module,
            'center_mhz': center_mhz,
            'span_mhz': span_mhz,
            'points': points
        })

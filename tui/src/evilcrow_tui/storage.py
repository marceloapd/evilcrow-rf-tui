"""
Storage Manager for Evil Crow RF V2
Handles file operations in ~/.evilcrow/
"""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime


class StorageManager:
    """Manages local storage for signals, logs, and configuration"""

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize storage manager

        Args:
            base_dir: Base directory for storage (default: ~/.evilcrow/)
        """
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path.home() / '.evilcrow'

        # Create directory structure
        self.signals_dir = self.base_dir / 'signals'
        self.raw_dir = self.signals_dir / 'raw'
        self.bin_dir = self.signals_dir / 'bin'
        self.sub_dir = self.signals_dir / 'sub'
        self.urh_dir = self.signals_dir / 'urh'
        self.logs_dir = self.base_dir / 'logs'
        self.presets_dir = self.base_dir / 'presets'
        self.config_file = self.base_dir / 'config.json'

        self._ensure_directories()
        self._load_config()

    def _ensure_directories(self):
        """Create directory structure if it doesn't exist"""
        for directory in [
            self.base_dir,
            self.signals_dir,
            self.raw_dir,
            self.bin_dir,
            self.sub_dir,
            self.urh_dir,
            self.logs_dir,
            self.presets_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        """Load configuration file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                'serial_port': '/dev/ttyUSB0',
                'baud_rate': 115200,
                'auto_save_captures': True,
                'default_format': 'raw',
                'theme': 'dark',
                'confirm_before_jamming': True,
                'confirm_before_attacks': True,
                'max_tx_power_dbm': 10
            }
            self.save_config()

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_config(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set_config(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()

    # Signal Management
    def save_signal(self, name: str, data: Dict, format: str = 'raw') -> bool:
        """
        Save signal to file

        Args:
            name: Signal name (without extension)
            data: Signal data dictionary
            format: File format ('raw', 'bin', 'sub', 'urh')

        Returns:
            True if successful
        """
        try:
            if format == 'raw':
                file_path = self.raw_dir / f"{name}.json"
                # Add metadata
                signal_data = {
                    'name': name,
                    'timestamp': datetime.now().isoformat(),
                    **data
                }
                with open(file_path, 'w') as f:
                    json.dump(signal_data, f, indent=2)

            elif format == 'bin':
                file_path = self.bin_dir / f"{name}.bin"
                # Binary format will be implemented in signal_formats.py
                # For now, just save as JSON
                with open(file_path, 'wb') as f:
                    f.write(json.dumps(data).encode())

            elif format == 'sub':
                file_path = self.sub_dir / f"{name}.sub"
                # Flipper Zero format will be implemented in signal_formats.py
                with open(file_path, 'w') as f:
                    f.write(f"# Signal: {name}\n")
                    f.write(json.dumps(data))

            elif format == 'urh':
                file_path = self.urh_dir / f"{name}.complex"
                # URH format will be implemented in signal_formats.py
                with open(file_path, 'wb') as f:
                    f.write(b'')  # Placeholder

            else:
                raise ValueError(f"Unknown format: {format}")

            return True

        except Exception as e:
            print(f"Error saving signal: {e}")
            return False

    def load_signal(self, name: str, format: str = 'raw') -> Optional[Dict]:
        """
        Load signal from file

        Args:
            name: Signal name (without extension)
            format: File format ('raw', 'bin', 'sub', 'urh')

        Returns:
            Signal data dictionary or None
        """
        try:
            if format == 'raw':
                file_path = self.raw_dir / f"{name}.json"
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        return json.load(f)

            elif format == 'bin':
                file_path = self.bin_dir / f"{name}.bin"
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        data = f.read()
                        return json.loads(data.decode())

            elif format == 'sub':
                file_path = self.sub_dir / f"{name}.sub"
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        # Skip comment line
                        f.readline()
                        return json.loads(f.read())

            elif format == 'urh':
                file_path = self.urh_dir / f"{name}.complex"
                if file_path.exists():
                    # URH loading will be implemented in signal_formats.py
                    return None

            return None

        except Exception as e:
            print(f"Error loading signal: {e}")
            return None

    def list_signals(self, format: Optional[str] = None) -> List[Dict]:
        """
        List all saved signals

        Args:
            format: Filter by format (None = all formats)

        Returns:
            List of signal info dictionaries
        """
        signals = []

        formats_to_check = {
            'raw': (self.raw_dir, '.json'),
            'bin': (self.bin_dir, '.bin'),
            'sub': (self.sub_dir, '.sub'),
            'urh': (self.urh_dir, '.complex')
        }

        if format:
            formats_to_check = {format: formats_to_check[format]}

        for fmt, (directory, extension) in formats_to_check.items():
            for file_path in directory.glob(f"*{extension}"):
                signals.append({
                    'name': file_path.stem,
                    'format': fmt,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })

        # Sort by modification time (newest first)
        signals.sort(key=lambda x: x['modified'], reverse=True)
        return signals

    def delete_signal(self, name: str, format: str = 'raw') -> bool:
        """
        Delete signal file

        Args:
            name: Signal name
            format: File format

        Returns:
            True if successful
        """
        try:
            formats_map = {
                'raw': (self.raw_dir, '.json'),
                'bin': (self.bin_dir, '.bin'),
                'sub': (self.sub_dir, '.sub'),
                'urh': (self.urh_dir, '.complex')
            }

            directory, extension = formats_map[format]
            file_path = directory / f"{name}{extension}"

            if file_path.exists():
                file_path.unlink()
                return True
            return False

        except Exception as e:
            print(f"Error deleting signal: {e}")
            return False

    def signal_exists(self, name: str, format: str = 'raw') -> bool:
        """Check if signal exists"""
        formats_map = {
            'raw': (self.raw_dir, '.json'),
            'bin': (self.bin_dir, '.bin'),
            'sub': (self.sub_dir, '.sub'),
            'urh': (self.urh_dir, '.complex')
        }

        directory, extension = formats_map[format]
        file_path = directory / f"{name}{extension}"
        return file_path.exists()

    # Logging
    def log_activity(self, message: str, level: str = 'info'):
        """
        Log activity to file

        Args:
            message: Log message
            level: Log level ('info', 'warning', 'error')
        """
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"

        # Log to daily file
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

        try:
            with open(log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing log: {e}")

    def get_logs(self, date: Optional[str] = None) -> List[str]:
        """
        Get logs for a specific date

        Args:
            date: Date in YYYY-MM-DD format (None = today)

        Returns:
            List of log entries
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        log_file = self.logs_dir / f"{date}.log"

        if log_file.exists():
            with open(log_file, 'r') as f:
                return f.readlines()
        return []

    # Presets
    def save_preset(self, name: str, preset: Dict) -> bool:
        """Save RF configuration preset"""
        try:
            preset_file = self.presets_dir / f"{name}.json"
            with open(preset_file, 'w') as f:
                json.dump(preset, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving preset: {e}")
            return False

    def load_preset(self, name: str) -> Optional[Dict]:
        """Load RF configuration preset"""
        try:
            preset_file = self.presets_dir / f"{name}.json"
            if preset_file.exists():
                with open(preset_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading preset: {e}")
            return None

    def list_presets(self) -> List[str]:
        """List all saved presets"""
        return [p.stem for p in self.presets_dir.glob('*.json')]

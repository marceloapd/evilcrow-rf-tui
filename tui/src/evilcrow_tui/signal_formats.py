"""
Signal Format Converters for Evil Crow RF V2
Supports: RAW (JSON), BIN (binary), SUB (Flipper Zero), URH (Universal Radio Hacker)
"""
import json
import struct
from typing import Dict, List, Optional
from datetime import datetime


class SignalFormats:
    """Signal format converters"""

    @staticmethod
    def to_raw(signal_data: Dict) -> str:
        """
        Convert to RAW format (JSON)

        Format:
        {
          "name": "signal_name",
          "timestamp": "2024-01-07T12:34:56",
          "frequency_mhz": 433.92,
          "modulation": "ASK",
          "sample_rate": 250000,
          "timings_us": [450, 1200, 450, 1200, ...],
          "protocol": "unknown",
          "rssi_dbm": -45
        }

        Args:
            signal_data: Signal data dictionary

        Returns:
            JSON string
        """
        raw_data = {
            'name': signal_data.get('name', 'unknown'),
            'timestamp': signal_data.get('timestamp', datetime.now().isoformat()),
            'frequency_mhz': signal_data.get('frequency_mhz', 433.92),
            'modulation': signal_data.get('modulation', 'ASK'),
            'sample_rate': signal_data.get('sample_rate', 250000),
            'timings_us': signal_data.get('timings_us', []),
            'protocol': signal_data.get('protocol', 'unknown'),
            'rssi_dbm': signal_data.get('rssi_dbm', -100)
        }

        return json.dumps(raw_data, indent=2)

    @staticmethod
    def from_raw(raw_json: str) -> Dict:
        """
        Parse RAW format (JSON)

        Args:
            raw_json: JSON string

        Returns:
            Signal data dictionary
        """
        return json.loads(raw_json)

    @staticmethod
    def to_bin(signal_data: Dict) -> bytes:
        """
        Convert to BIN format (custom binary)

        Binary Format:
        - Header: "ECRF" (4 bytes)
        - Version: 0x02 (1 byte)
        - Frequency: float (4 bytes)
        - Modulation: uint8 (1 byte) - 0=ASK, 1=FSK, 2=GFSK
        - Sample Rate: uint32 (4 bytes)
        - RSSI: int8 (1 byte)
        - Timing Count: uint32 (4 bytes)
        - Timings: array of uint32 (4 bytes each)

        Args:
            signal_data: Signal data dictionary

        Returns:
            Binary data
        """
        # Modulation mapping
        mod_map = {'ASK': 0, 'OOK': 0, 'FSK': 1, 'GFSK': 2, '2-FSK': 1, '4-FSK': 1}
        modulation = signal_data.get('modulation', 'ASK')
        mod_byte = mod_map.get(modulation, 0)

        # Build binary data
        data = bytearray()

        # Header
        data.extend(b'ECRF')

        # Version
        data.append(0x02)

        # Frequency (float32)
        data.extend(struct.pack('<f', signal_data.get('frequency_mhz', 433.92)))

        # Modulation (uint8)
        data.append(mod_byte)

        # Sample Rate (uint32)
        data.extend(struct.pack('<I', signal_data.get('sample_rate', 250000)))

        # RSSI (int8)
        rssi = max(-128, min(127, signal_data.get('rssi_dbm', -100)))
        data.extend(struct.pack('<b', rssi))

        # Timings
        timings = signal_data.get('timings_us', [])
        data.extend(struct.pack('<I', len(timings)))

        for timing in timings:
            # Convert to uint32 (max ~4.2 seconds per pulse)
            timing_val = max(0, min(4294967295, int(timing)))
            data.extend(struct.pack('<I', timing_val))

        return bytes(data)

    @staticmethod
    def from_bin(bin_data: bytes) -> Dict:
        """
        Parse BIN format

        Args:
            bin_data: Binary data

        Returns:
            Signal data dictionary
        """
        if len(bin_data) < 19:
            raise ValueError("Invalid BIN data: too short")

        # Check header
        if bin_data[0:4] != b'ECRF':
            raise ValueError("Invalid BIN header")

        # Parse header
        version = bin_data[4]
        frequency_mhz = struct.unpack('<f', bin_data[5:9])[0]
        mod_byte = bin_data[9]
        sample_rate = struct.unpack('<I', bin_data[10:14])[0]
        rssi_dbm = struct.unpack('<b', bin_data[14:15])[0]
        timing_count = struct.unpack('<I', bin_data[15:19])[0]

        # Modulation mapping
        mod_map = {0: 'ASK', 1: 'FSK', 2: 'GFSK'}
        modulation = mod_map.get(mod_byte, 'ASK')

        # Parse timings
        timings = []
        offset = 19
        for i in range(timing_count):
            if offset + 4 > len(bin_data):
                break
            timing = struct.unpack('<I', bin_data[offset:offset+4])[0]
            timings.append(timing)
            offset += 4

        return {
            'version': version,
            'frequency_mhz': frequency_mhz,
            'modulation': modulation,
            'sample_rate': sample_rate,
            'rssi_dbm': rssi_dbm,
            'timings_us': timings
        }

    @staticmethod
    def to_sub(signal_data: Dict) -> str:
        """
        Convert to SUB format (Flipper Zero)

        Flipper Zero .sub Format:
        Filetype: Flipper SubGhz RAW File
        Version: 1
        Frequency: 433920000
        Preset: FuriHalSubGhzPresetOok650Async
        Protocol: RAW
        RAW_Data: 450 -1200 450 -1200 ...

        Note: Positive values = HIGH, negative = LOW (duration in microseconds)

        Args:
            signal_data: Signal data dictionary

        Returns:
            SUB format string
        """
        # Frequency in Hz
        freq_hz = int(signal_data.get('frequency_mhz', 433.92) * 1_000_000)

        # Preset based on modulation
        modulation = signal_data.get('modulation', 'ASK')
        if modulation in ['ASK', 'OOK']:
            preset = 'FuriHalSubGhzPresetOok650Async'
        else:
            preset = 'FuriHalSubGhzPreset2FSKDev238Async'

        # Convert timings to Flipper format (alternating positive/negative)
        timings = signal_data.get('timings_us', [])
        raw_data_parts = []
        for i, timing in enumerate(timings):
            # Alternate between positive (HIGH) and negative (LOW)
            if i % 2 == 0:
                raw_data_parts.append(str(int(timing)))
            else:
                raw_data_parts.append(str(-int(timing)))

        raw_data = ' '.join(raw_data_parts)

        # Build SUB file content
        sub_content = f"""Filetype: Flipper SubGhz RAW File
Version: 1
Frequency: {freq_hz}
Preset: {preset}
Protocol: RAW
RAW_Data: {raw_data}
"""

        return sub_content

    @staticmethod
    def from_sub(sub_content: str) -> Dict:
        """
        Parse SUB format (Flipper Zero)

        Args:
            sub_content: SUB file content

        Returns:
            Signal data dictionary
        """
        lines = sub_content.strip().split('\n')
        data = {}

        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key == 'Frequency':
                    # Convert Hz to MHz
                    data['frequency_mhz'] = int(value) / 1_000_000

                elif key == 'Preset':
                    # Determine modulation from preset
                    if 'Ook' in value or 'ASK' in value:
                        data['modulation'] = 'ASK'
                    elif 'FSK' in value:
                        data['modulation'] = 'FSK'
                    else:
                        data['modulation'] = 'ASK'

                elif key == 'RAW_Data':
                    # Parse timings (convert negatives to absolute values)
                    timing_strings = value.split()
                    timings = []
                    for t_str in timing_strings:
                        timings.append(abs(int(t_str)))
                    data['timings_us'] = timings

        return data

    @staticmethod
    def to_urh(signal_data: Dict) -> bytes:
        """
        Convert to URH format (Universal Radio Hacker)

        URH uses complex IQ samples stored as interleaved float32 values:
        [I0, Q0, I1, Q1, I2, Q2, ...]

        We convert timing data to simple OOK modulated IQ samples:
        - HIGH pulse: I=1.0, Q=0.0
        - LOW pulse: I=0.0, Q=0.0

        Args:
            signal_data: Signal data dictionary

        Returns:
            Binary IQ data (complex64 format)
        """
        timings = signal_data.get('timings_us', [])
        sample_rate = signal_data.get('sample_rate', 250000)

        iq_samples = []

        # Convert timings to IQ samples
        is_high = True
        for timing_us in timings:
            # Calculate number of samples for this pulse
            num_samples = int((timing_us / 1_000_000) * sample_rate)

            # Generate IQ values
            if is_high:
                i_val, q_val = 1.0, 0.0
            else:
                i_val, q_val = 0.0, 0.0

            # Add samples
            for _ in range(num_samples):
                iq_samples.append(i_val)
                iq_samples.append(q_val)

            is_high = not is_high

        # Pack as float32
        return struct.pack(f'<{len(iq_samples)}f', *iq_samples)

    @staticmethod
    def from_urh(iq_data: bytes, sample_rate: int = 250000) -> Dict:
        """
        Parse URH format (Universal Radio Hacker)

        Convert IQ samples back to timing data by detecting level transitions

        Args:
            iq_data: Binary IQ data (complex64 format)
            sample_rate: Sample rate in Hz

        Returns:
            Signal data dictionary
        """
        # Unpack IQ samples
        num_floats = len(iq_data) // 4
        iq_samples = struct.unpack(f'<{num_floats}f', iq_data)

        # Extract I channel and detect transitions
        timings = []
        current_level = None
        sample_count = 0

        for i in range(0, len(iq_samples), 2):
            i_val = iq_samples[i]

            # Determine level (threshold at 0.5)
            level = 1 if i_val > 0.5 else 0

            if current_level is None:
                current_level = level
                sample_count = 1
            elif level == current_level:
                sample_count += 1
            else:
                # Transition detected
                timing_us = int((sample_count / sample_rate) * 1_000_000)
                timings.append(timing_us)

                current_level = level
                sample_count = 1

        # Add final timing
        if sample_count > 0:
            timing_us = int((sample_count / sample_rate) * 1_000_000)
            timings.append(timing_us)

        return {
            'sample_rate': sample_rate,
            'timings_us': timings,
            'modulation': 'ASK'
        }

    @staticmethod
    def convert(signal_data: Dict, from_format: str, to_format: str) -> any:
        """
        Convert signal between formats

        Args:
            signal_data: Signal data (format depends on from_format)
            from_format: Source format ('raw', 'bin', 'sub', 'urh')
            to_format: Target format ('raw', 'bin', 'sub', 'urh')

        Returns:
            Converted data (type depends on to_format)
        """
        # First, normalize to dict if needed
        if from_format == 'raw' and isinstance(signal_data, str):
            data_dict = SignalFormats.from_raw(signal_data)
        elif from_format == 'bin' and isinstance(signal_data, bytes):
            data_dict = SignalFormats.from_bin(signal_data)
        elif from_format == 'sub' and isinstance(signal_data, str):
            data_dict = SignalFormats.from_sub(signal_data)
        elif from_format == 'urh' and isinstance(signal_data, bytes):
            data_dict = SignalFormats.from_urh(signal_data)
        else:
            data_dict = signal_data

        # Convert to target format
        if to_format == 'raw':
            return SignalFormats.to_raw(data_dict)
        elif to_format == 'bin':
            return SignalFormats.to_bin(data_dict)
        elif to_format == 'sub':
            return SignalFormats.to_sub(data_dict)
        elif to_format == 'urh':
            return SignalFormats.to_urh(data_dict)
        else:
            raise ValueError(f"Unknown target format: {to_format}")

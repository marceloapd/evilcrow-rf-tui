#ifndef CONFIG_H
#define CONFIG_H

// Firmware version
#define FIRMWARE_VERSION "2.0.0-tui"

// Serial configuration
#define SERIAL_BAUD 115200

// SPI Pins (shared between CC1101 modules)
#define SPI_SCK   14
#define SPI_MISO  12
#define SPI_MOSI  13

// CC1101 Module 1
#define CC1101_1_RX   4
#define CC1101_1_TX   2
#define CC1101_1_CS   5

// CC1101 Module 2
#define CC1101_2_RX   26
#define CC1101_2_TX   25
#define CC1101_2_CS   27

// LED Indicator (built-in)
#define LED_PIN  2

// Signal capture configuration
#define MAX_SAMPLES 2000
#define ERROR_TOLERANCE 200  // microseconds

// Default RF configuration
#define DEFAULT_FREQUENCY 433.92
#define DEFAULT_MODULATION 2  // ASK/OOK
#define DEFAULT_RX_BANDWIDTH 812.0
#define DEFAULT_DATARATE 3.79
#define DEFAULT_DEVIATION 47.6

#endif // CONFIG_H

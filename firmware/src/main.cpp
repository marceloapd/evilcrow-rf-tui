#include <Arduino.h>
#include "config.h"
#include "serial_protocol.h"
#include "cc1101_driver.h"
#include "rf_operations.h"

// External CC1101 driver instance
extern ELECHOUSE_CC1101 ELECHOUSE_cc1101;

// Global state
bool deviceReady = false;
int currentModule = 1;
float currentFrequency = DEFAULT_FREQUENCY;

void setup() {
    // Initialize LED
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    // Initialize serial protocol
    initSerial();

    // Initialize SPI pins
    pinMode(SPI_SCK, OUTPUT);
    pinMode(SPI_MISO, INPUT);
    pinMode(SPI_MOSI, OUTPUT);

    // Initialize CC1101 chip select pins
    pinMode(CC1101_1_CS, OUTPUT);
    pinMode(CC1101_2_CS, OUTPUT);
    digitalWrite(CC1101_1_CS, HIGH);
    digitalWrite(CC1101_2_CS, HIGH);

    // Initialize TX pins
    pinMode(CC1101_1_TX, OUTPUT);
    pinMode(CC1101_2_TX, OUTPUT);
    digitalWrite(CC1101_1_TX, LOW);
    digitalWrite(CC1101_2_TX, LOW);

    // Initialize CC1101 Module 1
    ELECHOUSE_cc1101.setSpiPin(SPI_SCK, SPI_MISO, SPI_MOSI, CC1101_1_CS);
    ELECHOUSE_cc1101.Init();
    ELECHOUSE_cc1101.setMHZ(DEFAULT_FREQUENCY);
    ELECHOUSE_cc1101.SetRx();

    // Initialize RX operations
    initRX();

    // Blink LED to indicate ready
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);

    deviceReady = true;
}

void loop() {
    // Process incoming serial commands
    processSerialCommand();

    // Small delay to prevent watchdog issues
    delay(1);
}

#include <Arduino.h>
#include "config.h"
#include "serial_protocol.h"
#include "cc1101_driver.h"

// Global state
bool deviceReady = false;

void setup() {
    // Initialize LED
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    // Initialize serial protocol
    initSerial();

    // TODO: Initialize CC1101 modules
    // ELECHOUSE_cc1101.Init();
    // ELECHOUSE_cc1101.setMHZ(DEFAULT_FREQUENCY);

    // Blink LED to indicate ready
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);

    deviceReady = true;
}

void loop() {
    // Process incoming serial commands
    processSerialCommand();

    // TODO: Handle RF operations (RX/TX/Jammer)
    // TODO: Check for signal captures

    // Small delay to prevent watchdog issues
    delay(1);
}

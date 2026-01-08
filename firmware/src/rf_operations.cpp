#include "rf_operations.h"
#include "config.h"
#include "cc1101_driver.h"
#include "serial_protocol.h"
#include <ArduinoJson.h>

// External CC1101 driver instance
extern ELECHOUSE_CC1101 ELECHOUSE_cc1101;

// RX state
#define RECEIVE_ATTR IRAM_ATTR
#define SAMPLE_SIZE 2000
#define SIGNAL_STORAGE 10

static unsigned long samples[SAMPLE_SIZE];
static unsigned long smoothedSamples[SAMPLE_SIZE];
static int sampleCount = 0;
static unsigned long lastTime = 0;
static bool rxActive = false;
static int activeModule = 1;
static int currentModulation = 2; // ASK/OOK default
static String analysisOutput = "";

// Signal analysis
static int lastSmoothIndex = 0;

// TX state
static bool txActive = false;

// Jammer state
static bool jammerActive = false;
static int jammerModule = 1;

// Interrupt handler for RX
void RECEIVE_ATTR receiver() {
    const long time = micros();
    const unsigned int duration = time - lastTime;

    // Reset if gap > 100ms
    if (duration > 100000) {
        sampleCount = 0;
    }

    // Capture timing (min 100us, max SAMPLE_SIZE)
    if (duration >= 100 && sampleCount < SAMPLE_SIZE) {
        samples[sampleCount++] = duration;
    }

    // Buffer full - stop RX
    if (sampleCount >= SAMPLE_SIZE) {
        sampleCount = SAMPLE_SIZE - 1;

        // Detach interrupts
        if (activeModule == 1) {
            detachInterrupt(digitalPinToInterrupt(CC1101_1_RX));
        } else {
            detachInterrupt(digitalPinToInterrupt(CC1101_2_RX));
        }

        rxActive = false;
    }

    // Filter false triggers for 2-FSK
    if (currentModulation == 0) { // 2-FSK
        int rxPin = (activeModule == 1) ? CC1101_1_RX : CC1101_2_RX;
        if (sampleCount == 1 && digitalRead(rxPin) != HIGH) {
            sampleCount = 0;
        }
    }

    lastTime = time;
}

void initRX() {
    // Initialize RX pins
    pinMode(CC1101_1_RX, INPUT);
    pinMode(CC1101_2_RX, INPUT);

    sampleCount = 0;
    rxActive = false;
}

void startRX(int module) {
    if (rxActive) {
        stopRX();
    }

    activeModule = module;
    sampleCount = 0;
    lastTime = micros();

    // Attach interrupt
    int rxPin = (module == 1) ? CC1101_1_RX : CC1101_2_RX;
    attachInterrupt(digitalPinToInterrupt(rxPin), receiver, CHANGE);

    rxActive = true;
}

void stopRX() {
    if (!rxActive) return;

    // Detach interrupts
    detachInterrupt(digitalPinToInterrupt(CC1101_1_RX));
    detachInterrupt(digitalPinToInterrupt(CC1101_2_RX));

    rxActive = false;

    // If we captured something, analyze it
    if (sampleCount > 30) {
        analyzeSignal();

        // Send signal_received event
        StaticJsonDocument<2048> doc;
        JsonObject data = doc.to<JsonObject>();

        data["sample_count"] = sampleCount;
        data["samples_per_symbol"] = (lastSmoothIndex > 0) ? smoothedSamples[0] : 0;

        // Send raw timings (limited to prevent overflow)
        JsonArray rawArray = data.createNestedArray("raw_timings_us");
        int maxSamples = min(sampleCount, 100); // Limit to 100 samples for JSON size
        for (int i = 0; i < maxSamples; i++) {
            rawArray.add(samples[i]);
        }

        data["total_samples"] = sampleCount;
        data["analysis"] = analysisOutput;

        sendEvent("signal_received", data);
    }
}

bool isRXActive() {
    return rxActive;
}

void analyzeSignal() {
    if (sampleCount < 2) {
        analysisOutput = "Insufficient samples";
        return;
    }

    analysisOutput = "";

    // Timing analysis arrays
    long signalTimings[SIGNAL_STORAGE * 2];
    int signalTimingsCount[SIGNAL_STORAGE];
    long signalTimingsSum[SIGNAL_STORAGE];
    int timingDelay[SIGNAL_STORAGE];

    // Initialize
    for (int i = 0; i < SIGNAL_STORAGE; i++) {
        signalTimings[i * 2] = 100000;
        signalTimings[i * 2 + 1] = 0;
        signalTimingsCount[i] = 0;
        signalTimingsSum[i] = 0;
    }

    // Find unique timing patterns
    for (int p = 0; p < SIGNAL_STORAGE; p++) {
        // Find minimum timing in this pass
        for (int i = 1; i < sampleCount; i++) {
            if (p == 0) {
                if (samples[i] < signalTimings[p * 2]) {
                    signalTimings[p * 2] = samples[i];
                }
            } else {
                if (samples[i] < signalTimings[p * 2] && samples[i] > signalTimings[p * 2 - 1]) {
                    signalTimings[p * 2] = samples[i];
                }
            }
        }

        // Find maximum timing within tolerance
        for (int i = 1; i < sampleCount; i++) {
            if (samples[i] < signalTimings[p * 2] + ERROR_TOLERANCE && samples[i] > signalTimings[p * 2 + 1]) {
                signalTimings[p * 2 + 1] = samples[i];
            }
        }

        // Count occurrences
        for (int i = 1; i < sampleCount; i++) {
            if (samples[i] >= signalTimings[p * 2] && samples[i] <= signalTimings[p * 2 + 1]) {
                signalTimingsCount[p]++;
                signalTimingsSum[p] += samples[i];
            }
        }
    }

    // Count unique patterns
    int signalCount = SIGNAL_STORAGE;
    for (int i = 0; i < SIGNAL_STORAGE; i++) {
        if (signalTimingsCount[i] == 0) {
            signalCount = i;
            break;
        }
    }

    // Sort by frequency (bubble sort)
    for (int s = 1; s < signalCount; s++) {
        for (int i = 0; i < signalCount - s; i++) {
            if (signalTimingsCount[i] < signalTimingsCount[i + 1]) {
                // Swap
                long temp1 = signalTimings[i * 2];
                long temp2 = signalTimings[i * 2 + 1];
                long temp3 = signalTimingsSum[i];
                int temp4 = signalTimingsCount[i];

                signalTimings[i * 2] = signalTimings[(i + 1) * 2];
                signalTimings[i * 2 + 1] = signalTimings[(i + 1) * 2 + 1];
                signalTimingsSum[i] = signalTimingsSum[i + 1];
                signalTimingsCount[i] = signalTimingsCount[i + 1];

                signalTimings[(i + 1) * 2] = temp1;
                signalTimings[(i + 1) * 2 + 1] = temp2;
                signalTimingsSum[i + 1] = temp3;
                signalTimingsCount[i + 1] = temp4;
            }
        }
    }

    // Calculate average timings
    for (int i = 0; i < signalCount; i++) {
        timingDelay[i] = signalTimingsSum[i] / signalTimingsCount[i];
    }

    // Generate binary representation
    String binaryOutput = "";
    bool lastBin = 0;

    for (int i = 1; i < sampleCount; i++) {
        float r = (float)samples[i] / timingDelay[0];
        int calculate = r;
        r = r - calculate;
        r *= 10;
        if (r >= 5) calculate += 1;

        if (calculate > 0) {
            lastBin = !lastBin;

            if (lastBin == 0 && calculate > 8) {
                binaryOutput += " [Pause: " + String(samples[i]) + "us] ";
            } else {
                for (int b = 0; b < calculate; b++) {
                    binaryOutput += String(lastBin);
                }
            }
        }
    }

    // Generate smoothed samples
    int smoothCount = 0;
    for (int i = 1; i < sampleCount && smoothCount < SAMPLE_SIZE; i++) {
        float r = (float)samples[i] / timingDelay[0];
        int calculate = r;
        r = r - calculate;
        r *= 10;
        if (r >= 5) calculate += 1;

        if (calculate > 0) {
            smoothedSamples[smoothCount] = calculate * timingDelay[0];
            smoothCount++;
        }
    }

    lastSmoothIndex = smoothCount - 1;

    // Build analysis output
    analysisOutput = "Binary: " + binaryOutput.substring(0, 200); // Limit size
    analysisOutput += "\nSamples/Symbol: " + String(timingDelay[0]) + "us";
    analysisOutput += "\nSmoothed count: " + String(smoothCount);
}

String getSignalData() {
    String data = "";
    for (int i = 0; i < sampleCount && i < 100; i++) {
        if (i > 0) data += ",";
        data += String(samples[i]);
    }
    return data;
}

String getAnalysisResult() {
    return analysisOutput;
}

int getSampleCount() {
    return sampleCount;
}

unsigned long* getRawSamples() {
    return samples;
}

unsigned long* getSmoothedSamples() {
    return smoothedSamples;
}

// TX Operations
void transmitSignal(int module, unsigned long* timings, int count, int repeat) {
    if (rxActive) {
        stopRX();
    }

    txActive = true;

    // Select TX pin based on module
    int txPin = (module == 1) ? CC1101_1_TX : CC1101_2_TX;
    pinMode(txPin, OUTPUT);
    digitalWrite(txPin, LOW);

    // Set CC1101 to TX mode
    ELECHOUSE_cc1101.SetTx();

    // Transmit signal 'repeat' times
    for (int r = 0; r < repeat; r++) {
        bool pinState = LOW;

        for (int i = 0; i < count; i++) {
            // Toggle pin state
            pinState = !pinState;
            digitalWrite(txPin, pinState);

            // Wait for timing duration
            delayMicroseconds(timings[i]);
        }

        // End with pin LOW
        digitalWrite(txPin, LOW);

        // Small delay between repeats
        if (r < repeat - 1) {
            delay(10);
        }
    }

    // Return to RX mode
    ELECHOUSE_cc1101.SetRx();
    txActive = false;
}

bool isTXActive() {
    return txActive;
}

// Jammer Operations
void startJammer(int module, float frequency, int power) {
    if (jammerActive) {
        stopJammer();
    }

    // Stop RX/TX if active
    if (rxActive) {
        stopRX();
    }

    jammerActive = true;
    jammerModule = module;

    // Select TX pin based on module
    int txPin = (module == 1) ? CC1101_1_TX : CC1101_2_TX;
    pinMode(txPin, OUTPUT);

    // Configure CC1101 for jamming
    int csPin = (module == 1) ? CC1101_1_CS : CC1101_2_CS;
    ELECHOUSE_cc1101.setSpiPin(SPI_SCK, SPI_MISO, SPI_MOSI, csPin);
    ELECHOUSE_cc1101.Init();
    ELECHOUSE_cc1101.setMHZ(frequency);

    // Set TX power if specified (0-10 dBm range typically)
    if (power >= 0 && power <= 12) {
        ELECHOUSE_cc1101.setPA(power);
    }

    // Set to TX mode for continuous carrier
    ELECHOUSE_cc1101.SetTx();

    // Start continuous carrier transmission
    // We'll toggle the TX pin rapidly to create noise/interference
    digitalWrite(txPin, HIGH);
}

void stopJammer() {
    if (!jammerActive) {
        return;
    }

    // Stop TX
    int txPin = (jammerModule == 1) ? CC1101_1_TX : CC1101_2_TX;
    digitalWrite(txPin, LOW);

    // Return CC1101 to RX mode
    ELECHOUSE_cc1101.SetRx();

    jammerActive = false;
}

bool isJammerActive() {
    return jammerActive;
}

// Scanner & Spectrum Operations
void scanFrequencies(int module, float start_mhz, float end_mhz, float step_khz, int threshold_dbm, int* results_count, float* frequencies, int* rssi_values) {
    // Stop any active operations
    if (rxActive) stopRX();
    if (jammerActive) stopJammer();

    *results_count = 0;

    // Configure CC1101
    int csPin = (module == 1) ? CC1101_1_CS : CC1101_2_CS;
    ELECHOUSE_cc1101.setSpiPin(SPI_SCK, SPI_MISO, SPI_MOSI, csPin);

    // Scan frequency range
    float freq = start_mhz;
    int index = 0;

    while (freq <= end_mhz && index < 100) { // Limit to 100 results
        // Set frequency
        ELECHOUSE_cc1101.setMHZ(freq);
        ELECHOUSE_cc1101.SetRx();

        // Wait for signal to stabilize
        delay(5);

        // Read RSSI
        int rssi = ELECHOUSE_cc1101.getRssi();

        // If signal detected above threshold
        if (rssi > threshold_dbm) {
            frequencies[index] = freq;
            rssi_values[index] = rssi;
            index++;
        }

        // Move to next frequency
        freq += (step_khz / 1000.0);
    }

    *results_count = index;

    // Return to RX mode on default frequency
    ELECHOUSE_cc1101.setMHZ(DEFAULT_FREQUENCY);
    ELECHOUSE_cc1101.SetRx();
}

void getSpectrum(int module, float center_mhz, float span_mhz, int points, float* frequencies, int* rssi_values) {
    // Stop any active operations
    if (rxActive) stopRX();
    if (jammerActive) stopJammer();

    // Configure CC1101
    int csPin = (module == 1) ? CC1101_1_CS : CC1101_2_CS;
    ELECHOUSE_cc1101.setSpiPin(SPI_SCK, SPI_MISO, SPI_MOSI, csPin);

    // Calculate frequency range
    float start_freq = center_mhz - (span_mhz / 2.0);
    float step = span_mhz / (points - 1);

    // Sample spectrum
    for (int i = 0; i < points; i++) {
        float freq = start_freq + (i * step);

        // Set frequency
        ELECHOUSE_cc1101.setMHZ(freq);
        ELECHOUSE_cc1101.SetRx();

        // Wait for signal to stabilize
        delay(2);

        // Read RSSI
        frequencies[i] = freq;
        rssi_values[i] = ELECHOUSE_cc1101.getRssi();
    }

    // Return to RX mode on default frequency
    ELECHOUSE_cc1101.setMHZ(DEFAULT_FREQUENCY);
    ELECHOUSE_cc1101.SetRx();
}

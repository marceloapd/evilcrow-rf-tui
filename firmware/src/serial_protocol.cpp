#include "serial_protocol.h"
#include "config.h"
#include "cc1101_driver.h"
#include "rf_operations.h"
#include <ArduinoJson.h>

// External references
extern ELECHOUSE_CC1101 ELECHOUSE_cc1101;
extern int currentModule;
extern float currentFrequency;

// Buffer for incoming serial data
String serialBuffer = "";

void initSerial() {
    Serial.begin(SERIAL_BAUD);
    while (!Serial && millis() < 5000) {
        ; // Wait for serial port to connect (max 5 seconds)
    }

    // Send ready event
    StaticJsonDocument<128> doc;
    JsonObject data = doc.to<JsonObject>();
    data["firmware_version"] = FIRMWARE_VERSION;
    sendEvent("ready", data);
}

void sendResponse(int cmd_id, const char* cmd, const char* status, JsonObject data) {
    StaticJsonDocument<1024> doc;
    doc["status"] = status;
    doc["cmd"] = cmd;
    doc["id"] = cmd_id;

    if (!data.isNull()) {
        doc["data"] = data;
    }

    serializeJson(doc, Serial);
    Serial.println();
}

void sendSimpleResponse(int cmd_id, const char* cmd, const char* status) {
    StaticJsonDocument<128> doc;
    doc["status"] = status;
    doc["cmd"] = cmd;
    doc["id"] = cmd_id;

    serializeJson(doc, Serial);
    Serial.println();
}

void sendError(int cmd_id, const char* cmd, const char* error_msg) {
    StaticJsonDocument<256> doc;
    doc["status"] = "error";
    doc["cmd"] = cmd;
    doc["id"] = cmd_id;
    doc["error"] = error_msg;

    serializeJson(doc, Serial);
    Serial.println();
}

void sendEvent(const char* event_name, JsonObject data) {
    StaticJsonDocument<2048> doc;
    doc["type"] = "event";
    doc["event"] = event_name;
    doc["timestamp"] = millis();

    if (!data.isNull()) {
        doc["data"] = data;
    }

    serializeJson(doc, Serial);
    Serial.println();
}

// Forward declarations for command handlers
void handlePing(int cmd_id);
void handleGetStatus(int cmd_id);
void handleReboot(int cmd_id);
void handleRxConfig(int cmd_id, JsonObject params);
void handleRxStart(int cmd_id, JsonObject params);
void handleRxStop(int cmd_id);
void handleTxSend(int cmd_id, JsonObject params);

void processSerialCommand() {
    while (Serial.available()) {
        char c = Serial.read();

        if (c == '\n' || c == '\r') {
            if (serialBuffer.length() > 0) {
                // Parse JSON command
                StaticJsonDocument<512> doc;
                DeserializationError error = deserializeJson(doc, serialBuffer);

                if (error) {
                    // Invalid JSON
                    serialBuffer = "";
                    return;
                }

                // Extract command fields
                const char* cmd = doc["cmd"];
                int cmd_id = doc["id"] | 0;

                if (cmd == nullptr) {
                    serialBuffer = "";
                    return;
                }

                // Extract params if present
                JsonObject params = doc["params"];

                // Route command to appropriate handler
                if (strcmp(cmd, "ping") == 0) {
                    handlePing(cmd_id);
                }
                else if (strcmp(cmd, "get_status") == 0) {
                    handleGetStatus(cmd_id);
                }
                else if (strcmp(cmd, "reboot") == 0) {
                    handleReboot(cmd_id);
                }
                else if (strcmp(cmd, "rx_config") == 0) {
                    handleRxConfig(cmd_id, params);
                }
                else if (strcmp(cmd, "rx_start") == 0) {
                    handleRxStart(cmd_id, params);
                }
                else if (strcmp(cmd, "rx_stop") == 0) {
                    handleRxStop(cmd_id);
                }
                else if (strcmp(cmd, "tx_send") == 0) {
                    handleTxSend(cmd_id, params);
                }
                else {
                    sendError(cmd_id, cmd, "Unknown command");
                }

                serialBuffer = "";
            }
        } else {
            serialBuffer += c;

            // Prevent buffer overflow
            if (serialBuffer.length() > 512) {
                serialBuffer = "";
            }
        }
    }
}

// Command Handlers

void handlePing(int cmd_id) {
    StaticJsonDocument<256> doc;
    JsonObject data = doc.to<JsonObject>();
    data["firmware_version"] = FIRMWARE_VERSION;
    data["uptime_ms"] = millis();
    data["free_heap"] = ESP.getFreeHeap();

    sendResponse(cmd_id, "ping", "ok", data);
}

void handleGetStatus(int cmd_id) {
    StaticJsonDocument<512> doc;
    JsonObject data = doc.to<JsonObject>();

    data["rx_active"] = isRXActive();
    data["tx_active"] = isTXActive();
    data["jammer_active"] = false;
    data["module"] = currentModule;
    data["frequency_mhz"] = currentFrequency;
    data["free_heap"] = ESP.getFreeHeap();
    data["uptime_ms"] = millis();

    sendResponse(cmd_id, "get_status", "ok", data);
}

void handleReboot(int cmd_id) {
    sendSimpleResponse(cmd_id, "reboot", "ok");
    delay(100);
    ESP.restart();
}

void handleRxConfig(int cmd_id, JsonObject params) {
    if (params.isNull()) {
        sendError(cmd_id, "rx_config", "Missing params");
        return;
    }

    // Stop RX if active
    if (isRXActive()) {
        stopRX();
    }

    // Extract parameters
    int module = params["module"] | 1;
    float frequency = params["frequency_mhz"] | DEFAULT_FREQUENCY;

    // Update global state
    currentModule = module;
    currentFrequency = frequency;

    // Configure CC1101
    int csPin = (module == 1) ? CC1101_1_CS : CC1101_2_CS;
    ELECHOUSE_cc1101.setSpiPin(SPI_SCK, SPI_MISO, SPI_MOSI, csPin);
    ELECHOUSE_cc1101.Init();
    ELECHOUSE_cc1101.setMHZ(frequency);

    // Optional: Set modulation if provided
    if (params.containsKey("modulation")) {
        int mod = params["modulation"];
        ELECHOUSE_cc1101.setModulation(mod);
    }

    // Optional: Set RX bandwidth if provided
    if (params.containsKey("rx_bandwidth_khz")) {
        float rxBW = params["rx_bandwidth_khz"];
        ELECHOUSE_cc1101.setRxBW(rxBW);
    }

    // Set to RX mode
    ELECHOUSE_cc1101.SetRx();

    // Send response
    StaticJsonDocument<256> doc;
    JsonObject data = doc.to<JsonObject>();
    data["module"] = module;
    data["frequency_mhz"] = frequency;

    sendResponse(cmd_id, "rx_config", "ok", data);
}

void handleRxStart(int cmd_id, JsonObject params) {
    if (isRXActive()) {
        sendError(cmd_id, "rx_start", "RX already active");
        return;
    }

    // Module selection (default to currentModule)
    int module = currentModule;
    if (!params.isNull() && params.containsKey("module")) {
        module = params["module"];
    }

    // Start RX
    startRX(module);

    // Send response
    StaticJsonDocument<256> doc;
    JsonObject data = doc.to<JsonObject>();
    data["module"] = module;
    data["frequency_mhz"] = currentFrequency;

    sendResponse(cmd_id, "rx_start", "ok", data);
}

void handleRxStop(int cmd_id) {
    if (!isRXActive()) {
        sendError(cmd_id, "rx_stop", "RX not active");
        return;
    }

    // Stop RX (this will trigger signal analysis and send signal_received event)
    stopRX();

    // Send response
    sendSimpleResponse(cmd_id, "rx_stop", "ok");
}

void handleTxSend(int cmd_id, JsonObject params) {
    if (params.isNull()) {
        sendError(cmd_id, "tx_send", "Missing params");
        return;
    }

    if (!params.containsKey("timings_us")) {
        sendError(cmd_id, "tx_send", "Missing timings_us");
        return;
    }

    // Extract parameters
    int module = params["module"] | currentModule;
    int repeat = params["repeat"] | 1;
    JsonArray timingsArray = params["timings_us"];

    if (timingsArray.isNull() || timingsArray.size() == 0) {
        sendError(cmd_id, "tx_send", "Invalid timings_us");
        return;
    }

    // Check size limit
    if (timingsArray.size() > MAX_SAMPLES) {
        sendError(cmd_id, "tx_send", "Too many timings (max 2000)");
        return;
    }

    // Copy timings to array
    unsigned long timings[MAX_SAMPLES];
    int count = timingsArray.size();
    for (int i = 0; i < count; i++) {
        timings[i] = timingsArray[i];
    }

    // Transmit signal
    transmitSignal(module, timings, count, repeat);

    // Send response
    StaticJsonDocument<256> doc;
    JsonObject data = doc.to<JsonObject>();
    data["module"] = module;
    data["count"] = count;
    data["repeat"] = repeat;

    sendResponse(cmd_id, "tx_send", "ok", data);
}

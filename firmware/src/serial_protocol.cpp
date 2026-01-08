#include "serial_protocol.h"
#include "config.h"
#include <ArduinoJson.h>

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

    data["rx_active"] = false;  // Will be updated by rf_operations
    data["tx_active"] = false;
    data["jammer_active"] = false;
    data["module"] = 1;
    data["frequency_mhz"] = DEFAULT_FREQUENCY;
    data["free_heap"] = ESP.getFreeHeap();
    data["uptime_ms"] = millis();

    sendResponse(cmd_id, "get_status", "ok", data);
}

void handleReboot(int cmd_id) {
    sendSimpleResponse(cmd_id, "reboot", "ok");
    delay(100);
    ESP.restart();
}

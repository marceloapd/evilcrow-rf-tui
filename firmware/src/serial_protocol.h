#ifndef SERIAL_PROTOCOL_H
#define SERIAL_PROTOCOL_H

#include <Arduino.h>
#include <ArduinoJson.h>

// Initialize serial protocol
void initSerial();

// Process incoming serial commands
void processSerialCommand();

// Send JSON response to host
void sendResponse(int cmd_id, const char* cmd, const char* status, JsonObject data);

// Send JSON event to host (unsolicited)
void sendEvent(const char* event_name, JsonObject data);

// Helper: send simple response without data
void sendSimpleResponse(int cmd_id, const char* cmd, const char* status);

// Helper: send error response
void sendError(int cmd_id, const char* cmd, const char* error_msg);

#endif // SERIAL_PROTOCOL_H

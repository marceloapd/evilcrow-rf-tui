#ifndef RF_OPERATIONS_H
#define RF_OPERATIONS_H

#include <Arduino.h>

// RX Operations
void initRX();
void startRX(int module);
void stopRX();
bool isRXActive();

// TX Operations
void transmitSignal(int module, unsigned long* timings, int count, int repeat);
bool isTXActive();

// Jammer Operations
void startJammer(int module, float frequency, int power);
void stopJammer();
bool isJammerActive();

// Signal analysis
void analyzeSignal();
String getSignalData();
String getAnalysisResult();

// Get captured signal info
int getSampleCount();
unsigned long* getRawSamples();
unsigned long* getSmoothedSamples();

// Scanner & Spectrum Operations
void scanFrequencies(int module, float start_mhz, float end_mhz, float step_khz, int threshold_dbm, int* results_count, float* frequencies, int* rssi_values);
void getSpectrum(int module, float center_mhz, float span_mhz, int points, float* frequencies, int* rssi_values);

#endif // RF_OPERATIONS_H

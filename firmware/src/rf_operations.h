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

// Jammer Operations (to be implemented)
void startJammer(int module, float frequency, int power);
void stopJammer();

// Signal analysis
void analyzeSignal();
String getSignalData();
String getAnalysisResult();

// Get captured signal info
int getSampleCount();
unsigned long* getRawSamples();
unsigned long* getSmoothedSamples();

#endif // RF_OPERATIONS_H

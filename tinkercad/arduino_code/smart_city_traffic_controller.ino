#include <LiquidCrystal.h>

// ============================================================================
// PIN DEFINITIONS
// ============================================================================

// LED pins (Output)
const int RED_A = 2;
const int YEL_A = 3;
const int GRN_A = 4;

const int RED_B = 5;
const int YEL_B = 6;
const int GRN_B = 7;

const int RED_C = 8;
const int YEL_C = 9;
const int GRN_C = 10;

// Button pins (Input)
const int BTN_VEH_A = 11;
const int BTN_VEH_B = 12;
const int BTN_VEH_C = 13;
const int BTN_AMB   = A0;

// LCD Interface: LiquidCrystal lcd(rs, en, d4, d5, d6, d7)
// LiquidCrystal mapping matches TINKERCAD_DESIGN.md:
// RS=A1, EN=A2, D4=A3, D5=A4, D6=A5, D7=D1
const int LCD_RS = A1;
const int LCD_EN = A2;
const int LCD_D4 = A3;
const int LCD_D5 = A4;
const int LCD_D6 = A5;
const int LCD_D7 = 1;

LiquidCrystal lcd(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

// ============================================================================
// ENUMS & CONSTANTS
// ============================================================================

// ============================================================================
// ENUMS & CONSTANTS
// ============================================================================

// System state machine modes
enum SystemMode {
  NORMAL,
  EMERGENCY_ROUTE,
  EMERGENCY_CORRIDOR,
  ARRIVAL,
  RECOVERY
};

// Signal states for individual intersections
enum SignalState {
  STATE_RED,
  STATE_GREEN,
  STATE_YELLOW
};

// Timing constants (in milliseconds)
const unsigned long SIGNAL_CYCLES = 3000;    // Duration of each traffic light phase (3s)
const unsigned long AMBULANCE_ADVANCE = 4000; // Simulated time to move from junction to junction (4s)
const unsigned long DEBOUNCE_DELAY = 150;    // Software debounce window (150ms)
const unsigned long LCD_REFRESH = 500;       // LCD refresh rate (500ms)

// ============================================================================
// SYSTEM VARIABLES
// ============================================================================

SystemMode currentMode = NORMAL;
unsigned long modeTimer = 0;
unsigned long lcdTimer = 0;

// Vehicle counts and density classifications
int vehCountA = 0;
int vehCountB = 0;
int vehCountC = 0;

// Signal cycle states for normal mode
SignalState stateA = STATE_RED;
SignalState stateB = STATE_GREEN;
SignalState stateC = STATE_RED;

unsigned long cycleTimerA = 0;
unsigned long cycleTimerB = 1000; // Offset cycles for realistic offset
unsigned long cycleTimerC = 2000;

// Button debouncing helper variables
int lastBtnVehAState = LOW;
int lastBtnVehBState = LOW;
int lastBtnVehCState = LOW;
int lastBtnAmbState   = LOW;

unsigned long debounceTimerA = 0;
unsigned long debounceTimerB = 0;
unsigned long debounceTimerC = 0;
unsigned long debounceTimerAmb = 0;

// Ambulance routing and ETA variables
String activeRouteStr = "A>B>C>I";
char activeRoutePath[6] = {'A', 'B', 'C', 'I', '\0', '\0'};
int activeRouteLength = 4;
int currentCorridorStep = 0;
int etaSeconds = 252;
int baseEtaSeconds = 252;

// ============================================================================
// SETUP & INITIALIZATION
// ============================================================================

void setup() {
  // Initialize LED pins as output
  pinMode(RED_A, OUTPUT);
  pinMode(YEL_A, OUTPUT);
  pinMode(GRN_A, OUTPUT);
  
  pinMode(RED_B, OUTPUT);
  pinMode(YEL_B, OUTPUT);
  pinMode(GRN_B, OUTPUT);
  
  pinMode(RED_C, OUTPUT);
  pinMode(YEL_C, OUTPUT);
  pinMode(GRN_C, OUTPUT);
  
  // Initialize button pins as input
  pinMode(BTN_VEH_A, INPUT);
  pinMode(BTN_VEH_B, INPUT);
  pinMode(BTN_VEH_C, INPUT);
  pinMode(BTN_AMB, INPUT);
  
  // Initialize LCD
  lcd.begin(16, 2);
  lcd.clear();
  lcd.print("SYSTEM BOOTING");
  delay(1000);
  
  // Set timers
  unsigned long now = millis();
  cycleTimerA = now;
  cycleTimerB = now;
  cycleTimerC = now;
  modeTimer = now;
  lcdTimer = now;
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  unsigned long now = millis();
  
  // 1. Read input buttons with debouncing
  readButtons(now);
  
  // 2. Handle state transitions and controller execution
  switch (currentMode) {
    case NORMAL:
      runNormalCycling(now);
      updateLCDNormal(now);
      break;
      
    case EMERGENCY_ROUTE:
      // Show selected route for 2 seconds before ambulance starts moving
      setAllLEDsOff();
      digitalWrite(RED_A, HIGH);
      digitalWrite(RED_B, HIGH);
      digitalWrite(RED_C, HIGH);
      
      updateLCDEmergencyRoute(now);
      
      if (now - modeTimer >= 2000) {
        currentMode = EMERGENCY_CORRIDOR;
        currentCorridorStep = 0;
        modeTimer = now;
      }
      break;
      
    case EMERGENCY_CORRIDOR:
      runEmergencyCorridor(now);
      
      // Calculate remaining ETA dynamically
      {
        int elapsedOnSegment = (now - modeTimer) / 1000;
        int stepBaseTime = baseEtaSeconds / (activeRouteLength - 1);
        int remainingSteps = (activeRouteLength - 1) - currentCorridorStep;
        int stepProgressSeconds = stepBaseTime - elapsedOnSegment * (stepBaseTime / (AMBULANCE_ADVANCE / 1000));
        if (stepProgressSeconds < 0) stepProgressSeconds = 0;
        etaSeconds = (remainingSteps - 1) * stepBaseTime + stepProgressSeconds;
      }
      
      updateLCDCorridor(now, String(activeRoutePath[currentCorridorStep]), etaSeconds);
      
      if (now - modeTimer >= AMBULANCE_ADVANCE) {
        currentCorridorStep++;
        modeTimer = now;
        
        // If we reached the end of the route (hospital 'I'), trigger arrival
        if (currentCorridorStep >= activeRouteLength - 1) {
          currentMode = ARRIVAL;
        }
      }
      break;
      
    case ARRIVAL:
      setAllLEDsOff();
      digitalWrite(RED_A, HIGH);
      digitalWrite(RED_B, HIGH);
      digitalWrite(RED_C, HIGH);
      
      updateLCDArrival(now);
      
      if (now - modeTimer >= 3000) { // Display arrival for 3 seconds
        currentMode = RECOVERY;
        modeTimer = now;
      }
      break;
      
    case RECOVERY:
      setAllLEDsOff();
      updateLCDRecovery(now);
      
      if (now - modeTimer >= 2000) { // Recovery transition display for 2 seconds
        // Reset vehicle counts
        vehCountA = 0;
        vehCountB = 0;
        vehCountC = 0;
        
        currentMode = NORMAL;
        modeTimer = now;
      }
      break;
  }
}

// ============================================================================
// DRIVER AND LOGIC FUNCTIONS
// ============================================================================

// Debounced button readings
void readButtons(unsigned long now) {
  // Vehicle Button A
  int readingVehA = digitalRead(BTN_VEH_A);
  if (readingVehA != lastBtnVehAState) {
    debounceTimerA = now;
  }
  if ((now - debounceTimerA) > DEBOUNCE_DELAY) {
    if (readingVehA == HIGH && currentMode == NORMAL) {
      vehCountA++;
      debounceTimerA = now + 200; // Extra latch time
    }
  }
  lastBtnVehAState = readingVehA;
  
  // Vehicle Button B
  int readingVehB = digitalRead(BTN_VEH_B);
  if (readingVehB != lastBtnVehBState) {
    debounceTimerB = now;
  }
  if ((now - debounceTimerB) > DEBOUNCE_DELAY) {
    if (readingVehB == HIGH && currentMode == NORMAL) {
      vehCountB++;
      debounceTimerB = now + 200;
    }
  }
  lastBtnVehBState = readingVehB;
  
  // Vehicle Button C
  int readingVehC = digitalRead(BTN_VEH_C);
  if (readingVehC != lastBtnVehCState) {
    debounceTimerC = now;
  }
  if ((now - debounceTimerC) > DEBOUNCE_DELAY) {
    if (readingVehC == HIGH && currentMode == NORMAL) {
      vehCountC++;
      debounceTimerC = now + 200;
    }
  }
  lastBtnVehCState = readingVehC;
  
  // Ambulance Emergency Override Button
  int readingAmb = digitalRead(BTN_AMB);
  if (readingAmb != lastBtnAmbState) {
    debounceTimerAmb = now;
  }
  if ((now - debounceTimerAmb) > DEBOUNCE_DELAY) {
    if (readingAmb == HIGH && currentMode == NORMAL) {
      calculateDynamicRoute();
      currentMode = EMERGENCY_ROUTE;
      modeTimer = now;
      debounceTimerAmb = now + 500;
    }
  }
  lastBtnAmbState = readingAmb;
}

// Dynamic route lookup based on traffic volume
void calculateDynamicRoute() {
  String densityB = getDensityLabel(vehCountB);
  String densityC = getDensityLabel(vehCountC);
  
  if (densityB == "HIGH") {
    // Route bypasses B and C: A -> D -> G -> H -> I
    activeRouteStr = "A>D>G>H>I";
    activeRoutePath[0] = 'A';
    activeRoutePath[1] = 'D';
    activeRoutePath[2] = 'G';
    activeRoutePath[3] = 'H';
    activeRoutePath[4] = 'I';
    activeRoutePath[5] = '\0';
    activeRouteLength = 5;
    
    // Total ETA calculations (in seconds)
    // 4 LOW segments at base time = 4 * 63s = 252 seconds
    baseEtaSeconds = 252;
  }
  else if (densityC == "HIGH") {
    // Route bypasses C: A -> B -> E -> H -> I
    activeRouteStr = "A>B>E>H>I";
    activeRoutePath[0] = 'A';
    activeRoutePath[1] = 'B';
    activeRoutePath[2] = 'E';
    activeRoutePath[3] = 'H';
    activeRoutePath[4] = 'I';
    activeRoutePath[5] = '\0';
    activeRouteLength = 5;
    
    // Total ETA: A->B cost depends on B's density
    int segmentCost = (densityB == "MED") ? 90 : 63;
    baseEtaSeconds = segmentCost + 63 + 63 + 63; // E, H, I segments are LOW
  }
  else {
    // Standard shortest path: A -> B -> C -> I
    activeRouteStr = "A>B>C>I";
    activeRoutePath[0] = 'A';
    activeRoutePath[1] = 'B';
    activeRoutePath[2] = 'C';
    activeRoutePath[3] = 'I';
    activeRoutePath[4] = '\0';
    activeRouteLength = 4;
    
    int segmentAB = (densityB == "MED") ? 90 : 63;
    int segmentBC = (densityC == "MED") ? 90 : 63;
    baseEtaSeconds = segmentAB + segmentBC + 63; // C->I is LOW
  }
  etaSeconds = baseEtaSeconds;
}

// Get string label for traffic density
String getDensityLabel(int count) {
  if (count <= 10) return "LOW";
  if (count <= 25) return "MED";
  return "HIGH";
}

// Reset all LED outputs
void setAllLEDsOff() {
  digitalWrite(RED_A, LOW);
  digitalWrite(YEL_A, LOW);
  digitalWrite(GRN_A, LOW);
  digitalWrite(RED_B, LOW);
  digitalWrite(YEL_B, LOW);
  digitalWrite(GRN_B, LOW);
  digitalWrite(RED_C, LOW);
  digitalWrite(YEL_C, LOW);
  digitalWrite(GRN_C, LOW);
}

// Normal signal cycling logic for all junctions
void runNormalCycling(unsigned long now) {
  runNormalCyclingJunctionA(now);
  runNormalCyclingJunctionB(now);
  runNormalCyclingJunctionC(now);
}

void runNormalCyclingJunctionA(unsigned long now) {
  if (now - cycleTimerA >= SIGNAL_CYCLES) {
    cycleTimerA = now;
    stateA = (SignalState)((stateA + 1) % 3);
  }
  digitalWrite(RED_A, stateA == STATE_RED ? HIGH : LOW);
  digitalWrite(YEL_A, stateA == STATE_YELLOW ? HIGH : LOW);
  digitalWrite(GRN_A, stateA == STATE_GREEN ? HIGH : LOW);
}

void runNormalCyclingJunctionB(unsigned long now) {
  if (now - cycleTimerB >= SIGNAL_CYCLES) {
    cycleTimerB = now;
    stateB = (SignalState)((stateB + 1) % 3);
  }
  digitalWrite(RED_B, stateB == STATE_RED ? HIGH : LOW);
  digitalWrite(YEL_B, stateB == STATE_YELLOW ? HIGH : LOW);
  digitalWrite(GRN_B, stateB == STATE_GREEN ? HIGH : LOW);
}

void runNormalCyclingJunctionC(unsigned long now) {
  if (now - cycleTimerC >= SIGNAL_CYCLES) {
    cycleTimerC = now;
    stateC = (SignalState)((stateC + 1) % 3);
  }
  digitalWrite(RED_C, stateC == STATE_RED ? HIGH : LOW);
  digitalWrite(YEL_C, stateC == STATE_YELLOW ? HIGH : LOW);
  digitalWrite(GRN_C, stateC == STATE_GREEN ? HIGH : LOW);
}

// Emergency override logic for the active route node
void runEmergencyCorridor(unsigned long now) {
  char currentNode = activeRoutePath[currentCorridorStep];
  char nextNode = activeRoutePath[currentCorridorStep + 1];
  
  // Junction A LED control
  if (currentNode == 'A') {
    digitalWrite(RED_A, LOW);
    digitalWrite(YEL_A, LOW);
    digitalWrite(GRN_A, HIGH); // Overridden
  } else {
    runNormalCyclingJunctionA(now);
  }
  
  // Junction B LED control
  if (currentNode == 'B') {
    digitalWrite(RED_B, LOW);
    digitalWrite(YEL_B, LOW);
    digitalWrite(GRN_B, HIGH); // Overridden
  } else if (currentNode == 'A' && nextNode == 'B') {
    digitalWrite(RED_B, HIGH); // Prepare
    digitalWrite(YEL_B, LOW);
    digitalWrite(GRN_B, LOW);
  } else {
    runNormalCyclingJunctionB(now);
  }
  
  // Junction C LED control
  if (currentNode == 'C') {
    digitalWrite(RED_C, LOW);
    digitalWrite(YEL_C, LOW);
    digitalWrite(GRN_C, HIGH); // Overridden
  } else if (currentNode == 'B' && nextNode == 'C') {
    digitalWrite(RED_C, HIGH); // Prepare
    digitalWrite(YEL_C, LOW);
    digitalWrite(GRN_C, LOW);
  } else {
    runNormalCyclingJunctionC(now);
  }
}

// ============================================================================
// LCD UPDATE FUNCTIONS
// ============================================================================

void updateLCDNormal(unsigned long now) {
  if (now - lcdTimer >= LCD_REFRESH) {
    lcdTimer = now;
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("A:");
    lcd.print(getDensityLabel(vehCountA));
    lcd.setCursor(8, 0);
    lcd.print("B:");
    lcd.print(getDensityLabel(vehCountB));
    
    lcd.setCursor(0, 1);
    lcd.print("C:");
    lcd.print(getDensityLabel(vehCountC));
    lcd.setCursor(8, 1);
    lcd.print("NORMAL  ");
  }
}

void updateLCDEmergencyRoute(unsigned long now) {
  if (now - lcdTimer >= LCD_REFRESH) {
    lcdTimer = now;
    
    int minutes = baseEtaSeconds / 60;
    int seconds = baseEtaSeconds % 60;
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("ROUTE: ");
    lcd.print(activeRouteStr);
    lcd.setCursor(0, 1);
    lcd.print("ETA: ");
    lcd.print(minutes);
    lcd.print(":");
    if (seconds < 10) lcd.print("0");
    lcd.print(seconds);
  }
}

void updateLCDCorridor(unsigned long now, String position, int remainingSeconds) {
  if (now - lcdTimer >= LCD_REFRESH) {
    lcdTimer = now;
    
    int minutes = remainingSeconds / 60;
    int seconds = remainingSeconds % 60;
    
    if (minutes < 0) minutes = 0;
    if (seconds < 0) seconds = 0;
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("CORRIDOR ACTIVE ");
    lcd.setCursor(0, 1);
    lcd.print("AMB@");
    lcd.print(position);
    lcd.print("  ETA:");
    lcd.print(minutes);
    lcd.print(":");
    if (seconds < 10) lcd.print("0");
    lcd.print(seconds);
  }
}

void updateLCDArrival(unsigned long now) {
  if (now - lcdTimer >= LCD_REFRESH) {
    lcdTimer = now;
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("AMB AT HOSPITAL ");
    lcd.setCursor(0, 1);
    lcd.print("SAVED: 06:00    ");
  }
}

void updateLCDRecovery(unsigned long now) {
  if (now - lcdTimer >= LCD_REFRESH) {
    lcdTimer = now;
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("RECOVERING...   ");
    lcd.setCursor(0, 1);
    lcd.print("SIGNALS NORMAL  ");
  }
}


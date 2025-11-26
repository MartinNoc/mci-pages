# Smart Light Assignment - Implementierungsanleitung

## 🎯 Projektübersicht

In diesem Assignment entwickelst ihr ein intelligentes Lichtsystem mit folgenden Funktionen:

- **Umgebungslichtsensor (LDR)**: Misst die aktuelle Helligkeit
- **Intelligente LED-Steuerung**: LEDs werden bei Dunkelheit heller, bei Helligkeit dunkler
- **Smooth Verhalten**: Sanfte Übergänge ohne harte Sprünge
- **BLE-Kommunikation**: Status senden und optional Befehle empfangen
- **Flexible Ausgabe**: Einzelne LED oder Balkenanzeige (6 LEDs)

## 📋 Hardware-Aufbau

### Benötigte Komponenten
- ESP32 Entwicklungsboard
- 1x LDR (Fotowiderstand) + 10kΩ Widerstand
- 1x LED + 220Ω Widerstand (für Single-LED Modus)
- 6x LEDs + 220Ω Widerstände (für Bargraph-Modus)
- Breadboard und Verbindungskabel

### Pin-Belegung (Empfehlung)
```
LDR:         GPIO 33 (ADC1_CH5)
Einzel-LED:  GPIO 23
Bargraph:    GPIO 14, 27, 26, 32, 21, 22
```

## 🔧 Schritt 1: Projekt Setup und Konfiguration

### Grundlegende Imports und Konstanten

Beginne mit den notwendigen Imports:

```python
from machine import Pin, ADC, PWM
from time import ticks_ms, ticks_diff
import bluetooth, struct
```

### Konfiguration definieren

Erstelle eine Konfigurationssektion am Anfang deiner Datei:

```python
# Hardware-Pins
PIN_LDR = 33
PIN_LED = 23
BAR_PINS = [14, 27, 26, 32, 21, 22]

# PWM-Einstellungen
PWM_FREQ = 1000

# LDR-Kalibrierung (experimentell bestimmen!)
ADC_MIN = 200    # Dunkelster gemessener Wert - Selber bitte bestimmen
ADC_MAX = 3500   # Hellster gemessener Wert - Selber bitte bestimmen

# Verhalten
EMA_ALPHA = 0.2         # Glättungsfaktor (0.1-0.3 empfohlen)
STAT_INTERVAL = 2000    # BLE-Status alle 2 Sekunden
USE_BARGRAPH = True     # Bargraph oder Einzel-LED
```

## 🔧 Schritt 2: Hardware initialisieren

### ADC für LDR konfigurieren

```python
# LDR Setup
adc = ADC(Pin(PIN_LDR))     # ADC intialisieren
adc.atten(ADC.ATTN_11DB)    # 0-3.3V Messbereich
adc.width(ADC.WIDTH_12BIT)  # 12-Bit Auflösung (0-4095)
```

### PWM für LEDs einrichten

```python
# Einzel-LED PWM
single_led = PWM(Pin(PIN_LED), freq=PWM_FREQ)

# Bargraph LEDs PWM
bargraph_leds = [PWM(Pin(pin), freq=PWM_FREQ) for pin in BAR_PINS]
```

**💡 Tipp**: Teste zuerst jeden LED-Pin einzeln, um sicherzustellen, dass die Verkabelung korrekt ist. Das kann mittels led.on() oder direkt über die PWM gemacht werden. 

## 🔧 Schritt 3: PWM-Steuerfunktionen

### PWM-Wert setzen (0.0-1.0)

Implementiere eine Hilfsfunktion zum Setzen von PWM-Werten:

```python
def set_pwm_brightness(pwm_obj, brightness):
    # brightness: 0.0 (aus) bis 1.0 (voll an)
    # Begrenzung auf gültigen Bereich
    # PWM-Duty-Cycle berechnen und setzen
    pass
```

**🎯 Deine Aufgabe**: 
- Mapping programmieren das `brightness` zwischen 0.0 und 1.0 ist. (Max-Value == 1.0)
- Konvertiere zu PWM-Duty-Cycle
- Verwende `duty_u16()` für 16-Bit PWM oder `duty()` für 10-Bit

### Einzel-LED Steuerung

```python
def control_single_led(brightness):
    # Steuert die einzelne LED
    pass
```

### Bargraph-LED Steuerung

```python
def control_bargraph(brightness):
    # brightness: 0.0-1.0
    # Berechne, wie viele LEDs leuchten sollen
    # Verteile die Helligkeit über die LEDs
    # Beispiel: brightness=0.5 → 3 LEDs voll, 0 LEDs teilweise
    pass
```

**🎯 Deine Aufgabe**: 
- Multipliziere `brightness` mit der Anzahl LEDs
- Verwende `enumerate()` um über LED-Index zu iterieren
- Jede LED bekommt einen Anteil der Gesamthelligkeit

## 🔧 Schritt 4: LDR-Sensordaten auslesen

### Rohdaten normalisieren

```python
def read_ldr_normalized():
    # ADC-Rohdaten auslesen
    # Auf Kalibrierungsbereich begrenzen
    # Zu 0.0-1.0 normalisieren
    # Rückgabe: (normalized_value, raw_value)
    pass
```

### EMA-Filter (oder ähnliches) für die Glättung

Implementiere einen Exponential Moving Average Filter:

```python
# Globale Variable für Filter-Zustand
ema_value = None

def apply_ema_filter(new_value, alpha=EMA_ALPHA):
    global ema_value
    # Erste Messung: direkt übernehmen
    # Weitere Messungen: EMA-Formel anwenden
    # ema = alpha * new_value + (1 - alpha) * old_ema
    pass
```

**💡 Tipp**: Ein niedriger Alpha-Wert (0.1-0.2) macht das System sehr sanft, höhere Werte (0.5+) reagieren schneller (gerne experimentel ausprobieren).

## 🔧 Schritt 5: BLE-Kommunikation implementieren

### BLE-Klasse Grundstruktur

```python
class SmartLightBLE:
    def __init__(self, device_name="SmartLight"):
        # BLE initialisieren
        # UART-Service definieren
        # Interrupt-Handler registrieren
        # Advertising starten
        pass
    
    def _irq_handler(self, event, data):
        # Event 1: Verbindung hergestellt
        # Event 2: Verbindung getrennt
        # Event 3: Daten empfangen
        pass
    
    def send_status(self, message):
        # Status-Nachricht an verbundene Clients senden
        pass
    
    def _create_advertising_payload(self, name):
        # Advertising-Daten für Gerätename erstellen
        pass
```

### UART-Service definieren

Verwende den Standard Nordic UART Service:

```python
# Standard UART Service UUIDs Nordic UART Service
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" # 
UART_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # ESP32 → App
UART_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # App → ESP32
```

**🎯 Deine Aufgabe**: 
- Registriere den UART-Service mit TX (notify) und RX (write) Characteristics
- Implementiere Event-Handler für Verbindungen und Datenempfang

### Kommandos verarbeiten (Optional)

```python
def handle_incoming_command(self, message):
    # "LEVEL:75" → Manuelle Helligkeitssteuerung auf 75%
    # "MODE:AUTO" → Zurück zum automatischen Modus
    pass
```

## 🔧 Schritt 6: Intelligente Lichtsteuerung

### Mapping-Logik: Umgebungslicht zu LED-Helligkeit

```python
def calculate_led_brightness(ldr_normalized):
    # Umgekehrte Logik implementieren:
    # ldr_normalized = 0.0 (dunkel) → led_brightness = 1.0 (hell)
    # ldr_normalized = 1.0 (hell) → led_brightness = 0.0 (dunkel)
    pass
```

**💡 Tipp**: Die einfachste Implementierung ist `led_brightness = 1.0 - ldr_normalized`

### Override-Modus für manuelle Steuerung

```python
# Globale Variablen
auto_mode = True
manual_brightness = 0.5

def get_current_brightness(ldr_value):
    # Wenn auto_mode: verwende berechnete Helligkeit
    # Wenn manual: verwende manual_brightness
    pass
```

## 🔧 Schritt 7: Hauptprogramm-Schleife

### Timing-Management

```python
# Status-Timing
last_status_time = ticks_ms()

while True:
    current_time = ticks_ms()
    
    # 1. LDR auslesen und glätten
    
    # 2. LED-Helligkeit berechnen
    
    # 3. LEDs steuern
    
    # 4. BLE-Status senden (alle STAT_INTERVAL ms)
    
    # 5. Kurze Pause für Stabilität
```

### Struktur der Hauptschleife

```python
while True:
    # Sensor auslesen
    ldr_raw = # ADC lesen
    ldr_normalized = # normalisieren und glätten
    
    # Helligkeit berechnen
    target_brightness = # mapping anwenden
    
    # LEDs steuern
    if USE_BARGRAPH:
        # Bargraph steuern
    else:
        # Einzel-LED steuern
    
    # Status senden (zeitgesteuert)
    if # Zeit für Status-Update:
        status_message = # "STAT:LDR=1234,OUT=67%"
        # BLE-Status senden
    
    # Kleine Pause
```

## 🔧 Schritt 8: Testing und Kalibrierung

### LDR-Kalibrierung

1. **Dunkel-Kalibrierung**: Decke den LDR ab und notiere den ADC-Wert
2. **Hell-Kalibrierung**: Beleuchte den LDR stark und notiere den ADC-Wert
3. **Werte in Konstanten eintragen**: `ADC_MIN` und `ADC_MAX` entsprechend setzen

### LED-Test

```python
# Test-Funktion für LEDs
def test_leds():
    for brightness in [0.0, 0.25, 0.5, 0.75, 1.0]:
        print(f"Teste Helligkeit: {brightness}")
        if USE_BARGRAPH:
            control_bargraph(brightness)
        else:
            control_single_led(brightness)
        time.sleep(1)
```

### BLE-Test mit LightBlue App

1. **App installieren**: "LightBlue" (iOS/Android)
2. **Gerät suchen**: "SmartLight" sollte erscheinen
3. **Verbinden und Services erkunden**
4. **UART RX**: Nachrichten an ESP32 senden
5. **UART TX**: Status-Nachrichten von ESP32 empfangen

## 📊 Status-Nachrichten Format

### Empfohlenes Format

```
STAT:LDR=1234,OUT=67%
```

- `LDR=1234`: Aktueller ADC-Rohwert
- `OUT=67%`: Aktuelle LED-Helligkeit in Prozent

### Erweiterte Formate (Optional)

```
STAT:LDR=1234,NORM=45,OUT=67%,MODE=AUTO
INFO:Kalibrierung gestartet
ERROR:ADC-Fehler
```

## 🐛 Debugging-Tipps

### Print-Debugging

```python
# Debug-Ausgaben für verschiedene Bereiche
DEBUG_ADC = True
DEBUG_BLE = True
DEBUG_PWM = False

if DEBUG_ADC:
    print(f"LDR: raw={raw}, norm={normalized:.2f}")
```

### Häufige Probleme

**LEDs funktionieren nicht**:
- PWM-Pins korrekt verkabelt?
- PWM-Frequenz zu hoch/niedrig? (Versuche 1000 Hz)
- duty_u16() vs. duty() je nach MicroPython-Version

**LDR reagiert nicht**:
- Spannungsteiler korrekt aufgebaut?
- ADC-Kalibrierung durchgeführt?
- ADC.ATTN_11DB für 3.3V Bereich?

**BLE verbindet nicht**:
- ESP32 in Reichweite?
- Andere BLE-Geräte stören?
- Advertising läuft? (Print-Ausgabe prüfen)

**Verhalten zu nervös**:
- EMA_ALPHA verringern (z.B. auf 0.1)
- Hauptschleife-Delay erhöhen

## 🚀 Mögliche Erweiterungen (Freiwillig)

### Mehrere LEDs parallel dimmen

```python
# Verschiedene Helligkeitskurven für kreative Effekte
def breathing_effect(base_brightness, time_factor):
    # Atmungs-Effekt implementieren
    pass

def color_temperature_effect(brightness):
    # Warmes/kaltes Licht simulieren
    pass
```

### Erweiterte BLE-Kommandos

```python
# Kommando-Parser
commands = {
    "LEVEL": lambda x: set_manual_brightness(int(x)/100),
    "MODE": lambda x: set_mode(x),
    "CALIB": lambda x: start_calibration(),
    "STATUS": lambda x: send_full_status()
}
```

### Automatische Kalibrierung

```python
def auto_calibration(duration_seconds=10):
    # Über Zeitraum min/max Werte sammeln
    # Automatisch ADC_MIN/ADC_MAX setzen
    pass
```

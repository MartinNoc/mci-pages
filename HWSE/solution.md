# Lösungen und Musterlösung

Hier findest du die Lösungen zu den Aufgaben und das vollständige Zustandsdiagramm.

## 🧠 Zustandsdiagramm-Lösung

### Vollständiges Zustandsdiagramm

```
                    [START]
                       │
                       ▼
    ┌─────────────────────────────────────┐
    │            WAITING                  │◄─────────┐
    │  • LED: aus                        │          │
    │  • Buzzer: aus                     │          │
    │  • Warte auf Button-Druck          │          │
    └─────────────────┬───────────────────┘          │
                      │ Button gedrückt              │
                      ▼                              │
    ┌─────────────────────────────────────┐          │
    │            READY                    │          │
    │  • LED: pulsiert (PWM)             │          │
    │  • Buzzer: 1 kurzer Beep           │          │
    │  • Zufällige Wartezeit (2-5s)      │          │
    └─────────┬───────────────────┬───────┘          │
              │                   │                  │
              │ Timer abgelaufen  │ Button gedrückt  │
              ▼                   ▼                  │
    ┌─────────────────┐  ┌─────────────────┐         │
    │      GO         │  │  FALSCHSTART    │─────────┘
    │  • LED: hell    │  │  • Zurück zu    │
    │  • Buzzer: 3x   │  │    WAITING      │
    │  • Reaktion!    │  └─────────────────┘
    └─────┬─────┬─────┘
          │     │
          │     │ Timeout (3s)
          │     ▼
          │  ┌─────────────────┐
          │  │    TIMEOUT      │
          │  │  • reaction_time│
          │  │    = -1         │
          │  └─────┬───────────┘
          │        │
          │ Button │
          │ gedrückt│
          ▼        ▼
    ┌─────────────────────────────────────┐
    │            RESULT                   │
    │  • LED: blinkt                     │
    │  • Buzzer: 1 langer Beep           │
    │  • Reaktionszeit anzeigen          │
    │  • 2s warten                       │
    └─────────────────┬───────────────────┘
                      │ 2s Timer
                      │ abgelaufen
                      └─────────────────────┘
```

### Ereignisse und Übergänge

| Von | Nach | Ereignis | Bedingung |
|-----|------|----------|-----------|
| WAITING | READY | Button gedrückt | `button.was_pressed()` |
| READY | GO | Timer | `elapsed >= ready_duration` |
| READY | WAITING | Button gedrückt (Falschstart) | `button.was_pressed()` |
| GO | RESULT | Button gedrückt | `button.was_pressed()` |
| GO | RESULT | Timeout | `elapsed >= 3000ms` |
| RESULT | WAITING | Timer | `elapsed >= 2000ms` |

### Variablen und Timer

- `ready_duration`: 2000-5000ms (zufällig)
- `reaction_time`: Gemessene Zeit in GO
- `state_start_time`: Zeitstempel beim Zustandswechsel

## 💻 Code-Aufgaben Lösungen

### Aufgabe 1: Timer-Test Lösung

```python
import utime
from machine import Pin

def timer_led_blink():
    """LED alle 500ms für 100ms aufleuchten lassen (non-blocking)"""
    led = Pin(2, Pin.OUT)
    
    last_blink_time = 0
    led_on_time = 0
    led_is_on = False
    
    print("Timer-LED-Test startet...")
    
    try:
        while True:
            current_time = utime.ticks_ms()
            
            # Zeit für neuen Blink-Zyklus?
            if utime.ticks_diff(current_time, last_blink_time) >= 500:
                last_blink_time = current_time
                led_on_time = current_time
                led.on()
                led_is_on = True
                print(f"LED an bei {current_time}ms")
            
            # LED nach 100ms wieder ausschalten?
            if led_is_on and utime.ticks_diff(current_time, led_on_time) >= 100:
                led.off()
                led_is_on = False
                print(f"LED aus bei {current_time}ms")
            
            utime.sleep_ms(1)  # Kurze Pause
    
    except KeyboardInterrupt:
        led.off()
        print("Test beendet")

if __name__ == "__main__":
    timer_led_blink()
```

### Aufgabe 2: Button-Counter Lösung (ohne Klassen)

```python
import utime
from machine import Pin

# Globale Variablen für Button-Counter
counter = 0
last_button_time = 0
debounce_ms = 50

def button_pressed():
    """Prüft ob Button gedrückt wurde (mit Entprellung)"""
    global last_button_time
    
    current_time = utime.ticks_ms()
    
    # Button gedrückt UND genug Zeit seit letztem Druck vergangen?
    if not button.value() and utime.ticks_diff(current_time, last_button_time) > debounce_ms:
        last_button_time = current_time
        return True
    return False

def main():
    global counter
    
    button = Pin(0, Pin.IN, Pin.PULL_UP)  # GPIO 0
    
    print("Button-Counter Test")
    print("Drücke den Button zum Zählen")
    print("Strg+C zum Beenden")
    
    try:
        while True:
            if button_pressed():
                counter += 1
                print(f"Button gedrückt! Zähler: {counter}")
            
            utime.sleep_ms(10)
    
    except KeyboardInterrupt:
        print(f"\nTest beendet. Gesamtzahl: {counter}")

if __name__ == "__main__":
    main()
```

### Aufgabe 3: PWM "Atmen" Lösung (ohne Klassen)

```python
import utime
import math
from machine import Pin, PWM

# Globale Variablen für LED-Atmung
led_phase = 0
speed = 0.05  # Geschwindigkeit der Atmung

def update_breathing_led():
    """LED-Atmung updaten"""
    global led_phase
    
    # Sinuswelle von 0 bis 1
    sine_value = (math.sin(led_phase) + 1) / 2
    
    # Auf PWM-Bereich (0-1023) skalieren
    brightness = int(sine_value * 1023)
    led_pwm.duty(brightness)
    
    # Phase für nächsten Durchlauf
    led_phase += speed
    if led_phase > 2 * math.pi:
        led_phase = 0

def main():
    global led_pwm
    
    led_pwm = PWM(Pin(2))
    led_pwm.freq(1000)
    
    print("LED 'Atmung' Demo")
    print("LED atmet sanft auf und ab")
    print("Strg+C zum Beenden")
    
    try:
        while True:
            update_breathing_led()
            utime.sleep_ms(20)  # 50 FPS
    
    except KeyboardInterrupt:
        led_pwm.duty(0)
        print("\nDemo beendet")

if __name__ == "__main__":
    main()
```

## 🔧 Hardware-Troubleshooting

### LED-Probleme

**Problem:** LED leuchtet nicht
```python
# Debug-Code für LED
from machine import Pin, PWM

def debug_led():
    # Test 1: Einfache digitale Ausgabe
    led_digital = Pin(2, Pin.OUT)
    led_digital.on()
    print("LED sollte jetzt leuchten (digital)")
    
    # Test 2: PWM mit verschiedenen Helligkeiten
    led_pwm = PWM(Pin(2))
    led_pwm.freq(1000)
    
    for brightness in [256, 512, 768, 1023]:
        led_pwm.duty(brightness)
        print(f"LED Helligkeit: {brightness}/1023")
        utime.sleep(1)
    
    led_pwm.duty(0)
```

**Mögliche Ursachen:**
- Falsche Polarität (Anode/Kathode vertauscht)
- Defekter Widerstand
- Lockere Verbindung
- GPIO-Pin bereits von anderem Code verwendet

### Button-Probleme

**Problem:** Button reagiert nicht oder unzuverlässig
```python
# Debug-Code für Button
from machine import Pin
import utime

def debug_button():
    button = Pin(0, Pin.IN, Pin.PULL_UP)
    
    print("Button-Debug:")
    print("Drücke und halte den Button...")
    
    for _ in range(100):  # 10 Sekunden Test
        value = button.value()
        print(f"Button-Wert: {value} {'(GEDRÜCKT)' if value == 0 else '(NICHT GEDRÜCKT)'}")
        utime.sleep(0.1)
```

**Mögliche Ursachen:**
- Pull-up Widerstand fehlt oder falsch
- Button-Pins vertauscht
- Mechanischer Defekt des Buttons
- Interferenz durch andere Signale

### Buzzer-Probleme

**Problem:** Buzzer macht keinen Ton
```python
# Debug-Code für Buzzer
from machine import Pin, PWM
import utime

def debug_buzzer():
    buzzer = PWM(Pin(4))
    
    # Test verschiedene Frequenzen
    frequencies = [100, 500, 1000, 2000, 3000]
    
    for freq in frequencies:
        print(f"Teste Frequenz: {freq}Hz")
        buzzer.freq(freq)
        buzzer.duty(512)  # 50% Duty Cycle
        utime.sleep(0.5)
        buzzer.duty(0)
        utime.sleep(0.2)
    
    print("Buzzer-Test beendet")
```

**Mögliche Ursachen:**
- Falsche Polarität
- Zu niedrige Frequenz (<500Hz)
- Duty Cycle zu niedrig
- Passiver statt aktiver Buzzer (braucht PWM)

## ⚡ Performance-Optimierung

### Timing-Optimierung

```python
# Schlecht: Viele kleine sleep() Aufrufe
def bad_timing():
    while True:
        # Viel Code hier
        utime.sleep_ms(1)  # Sehr kleine Pause

# Besser: Adaptive Sleep-Zeit
def better_timing():
    target_fps = 50  # 50 Updates pro Sekunde
    target_delay = 1000 // target_fps  # 20ms
    
    while True:
        start_time = utime.ticks_ms()
        
        # Hauptlogik hier
        game.update()
        
        # Berechne wie lange das Update gedauert hat
        update_time = utime.ticks_diff(utime.ticks_ms(), start_time)
        
        # Nur warten wenn nötig
        remaining_time = target_delay - update_time
        if remaining_time > 0:
            utime.sleep_ms(remaining_time)
```

### Speicher-Optimierung

```python
# Problematisch: Unbegrenzte Listen
class BadStatistics:
    def __init__(self):
        self.all_times = []  # Wird immer größer!
    
    def add_time(self, time):
        self.all_times.append(time)

# Besser: Ringpuffer
class GoodStatistics:
    def __init__(self, max_history=100):
        self.times = [0] * max_history
        self.index = 0
        self.count = 0
        self.max_history = max_history
    
    def add_time(self, time):
        self.times[self.index] = time
        self.index = (self.index + 1) % self.max_history
        if self.count < self.max_history:
            self.count += 1
    
    def get_average(self):
        if self.count == 0:
            return 0
        return sum(self.times[:self.count]) / self.count
```

## 🎯 Bewertungskriterien

### Grundfunktionalität (60%)
- ✅ Alle 4 Zustände implementiert
- ✅ LED-Modi funktionieren korrekt  
- ✅ Button-Entprellung funktioniert
- ✅ Zeitmessung ist präzise
- ✅ Falschstart-Erkennung

### Code-Qualität (25%)
- ✅ Strukturierter, lesbarer Code
- ✅ Sinnvolle Klasseneinteilung
- ✅ Aussagekräftige Variablennamen
- ✅ Kommentare an wichtigen Stellen
- ✅ Keine blocking Operations

### Erweiterungen (15%)
Mindestens eine der folgenden Erweiterungen:
- ✅ High-Score System
- ✅ RGB-LED Unterstützung
- ✅ Mehrspielermodus
- ✅ Verschiedene Schwierigkeitsgrade
- ✅ Persistente Statistiken
- ✅ Audio-Feedback Verbesserungen

## 📝 Häufige Fehler

### 1. Blocking Code
```python
# FALSCH: Blockiert das gesamte System
def wrong_ready_state(self):
    self.led.on()
    time.sleep(3)  # Blockiert!
    self.change_state(STATE_GO)

# RICHTIG: Non-blocking mit Timer
def correct_ready_state(self):
    elapsed = utime.ticks_diff(utime.ticks_ms(), self.state_start_time)
    if elapsed >= self.ready_duration:
        self.change_state(STATE_GO)
```

### 2. Fehlende Entprellung
```python
# FALSCH: Direkte Button-Abfrage
if not button.value():  # Kann mehrmals triggern!

# RICHTIG: Mit Entprellung
if button.was_pressed():  # Nur einmal pro Druck
```

### 3. Falsche Zeitmessung
```python
# FALSCH: time.time() verwenden
import time
start = time.time()

# RICHTIG: utime.ticks_ms() für Mikrocontroller
import utime
start = utime.ticks_ms()
elapsed = utime.ticks_diff(utime.ticks_ms(), start)
```

### 4. Unendliche Loops ohne Pause
```python
# FALSCH: 100% CPU-Last
while True:
    game.update()  # Keine Pause!

# RICHTIG: Mit kleiner Pause
while True:
    game.update()
    utime.sleep_ms(10)  # CPU entlasten
```

## 🏆 Performance-Metriken

### Reaktionszeiten-Benchmark
- **Excellent:** < 200ms
- **Very Good:** 200-300ms  
- **Good:** 300-450ms
- **Average:** 450-600ms
- **Needs Practice:** > 600ms

### System-Performance
- **Update-Rate:** ~50-100 Hz (10-20ms pro Cycle)
- **Button-Latenz:** < 50ms (durch Entprellung)
- **LED-Latenz:** < 20ms
- **Speicherverbrauch:** < 50KB für Basis-Version

Glückwunsch! Du hast das vollständige Reaktionsspiel-Tutorial durchgearbeitet! 🎉

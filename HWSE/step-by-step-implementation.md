# Schritt-für-Schritt Implementation

Jetzt bauen wir unser Reaktionsspiel Schritt für Schritt auf. Wir beginnen mit einer einfachen Version und erweitern sie systematisch.

**Wichtig:** Wir verwenden einfache Funktionen statt Klassen, um es für Anfänger verständlicher zu machen.

## 🏗️ Entwicklungsplan

1. **[Schritt 1: Grundgerüst](#schritt-1-grundgerüst)** - Hardware-Setup und einfacher Zustandsautomat mit Funktionen
2. **[Schritt 2: LED-Steuerung](#schritt-2-led-steuerung)** - PWM und LED-Modi implementieren
3. **[Schritt 3: Button-Handling](#schritt-3-button-handling)** - Einfache Entprellung und Eingabeverarbeitung
4. **[Schritt 4: Zufallszeiten](#schritt-4-zufallszeiten)** - Unvorhersagbare Wartezeiten
5. **[Schritt 5: Buzzer-Integration](#schritt-5-buzzer-integration)** - Audio-Feedback hinzufügen
6. **[Schritt 6: Vollständiges Spiel](#schritt-6-vollständiges-spiel)** - Alles zusammenfügen

## ⚠️ Wichtiger Hinweis: `utime` vs `time`

In unseren Programmen verwenden wir **`utime`** statt `time`:

```python
# SCHLECHT für Mikrocontroller:
import time
time.sleep(3)  # Blockiert das gesamte System für 3 Sekunden!

# GUT für Mikrocontroller:
import utime
start = utime.ticks_ms()
# ... anderer Code kann laufen ...
if utime.ticks_diff(utime.ticks_ms(), start) >= 3000:
    print("3 Sekunden vergangen!")
```

**Warum `utime`?**
- **Non-blocking**: Andere Teile des Programms können weiterlaufen
- **Präziser**: Millisekunden-Genauigkeit
- **Embedded-optimiert**: Speziell für Mikrocontroller entwickelt

---

## Schritt 1: Grundgerüst

Wir starten mit einem minimalen Zustandsautomaten **ohne Klassen**.

### 📄 Code: [step1_basic_states.py](step1_basic_states.py)

**Neue Struktur:**
```python
# Globale Variablen für Zustand
current_state = STATE_WAITING
state_start_time = 0

# Hardware (global)
led = Pin(2, Pin.OUT)
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Einfache Funktionen
def change_state(new_state):
    global current_state, state_start_time
    # ...

def button_pressed():
    # Einfache Entprellung
    # ...

def update_waiting():
    # WAITING Zustand
    # ...
```

### 🧪 Test Schritt 1
1. Lade den Code auf deinen ESP32
2. Teste die grundlegenden Zustandsübergänge
3. Prüfe, ob die Reaktionszeitmessung funktioniert

### ✅ Erwartetes Verhalten:
- System startet in WAITING (LED aus)
- Button-Druck → READY (LED an, 3s warten)
- Automatisch → GO (LED an)
- Button-Druck → RESULT (LED blinkt, Reaktionszeit ausgeben)
- Nach 2s → WAITING

---

## Schritt 2: LED-Steuerung

Wir verbessern die LED-Steuerung mit PWM für sanftes Pulsieren.

### 📄 Code: [step2_led_control.py](step2_led_control.py)

**Wichtige Änderungen:**
```python
# PWM statt einfache GPIO
led_pwm = PWM(Pin(2))
led_pwm.freq(1000)

# LED-Modi (global)
led_mode = "off"  # "off", "pulse", "on", "blink"
led_phase = 0

def set_led_mode(mode):
    global led_mode, led_phase
    led_mode = mode
    if mode == "off":
        led_pwm.duty(0)
    elif mode == "on":
        led_pwm.duty(1023)
    # ...

def update_led():
    global led_phase
    if led_mode == "pulse":
        # Sinuswelle für Pulsieren
        brightness = int(300 + 200 * math.sin(led_phase))
        led_pwm.duty(brightness)
        led_phase += 0.15
    # ...
```

### 🧪 Test Schritt 2
1. Beobachte das sanfte Pulsieren in READY
2. Prüfe das helle Leuchten in GO
3. Teste das Blinken in RESULT

---

## Schritt 3: Button-Handling

Jetzt implementieren wir ordentliche Button-Entprellung (einfache Variante).

### 📄 Code: [step3_button_debounce.py](step3_button_debounce.py)

**Einfache Entprellung:**
```python
# Globale Variablen für Entprellung
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
```

**Alternative mit Interrupts (fortgeschritten):**

Basierend auf dem Beispiel von Random Nerd Tutorials:

```python
from machine import Pin, Timer

counter = 0
debounce_timer = None

def button_pressed(pin):
    global counter, debounce_timer
    
    if debounce_timer is None:  # Nur wenn kein Timer läuft
        counter += 1
        print("Button Pressed! Count:", counter)
        
        # Timer für Entprellung starten
        debounce_timer = Timer(1)
        debounce_timer.init(mode=Timer.ONE_SHOT, period=200, callback=debounce_callback)

def debounce_callback(timer):
    global debounce_timer
    debounce_timer = None  # Timer beenden

# Interrupt anhängen
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)
```

### 🧪 Test Schritt 3
1. Teste die Entprellung: Drücke den Button schnell mehrmals
2. Prüfe die Zufallszeiten in READY
3. Teste das "zu früh drücken" Feature

---

## Schritt 4: Zufallszeiten

Unvorhersagbare Wartezeiten machen das Spiel fairer.

```python
import urandom

# In update_ready():
def change_state_to_ready():
    global ready_duration
    # Zufällige Zeit zwischen 2-5 Sekunden
    ready_duration = 2000 + urandom.getrandbits(12) % 3001
    print(f"Warte {ready_duration}ms...")
```

---

## Schritt 5: Buzzer-Integration

Audio-Feedback für bessere Benutzererfahrung.

### 📄 Code: [step5_buzzer_audio.py](step5_buzzer_audio.py)

**Einfache Buzzer-Steuerung:**
```python
buzzer = PWM(Pin(4))

# Globale Variablen für Timer
buzzer_stop_time = 0
buzzer_active = False

def beep(frequency=1000, duration_ms=200):
    """Kurzen Piep abspielen"""
    global buzzer_stop_time, buzzer_active
    
    buzzer.freq(frequency)
    buzzer.duty(512)  # 50% Duty Cycle
    buzzer_stop_time = utime.ticks_ms() + duration_ms
    buzzer_active = True

def update_buzzer():
    """Buzzer updaten (in Hauptschleife aufrufen)"""
    global buzzer_active
    
    if buzzer_active and utime.ticks_ms() >= buzzer_stop_time:
        buzzer.duty(0)
        buzzer_active = False
```

---

## Schritt 6: Vollständiges Spiel

Die finale Version mit allen Features!

### 📄 Code: [step6_complete_game.py](step6_complete_game.py)

Diese Datei enthält die vollständige Implementation mit:
- ✅ Allen vier Zuständen (funktional, ohne Klassen)
- ✅ PWM LED-Steuerung  
- ✅ Einfache Button-Entprellung
- ✅ Präziser Zeitmessung mit `utime`
- ✅ Audio-Feedback
- ✅ Fehlerbehandlung
- ✅ Benutzerfreundliche Ausgaben

**Hauptschleife (vereinfacht):**
```python
def main():
    while True:
        # Hardware-Updates
        update_led()
        update_buzzer()
        
        # Zustandslogik
        if current_state == STATE_WAITING:
            update_waiting()
        elif current_state == STATE_READY:
            update_ready()
        elif current_state == STATE_GO:
            update_go()
        elif current_state == STATE_RESULT:
            update_result()
        
        utime.sleep_ms(10)  # 10ms Update-Rate
```

## 🎯 Deine Aufgaben

### Aufgabe 1: Code verstehen
Arbeite dich durch jeden Schritt und verstehe:
- Wie funktioniert die Zustandsmaschine ohne Klassen?
- Warum verwenden wir `utime.ticks_ms()` statt `time.sleep()`?
- Wie funktioniert die einfache Button-Entprellung?

### Aufgabe 2: Einfache Erweiterungen
Implementiere mindestens eine dieser Erweiterungen:
- **Längere Statistiken**: Zähle die letzten 10 Spielzeiten
- **Verschiedene Töne**: Andere Frequenzen für verschiedene Ergebnisse
- **Erweiterte LED-Modi**: Schnelleres/langsameres Blinken je nach Ergebnis
- **Difficulty-Modi**: Kürzere/längere Timeouts

### Aufgabe 3: Debugging
Was passiert wenn...?
- Du `time.sleep()` statt `utime` verwendest?
- Die Button-Entprellung zu kurz ist?
- Du die Update-Rate auf 100ms erhöhst?

## 🚀 Nächster Schritt

Wenn du alle Schritte durchgearbeitet hast, teste dein Spiel ausgiebig mit den [Test-Übungen](test-exercises.md)!

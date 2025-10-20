# Reaktionsspiel mit ESP32 und MicroPython

Willkommen zum Tutorial! In dieser Online-Lesson entwickelst du Schritt für Schritt ein Reaktionsspiel mit dem ESP32 Microcontroller und MicroPython.

## 🎯 Was du lernen wirst

- Zustandsautomaten in embedded Systemen verstehen und implementieren
- Hardware-Komponenten (LEDs, Buttons, Buzzer) mit MicroPython steuern
- Timer und Zeitmessung für präzise Timing-Anwendungen
- PWM für LED-Helligkeitssteuerung verwenden
- Button-Entprellung implementieren
- Strukturierte Programmierung in MicroPython

## 🎮 Das Reaktionsspiel

Du entwickelst ein interaktives Spiel, bei dem Spieler:innen so schnell wie möglich auf ein LED-Signal reagieren müssen. Das Spiel misst die Reaktionszeit und gibt audio-visuelles Feedback.

### Spielablauf:
1. **WAITING**: Das Spiel wartet auf den Start
2. **READY**: Nach dem Drücken des Buttons wartet das Spiel eine zufällige Zeit (2-5 Sekunden)
3. **GO**: Die LED leuchtet auf - jetzt muss schnell reagiert werden!
4. **RESULT**: Die Reaktionszeit wird angezeigt und das Spiel kehrt zum Anfang zurück

## 📋 Tutorial-Struktur

Dieses Tutorial ist in mehrere Abschnitte unterteilt:

1. **[Hardware Setup](#hardware-setup)** - Schaltung aufbauen und Komponenten verstehen
2. **[Zustandsdiagramm-Aufgabe](#zustandsdiagramm-aufgabe)** - Das System als Zustandsautomat modellieren
3. **[MicroPython Grundlagen](#micropython-grundlagen-für-esp32-wiederholung)** - Grundlagen für ESP32 Programmierung
4. **[Schritt-für-Schritt Implementation](#schritt-für-schritt-implementation)** - Das Spiel entwickeln
5. **[Tests & Erweiterungen](#test-übungen-und-erweiterungen)** - Das System testen und erweitern

## 🚀 Los geht's!

Starte mit dem [Hardware Setup](#hardware-setup) und arbeite dich durch die einzelnen Abschnitte. Jeder Abschnitt baut auf dem vorherigen auf, deshalb ist es wichtig, die Reihenfolge einzuhalten.

Viel Spaß beim Programmieren!

# Hardware Setup

## 🔧 Kurze Wiederholung: Benötigte Komponenten

Da wir die Hardware-Grundlagen bereits behandelt haben, hier eine kurze Wiederholung der Schaltung für unser Reaktionsspiel:

| Komponente | GPIO Pin | Beschreibung |
|------------|----------|--------------|
| LED | GPIO 2 | Signallicht (mit 220Ω Widerstand) |
| Button | GPIO 0 | Start/Reaktions-Eingabe (mit Pull-up) |
| Buzzer | GPIO 4 | Audio-Feedback |

## 🔌 Schaltplan (Kurzfassung)

```
LED:    GPIO 2 → 220Ω → LED(+) → LED(-) → GND
Button: GPIO 0 → Button → GND (+ Pull-up zu 3.3V)
Buzzer: GPIO 4 → Buzzer(+) → Buzzer(-) → GND
```

## 🧪 Schneller Hardware-Test

Falls du die Schaltung neu aufbaust, teste sie kurz:

```python
from machine import Pin, PWM
import time

# Komponenten initialisieren
led = Pin(2, Pin.OUT)
button = Pin(0, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(4))

# Kurzer Test
print("LED Test...")
led.on()
time.sleep(1)
led.off()

print("Button Test - drücke Button...")
for _ in range(50):  # 5 Sekunden
    if not button.value():
        print("Button gedrückt!")
        break
    time.sleep(0.1)

print("Buzzer Test...")
buzzer.freq(1000)
buzzer.duty(512)
time.sleep(0.3)
buzzer.duty(0)

print("Hardware-Test abgeschlossen!")
```

## 🎯 Nächster Schritt

Hardware funktioniert? Dann weiter zur [Zustandsdiagramm-Aufgabe](#zustandsdiagramm-aufgabe)!


# Zustandsdiagramm-Aufgabe

Bevor wir mit der Programmierung beginnen, modellieren wir unser Reaktionsspiel als **Zustandsautomat**. Das hilft uns, das Verhalten des Systems zu verstehen und strukturiert zu programmieren.

## 🧠 Was ist ein Zustandsautomat?

Ein Zustandsautomat beschreibt ein System durch:
- **Zustände**: Verschiedene Betriebsmodi
- **Übergänge**: Bedingungen zum Wechsel zwischen Zuständen  
- **Ereignisse**: Auslöser für Zustandsübergänge
- **Aktionen**: Was in jedem Zustand passiert

## 🎮 Unser Reaktionsspiel

Basierend auf der Aufgabenstellung hat unser Spiel vier Zustände:

### Zustandstabelle

| Zustand | LED-Verhalten | Buzzer | Beschreibung |
|---------|---------------|--------|--------------|
| **WAITING** | LED aus | aus | Spiel bereit, wartet auf Start |
| **READY** | LED pulsiert langsam (PWM) | 1 kurzer Beep | Zufällige Wartezeit (2–5 s) |
| **GO** | LED leuchtet hell | 3 kurze Beeps | Spieler soll so schnell wie möglich drücken |
| **RESULT** | LED blinkt | 1 langer Beep | Zeigt Reaktionszeit oder Timeout an |

## 📝 Aufgabe: Zeichne das Zustandsdiagramm

**Deine Aufgabe:** Zeichne das Zustandsdiagramm für das Reaktionsspiel auf Papier oder digital.

### Hilfestellung:

#### Zustände (als Kreise/Ellipsen):
- WAITING
- READY  
- GO
- RESULT

#### Übergänge (als Pfeile mit Beschriftung):
Überlege dir, welche **Ereignisse** oder **Bedingungen** zu einem Zustandswechsel führen:

- Button gedrückt?
- Timer abgelaufen?
- Timeout erreicht?
- Bereit für neues Spiel?

#### Fragen zum Nachdenken:
1. In welchem Zustand startet das System?
2. Was passiert, wenn der Button zu früh gedrückt wird (in READY)?
3. Was passiert, wenn der Button zu spät gedrückt wird (Timeout)?
4. Wie kommt das System zurück zum Anfang?

### Beispiel-Struktur:
```
[START] → [WAITING] → [READY] → [GO] → [RESULT] → [WAITING]
             ↑                              ↓
             └──────── (zurück zum Start) ───┘
```

## 🔍 Erweiterte Überlegungen

### Timing-Ereignisse:
- **ready_timer**: Zufällige Wartezeit in READY (2-5 Sekunden)
- **timeout_timer**: Maximale Reaktionszeit in GO (z.B. 3 Sekunden)
- **result_timer**: Anzeigezeit für Ergebnis (2-3 Sekunden)

### Fehlerbehandlung:
- Was passiert bei zu frühem Drücken?
- Wie gehst du mit Timeouts um?
- Soll es eine "Falschstart"-Meldung geben?

## 🎯 Selbstcheck

Beantworte diese Fragen mit deinem Diagramm:

1. **Startzustand**: Wo beginnt das Spiel?
2. **Button in WAITING**: Was passiert beim ersten Button-Druck?
3. **Timer in READY**: Wie wechselt das System automatisch zu GO?
4. **Button in GO**: Wie wird die Reaktionszeit gemessen?
5. **Timeout**: Was passiert, wenn nicht rechtzeitig reagiert wird?
6. **Zurück zum Start**: Wie kehrt das System zu WAITING zurück?

## 📋 Arbeitsblatt

Zeichne dein Zustandsdiagramm hier (auf Papier oder digital):

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Platz für dein Zustandsdiagramm                           │
│                                                             │
│  Tipp: Verwende Kreise für Zustände und Pfeile für         │
│        Übergänge. Beschrifte die Pfeile mit den           │
│        Bedingungen für den Übergang.                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Überprüfung

Wenn du dein Zustandsdiagramm gezeichnet hast, vergleiche es mit der [Musterlösung](#lösungen-und-musterlösung) am Ende des Tutorials.

Keine Sorge, wenn dein Diagramm anders aussieht - es gibt verschiedene korrekte Darstellungsweisen!

## 🚀 Nächster Schritt

Hast du dein Zustandsdiagramm erstellt? Dann geht es weiter mit den [MicroPython Grundlagen](#micropython-grundlagen-für-esp32-wiederholung), wo wir die technischen Grundlagen für die Implementation lernen.


# MicroPython Grundlagen für ESP32 (Wiederholung)

In diesem Abschnitt lernst du die wichtigsten MicroPython-Konzepte für unser Reaktionsspiel.

## MicroPython auf ESP32

MicroPython ist eine schlanke Python-Implementation für Microcontroller. Der ESP32 unterstützt die meisten Python-Features, die wir brauchen.

## Wichtige Module für unser Projekt

### 1. `machine` - Hardware-Steuerung

Das `machine`-Modul ist das Herzstück für Hardware-Interaktion:

```python
from machine import Pin, PWM
import time

# GPIO als Ausgang (LED)
led = Pin(2, Pin.OUT)
led.on()   # LED an
led.off()  # LED aus

# GPIO als Eingang (Button)
button = Pin(0, Pin.IN, Pin.PULL_UP)
print(button.value())  # 1 = nicht gedrückt, 0 = gedrückt

# PWM für variable Helligkeit
led_pwm = PWM(Pin(2))
led_pwm.freq(1000)      # 1 kHz Frequenz
led_pwm.duty(512)       # 50% Helligkeit (0-1023)
```

### 2. `utime` vs `time` - Wichtiger Unterschied!

**Warum `utime` statt `time`?**

```python
# time - Standard Python (auch in MicroPython verfügbar)
import time
time.sleep(1)  # Blockiert 1 Sekunde - PROBLEMATISCH für Embedded!

# utime - MicroPython optimiert für Microcontroller
import utime
start = utime.ticks_ms()  # Millisekunden-Zeitstempel
# ... andere Arbeit ...
elapsed = utime.ticks_diff(utime.ticks_ms(), start)  # Non-blocking!
```

**Warum `utime` besser ist:**
- **Non-blocking**: Programm kann währenddessen andere Dinge tun
- **Präziser**: Millisekunden-Genauigkeit
- **Embedded-optimiert**: Für Microcontroller entwickelt

### 3. Non-blocking Timer implementieren

**Schlecht - blockierend:**
```python
# NICHT SO! Blockiert das gesamte System
def bad_wait():
    time.sleep(3)  # 3 Sekunden nichts anderes möglich
    print("Fertig")
```

**Gut - non-blocking:**
```python
import utime

# Globale Variable für Timer
timer_start = 0
timer_duration = 3000  # 3 Sekunden in Millisekunden

def start_timer():
    global timer_start
    timer_start = utime.ticks_ms()

def is_timer_expired():
    global timer_start, timer_duration
    if timer_start == 0:
        return False
    elapsed = utime.ticks_diff(utime.ticks_ms(), timer_start)
    return elapsed >= timer_duration

# Verwendung in Hauptschleife:
start_timer()
while True:
    if is_timer_expired():
        print("Timer abgelaufen!")
        break
    # Hier kann anderer Code laufen!
    utime.sleep_ms(10)
```

### 4. Button-Entprellung (Einfache Variante)

Mechanische Buttons "prellen" - sie senden mehrere Signale beim Drücken:

```python
import utime

# Globale Variablen für Entprellung
last_button_time = 0
button_debounce_ms = 50

def button_pressed():
    """Prüft ob Button gedrückt wurde (mit Entprellung)"""
    global last_button_time
    
    current_time = utime.ticks_ms()
    
    # Button gedrückt UND genug Zeit seit letztem Druck vergangen?
    if not button.value() and utime.ticks_diff(current_time, last_button_time) > button_debounce_ms:
        last_button_time = current_time
        return True
    return False

# Verwendung:
button = Pin(0, Pin.IN, Pin.PULL_UP)

while True:
    if button_pressed():
        print("Button gedrückt!")
    utime.sleep_ms(10)
```

### 5. PWM für LED-Effekte

```python
import utime
import math

# LED mit PWM für variable Helligkeit
led_pwm = PWM(Pin(2))
led_pwm.freq(1000)

# Einfaches Pulsieren
def pulse_led():
    phase = 0
    while True:
        # Sinuswelle für sanftes Pulsieren
        brightness = int(512 + 300 * math.sin(phase))
        led_pwm.duty(brightness)
        phase += 0.1
        if phase > 2 * math.pi:
            phase = 0
        utime.sleep_ms(50)
```

### 6. Buzzer-Steuerung

```python
# Buzzer für Audio-Feedback
buzzer = PWM(Pin(4))

def beep(frequency=1000, duration_ms=200):
    """Kurzen Piep abspielen"""
    buzzer.freq(frequency)
    buzzer.duty(512)  # 50% Duty Cycle
    utime.sleep_ms(duration_ms)
    buzzer.duty(0)    # Aus

# Verschiedene Töne
beep(800, 150)   # Kurzer, tiefer Ton
beep(1200, 100)  # Kurzer, hoher Ton
beep(600, 500)   # Langer, tiefer Ton
```

## 🔄 Zustandsautomat - Funktionaler Ansatz

```python
import utime
from machine import Pin, PWM

# Zustände als Konstanten
STATE_WAITING = 0
STATE_READY = 1
STATE_GO = 2
STATE_RESULT = 3

# Globale Zustandsvariablen
current_state = STATE_WAITING
state_start_time = 0
ready_duration = 0
reaction_time = 0

# Hardware initialisieren
led = Pin(2, Pin.OUT)
button = Pin(0, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(4))

# Button-Entprellung
last_button_time = 0

def change_state(new_state):
    """Zustand wechseln"""
    global current_state, state_start_time
    
    state_names = ["WAITING", "READY", "GO", "RESULT"]
    print(f"State: {state_names[current_state]} → {state_names[new_state]}")
    
    current_state = new_state
    state_start_time = utime.ticks_ms()

def button_pressed():
    """Button mit Entprellung prüfen"""
    global last_button_time
    
    current_time = utime.ticks_ms()
    if not button.value() and utime.ticks_diff(current_time, last_button_time) > 50:
        last_button_time = current_time
        return True
    return False

def update_waiting():
    """WAITING Zustand"""
    led.off()
    if button_pressed():
        change_state(STATE_READY)

def update_ready():
    """READY Zustand"""
    led.on()  # Später: Pulsieren
    
    # Zu früh gedrückt?
    if button_pressed():
        print("Zu früh gedrückt!")
        change_state(STATE_WAITING)
        return
    
    # Wartezeit abgelaufen?
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= ready_duration:
        change_state(STATE_GO)

def update_go():
    """GO Zustand"""
    global reaction_time
    
    led.on()  # Hell
    
    if button_pressed():
        reaction_time = utime.ticks_diff(utime.ticks_ms(), state_start_time)
        print(f"Reaktionszeit: {reaction_time}ms")
        change_state(STATE_RESULT)
        return
    
    # Timeout nach 3 Sekunden
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= 3000:
        print("Timeout!")
        change_state(STATE_RESULT)

def update_result():
    """RESULT Zustand"""
    # LED blinken
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if (elapsed // 300) % 2:
        led.on()
    else:
        led.off()
    
    # Nach 2 Sekunden zurück
    if elapsed >= 2000:
        change_state(STATE_WAITING)

# Hauptschleife
def main_loop():
    while True:
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

## 🎯 Wichtige Prinzipien

1. **Verwende `utime` statt `time`** für bessere Embedded-Performance
2. **Niemals `time.sleep()` in Hauptschleife** - immer non-blocking programmieren
3. **Button-Entprellung ist wichtig** - sonst mehrfache Erkennungen
4. **Kleine Update-Zyklen** (10-20ms) für responsive Programme
5. **Globale Variablen sind okay** - für einfache Mikrocontroller-Programme

## 🚀 Nächster Schritt

Jetzt kennst du die Grundlagen! Im nächsten Abschnitt setzen wir alles zusammen: [Schritt-für-Schritt Implementation](#schritt-für-schritt-implementation)

# Schritt-für-Schritt Implementation

Jetzt bauen wir unser Reaktionsspiel Schritt für Schritt auf. Wir beginnen mit einer einfachen Version und erweitern sie systematisch.

## 🏗️ Entwicklungsplan

1. **[Schritt 1: Grundgerüst](#schritt-1-grundgerüst)** - Hardware-Setup und einfacher Zustandsautomat mit Funktionen
2. **[Schritt 2: LED-Steuerung](#schritt-2-led-steuerung)** - PWM und LED-Modi implementieren
3. **[Schritt 3: Button-Handling](#schritt-3-button-handling)** - Einfache Entprellung und Eingabeverarbeitung
4. **[Schritt 4: Zufallszeiten](#schritt-4-zufallszeiten)** - Unvorhersagbare Wartezeiten
5. **[Schritt 5: Buzzer-Integration](#schritt-5-buzzer-integration)** - Audio-Feedback hinzufügen
6. **[Schritt 6: Vollständiges Spiel](#schritt-6-vollständiges-spiel)** - Alles zusammenfügen

## Hinweis: `utime` vs `time`

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

Wir starten mit einem minimalen Zustandsautomaten.

### Code: [step1_basic_states.py](step1_basic_states.py)

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

### Code: [step2_led_control.py](step2_led_control.py)

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

### Code: [step3_button_debounce.py](step3_button_debounce.py)

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

### Code: [step5_buzzer_audio.py](step5_buzzer_audio.py)

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

### Code: [step6_complete_game.py](step6_complete_game.py)

Diese Datei enthält die vollständige Implementation mit:
- ✅ Allen vier Zuständen
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
- Wie funktioniert die Zustandsmaschine?
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

Wenn du alle Schritte durchgearbeitet hast, teste dein Spiel ausgiebig mit den [Test-Übungen](#test-übungen-und-erweiterungen)!

# Test-Übungen und Erweiterungen

Nach der Implementierung des Reaktionsspiels ist es Zeit, das System zu testen und zu erweitern. Hier findest du verschiedene Aufgaben und Experimente.

## 🧪 Grundlegende Tests

### Test 1: Hardware-Funktionstest
Bevor du das Spiel testest, prüfe jede Hardware-Komponente einzeln:

```python
# LED-Test
from machine import Pin, PWM
import utime

led = PWM(Pin(2))
led.freq(1000)

# LED von dunkel zu hell
for brightness in range(0, 1024, 10):
    led.duty(brightness)
    utime.sleep_ms(20)
```

**Aufgabe:** Teste alle Hardware-Komponenten einzeln und dokumentiere mögliche Probleme.

### Test 2: Button-Entprellung testen
```python
# Button-Prelltest
from machine import Pin
import utime

button = Pin(0, Pin.IN, Pin.PULL_UP)
last_state = 1
press_count = 0

print("Drücke Button schnell mehrmals...")

for _ in range(1000):  # 10 Sekunden Test
    current_state = button.value()
    if current_state != last_state and current_state == 0:
        press_count += 1
        print(f"Press {press_count}")
    last_state = current_state
    utime.sleep_ms(10)
```

**Aufgabe:** Vergleiche mit und ohne Entprellung. Wie viele "falsche" Drücke erkennst du?

### Test 3: Timing-Genauigkeit
```python
# Timer-Genauigkeitstest
import utime

def timing_test(expected_ms):
    start = utime.ticks_ms()
    utime.sleep_ms(expected_ms)
    actual = utime.ticks_diff(utime.ticks_ms(), start)
    error = abs(actual - expected_ms)
    print(f"Erwartet: {expected_ms}ms, Gemessen: {actual}ms, Fehler: {error}ms")

for delay in [100, 500, 1000, 2000]:
    timing_test(delay)
```

**Aufgabe:** Wie genau ist die Zeitmessung? Warum gibt es Abweichungen?

## 🎮 Spieltests

### Test 4: Reaktionszeit-Statistiken
Führe das Spiel 20 Mal aus und sammle Daten:

```python
# Statistik-Sammlung (erweitere das Hauptspiel)
reaction_times = []
false_starts = 0

# Nach jedem Spiel:
if reaction_time > 0:
    reaction_times.append(reaction_time)

# Statistiken berechnen
if reaction_times:
    average = sum(reaction_times) / len(reaction_times)
    minimum = min(reaction_times)
    maximum = max(reaction_times)
    print(f"Durchschnitt: {average:.1f}ms")
    print(f"Beste Zeit: {minimum}ms")
    print(f"Schlechteste Zeit: {maximum}ms")
```

**Aufgabe:** Sammle Daten von 20 Spielen und analysiere:
- Wird deine Reaktionszeit mit der Zeit besser?
- Wie konsistent sind deine Zeiten?
- Wann machst du die meisten Falschstarts?

### Test 5: Verschiedene Wartezeiten
Teste das Spiel mit verschiedenen Einstellungen:

```python
# Verschiedene Schwierigkeitsgrade
DIFFICULTY_EASY   = (3000, 6000)  # 3-6 Sekunden Wartezeit
DIFFICULTY_MEDIUM = (2000, 5000)  # 2-5 Sekunden (Standard)
DIFFICULTY_HARD   = (1000, 3000)  # 1-3 Sekunden
DIFFICULTY_EXPERT = (500, 2000)   # 0.5-2 Sekunden
```

**Aufgabe:** Welche Wartezeit ist optimal? Wann machst du die meisten Fehler?

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
    │  • LED: aus                         │          │
    │  • Buzzer: aus                      │          │
    │  • Warte auf Button-Druck           │          │
    └─────────────────┬───────────────────┘          │
                      │ Button gedrückt              │
                      ▼                              │
    ┌─────────────────────────────────────┐          │
    │            READY                    │          │
    │  • LED: pulsiert (PWM)              │          │
    │  • Buzzer: 1 kurzer Beep            │          │
    │  • Zufällige Wartezeit (2-5s)       │          │
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
    │  • LED: blinkt                      │
    │  • Buzzer: 1 langer Beep            │
    │  • Reaktionszeit anzeigen           │
    │  • 2s warten                        │
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

### Aufgabe 2: Button-Counter Lösung

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

### Aufgabe 3: PWM "Atmen" Lösung

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


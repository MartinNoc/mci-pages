# MicroPython Grundlagen für ESP32

In diesem Abschnitt lernst du die wichtigsten MicroPython-Konzepte für unser Reaktionsspiel.

## 🐍 MicroPython auf ESP32

MicroPython ist eine schlanke Python-Implementation für Microcontroller. Der ESP32 unterstützt die meisten Python-Features, die wir brauchen.

## 📚 Wichtige Module für unser Projekt

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

⚠️ **Warum `utime` statt `time`?**

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

Statt Klassen verwenden wir einfache Funktionen und globale Variablen:

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

Jetzt kennst du die Grundlagen! Im nächsten Abschnitt setzen wir alles zusammen: [Schritt-für-Schritt Implementation](step-by-step-implementation.md)

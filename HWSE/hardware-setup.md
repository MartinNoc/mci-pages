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

Hardware funktioniert? Dann weiter zur [Zustandsdiagramm-Aufgabe](state-diagram-exercise.md)!

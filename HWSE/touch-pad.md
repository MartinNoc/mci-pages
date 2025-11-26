# Touch Pad

Das ESP32 verfügt über kapazitive Touch-Sensoren, die Berührungen ohne mechanischen Kontakt erkennen können. Diese TouchPads können direkt mit MicroPython angesprochen werden und eignen sich hervorragend für Benutzereingaben in eingebetteten Systemen.

## Einstieg

Der erste Schritt besteht darin, einen TouchPad-Pin zu konfigurieren und dessen Werte kontinuierlich auszulesen. Die Werte zeigen die kapazitive Änderung an - niedrigere Werte bedeuten eine Berührung.

```python
from machine import TouchPad, Pin, Timer

# TouchPad an GPIO 13 initialisieren
touch_pin = TouchPad(Pin(13, mode=Pin.IN))

def check_touch(timer):
    # TouchPad-Wert auslesen (niedrigere Werte = Berührung)
    print(touch_pin.read())

# Timer für periodische Abfrage alle 500ms
pin_timer = Timer(0)
pin_timer.init(period=500, mode=Timer.PERIODIC, callback=check_touch)
```

## Berührung erkennen

Um zuverlässig Berührungen zu erkennen, wird ein Schwellwert definiert. Wenn der gemessene Wert unter diesen Schwellwert fällt, wird eine Berührung erkannt. Der Schwellwert muss je nach Hardware und Umgebung angepasst werden.

```python
from machine import TouchPad, Pin, Timer
import time

# TouchPad an GPIO 13 initialisieren
touch_pin = TouchPad(Pin(13, mode=Pin.IN))
# Schwellwert für Berührungserkennung (muss ggf. angepasst werden)
TOUCH_THRESHOLD = 400

def check_touch(timer):
    # Aktuellen TouchPad-Wert auslesen
    value = touch_pin.read()
    # Berührung erkennen: Wert unter Schwellwert = Berührung
    is_touched = value < TOUCH_THRESHOLD
    if is_touched:
        print(f"Touch detected ({value})")
    else:
        print(f"No touch ({value})")

# Timer für kontinuierliche Überwachung alle 500ms
pin_timer = Timer(0)
pin_timer.init(period=500, mode=Timer.PERIODIC, callback=check_touch)
```

## Touchpad Kalibrierung

Da sich die Grundwerte der TouchPads je nach Umgebung, Temperatur und Hardware unterscheiden können, ist eine automatische Kalibrierung sinnvoll. Hier wird der Durchschnittswert über mehrere Messungen ermittelt, um eine stabile Basis für die Schwellwertbestimmung zu erhalten.

```python
from machine import TouchPad, Pin, Timer
import time

# TouchPad an GPIO 13 initialisieren
touch_pin = TouchPad(Pin(13, mode=Pin.IN))

# Anzahl Messungen für Kalibrierung
num = 1000

# Durchschnittswert aus vielen Messungen berechnen (Basiswert im unberührten Zustand)
base = sum(touch_pin.read() for _ in range(num)) // num
print(base)  # Diesen Wert als Referenz für Schwellwert verwenden
```

## TouchPad Sequenz Erkennung

Erweiterte TouchPad-Funktionalität zur Erkennung von Berührungssequenzen. Hierbei werden zeitliche Abstände zwischen Berührungen gemessen, um unterschiedliche Eingabemuster zu erkennen. Das System kann zwischen kurzen und langen Pausen unterscheiden und komplexe Eingabesequenzen verarbeiten.

```python
from machine import TouchPad, Pin, Timer
import time

# TouchPad an GPIO 13 initialisieren
touch_pin = TouchPad(Pin(13, mode=Pin.IN))
# Schwellwert für Berührungserkennung
TOUCH_THRESHOLD = 400
# Zeitgrenzen für Sequenzerkennung (in Millisekunden)
T_SHORT = 700   # Kurze Pause zwischen Berührungen
T_LONG = 1400   # Lange Pause = Ende der Sequenz

# Globale Variablen für Sequenzverfolgung
last_event_time = 0      # Zeitpunkt der letzten Berührung
event_counter = 0        # Anzahl Berührungen in aktueller Sequenz
prev_touch_status = False # Vorheriger Berührungsstatus (für Flankenerkdnung)

def time_expired(timer):
    """Callback wenn Sequenz-Timer abläuft (Ende der Sequenz)"""
    global event_counter
    print(f"End of sequence: {event_counter} touches")
    event_counter = 0
    
# Timer für Sequenz-Ende-Erkennung
sequence_timer = Timer(1)

def check_touch(timer):
    """Hauptfunktion zur Berührungsüberwachung und Sequenzerkennung"""
    global last_event_time, event_counter, prev_touch_status
    
    # TouchPad-Wert auslesen und Berührung prüfen
    value = touch_pin.read()
    is_touched = value < TOUCH_THRESHOLD
    
    # Nur bei neuer Berührung (steigende Flanke) reagieren
    if is_touched and not prev_touch_status:
        current_time = time.ticks_ms()
        time_diff = time.ticks_diff(current_time, last_event_time)
        
        if time_diff < T_SHORT:
            # Kurze Pause: Ereignis gehört zur aktuellen Sequenz
            print("SHORT")
            event_counter += 1
        elif time_diff < T_LONG:
            # Mittlere Pause: Noch zur Sequenz gehörend
            print("LONG")
            event_counter += 1
        else:
            # Lange Pause: Neue Sequenz beginnt
            print("New sequence")
            pass
            
        last_event_time = current_time
        # Sequenz-Timer neu starten (wartet auf Ende der Sequenz)
        sequence_timer.init(period=T_LONG, mode=Timer.ONE_SHOT, callback=time_expired)
        
    # Berührungsstatus für nächste Iteration speichern
    prev_touch_status = is_touched

# Haupt-Timer für kontinuierliche TouchPad-Überwachung (alle 50ms)
pin_timer = Timer(0)
pin_timer.init(period=50, mode=Timer.PERIODIC, callback=check_touch)
```
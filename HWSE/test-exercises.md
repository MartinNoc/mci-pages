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

## 🚀 Erweiterungsaufgaben

### Erweiterung 1: High-Score System
Implementiere ein System, das die 5 besten Zeiten speichert:

```python
class HighScore:
    def __init__(self):
        self.scores = []  # Liste der besten Zeiten
        self.max_scores = 5
    
    def add_score(self, reaction_time):
        """Neue Zeit hinzufügen und Liste sortiert halten"""
        self.scores.append(reaction_time)
        self.scores.sort()  # Sortieren: beste Zeit zuerst
        
        # Nur die besten 5 behalten
        if len(self.scores) > self.max_scores:
            self.scores = self.scores[:self.max_scores]
    
    def is_new_record(self, reaction_time):
        """Prüfen ob es eine neue Bestzeit ist"""
        if len(self.scores) < self.max_scores:
            return True
        return reaction_time < self.scores[-1]  # Besser als schlechteste Top-5
    
    def print_highscores(self):
        """High-Score Liste ausgeben"""
        print("\n🏆 High Scores:")
        for i, score in enumerate(self.scores, 1):
            print(f"  {i}. {score}ms")
```

**Aufgabe:** Integriere das High-Score System ins Hauptspiel.

### Erweiterung 2: RGB-LED Unterstützung
Erweitere das Spiel für RGB-LEDs:

```python
class RGBLED:
    def __init__(self, red_pin, green_pin, blue_pin):
        self.red = PWM(Pin(red_pin))
        self.green = PWM(Pin(green_pin))
        self.blue = PWM(Pin(blue_pin))
        
        for pwm in [self.red, self.green, self.blue]:
            pwm.freq(1000)
    
    def set_color(self, red, green, blue):
        """Farbe setzen (0-1023 für jede Komponente)"""
        self.red.duty(red)
        self.green.duty(green)
        self.blue.duty(blue)
    
    def set_mode(self, mode):
        if mode == "waiting":
            self.set_color(0, 0, 100)      # Schwaches Blau
        elif mode == "ready":
            self.set_color(1023, 500, 0)   # Orange (pulsierend)
        elif mode == "go":
            self.set_color(0, 1023, 0)     # Helles Grün
        elif mode == "result_good":
            self.set_color(0, 1023, 0)     # Grün blinken
        elif mode == "result_bad":
            self.set_color(1023, 0, 0)     # Rot blinken
        elif mode == "false_start":
            self.set_color(1023, 0, 0)     # Rot
```

**Aufgabe:** Implementiere verschiedene Farben für verschiedene Spielsituationen.

### Erweiterung 3: Mehrspielermodus
Erweitere das Spiel für 2 Spieler:

```python
class TwoPlayerGame:
    def __init__(self):
        # Zwei Buttons und LEDs
        self.button1 = DebouncedButton(0)  # Spieler 1
        self.button2 = DebouncedButton(5)  # Spieler 2
        self.led1 = PulsingLED(2)          # LED Spieler 1
        self.led2 = PulsingLED(4)          # LED Spieler 2
        
        self.scores = [0, 0]  # Punktestand
        self.round_count = 0
        self.max_rounds = 5
    
    def update_go(self):
        """Beide Spieler können reagieren"""
        if self.button1.was_pressed():
            reaction_time = self.state_timer.get_elapsed()
            print(f"🎉 Spieler 1 gewinnt! ({reaction_time}ms)")
            self.scores[0] += 1
            self.winner = 1
            self.change_state(STATE_RESULT)
        
        elif self.button2.was_pressed():
            reaction_time = self.state_timer.get_elapsed()
            print(f"🎉 Spieler 2 gewinnt! ({reaction_time}ms)")
            self.scores[1] += 1
            self.winner = 2
            self.change_state(STATE_RESULT)
```

**Aufgabe:** Implementiere einen Best-of-5 Modus für zwei Spieler.

### Erweiterung 4: Schwierigkeitsgrade
Implementiere verschiedene Schwierigkeitsgrade:

```python
class DifficultySettings:
    EASY = {
        'wait_min': 3000,
        'wait_max': 6000,
        'timeout': 5000,
        'name': '😊 Einfach'
    }
    
    MEDIUM = {
        'wait_min': 2000,
        'wait_max': 5000,
        'timeout': 3000,
        'name': '😐 Mittel'
    }
    
    HARD = {
        'wait_min': 1000,
        'wait_max': 3000,
        'timeout': 2000,
        'name': '😤 Schwer'
    }
    
    EXPERT = {
        'wait_min': 500,
        'wait_max': 2000,
        'timeout': 1500,
        'name': '🔥 Experte'
    }

def select_difficulty():
    """Schwierigkeitsgrad per Button-Kombination wählen"""
    # Implementation hier...
    pass
```

**Aufgabe:** Lass den Benutzer per Button-Kombinationen die Schwierigkeit wählen.

### Erweiterung 5: Datenspeicherung
Speichere Spielstatistiken persistent:

```python
import json

class GameStatistics:
    def __init__(self, filename='game_stats.json'):
        self.filename = filename
        self.stats = self.load_stats()
    
    def load_stats(self):
        """Statistiken von Datei laden"""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return {
                'games_played': 0,
                'best_time': None,
                'average_time': 0,
                'false_starts': 0,
                'all_times': []
            }
    
    def save_stats(self):
        """Statistiken in Datei speichern"""
        with open(self.filename, 'w') as f:
            json.dump(self.stats, f)
    
    def add_game(self, reaction_time, was_false_start=False):
        """Neues Spiel zu Statistiken hinzufügen"""
        if was_false_start:
            self.stats['false_starts'] += 1
        else:
            self.stats['games_played'] += 1
            self.stats['all_times'].append(reaction_time)
            
            # Neue Bestzeit?
            if self.stats['best_time'] is None or reaction_time < self.stats['best_time']:
                self.stats['best_time'] = reaction_time
            
            # Durchschnitt neu berechnen
            self.stats['average_time'] = sum(self.stats['all_times']) / len(self.stats['all_times'])
        
        self.save_stats()
```

**Aufgabe:** Implementiere persistente Statistiken, die auch nach Neustart erhalten bleiben.

## 🔧 Debugging-Aufgaben

### Debug 1: Timing-Probleme
Was passiert, wenn du diese Änderungen machst?

```python
# Schlecht: Blocking Sleep verwenden
def bad_update_ready(self):
    self.led.set_mode("pulse")
    time.sleep(3)  # SCHLECHT: Blockiert alles!
    self.change_state(STATE_GO)

# Gut: Non-blocking Timer
def good_update_ready(self):
    if self.state_timer.is_expired():
        self.change_state(STATE_GO)
```

**Aufgabe:** Implementiere die schlechte Version und beobachte die Probleme.

### Debug 2: Button-Prellen
Teste das Spiel ohne Entprellung:

```python
# Ohne Entprellung - direkte Abfrage
def bad_button_check(self):
    if not self.button.pin.value():  # Direkt abfragen
        return True
    return False
```

**Aufgabe:** Wie oft wird fälschlicherweise ein Button-Druck erkannt?

### Debug 3: Speicher-Probleme
Was passiert bei sehr vielen Spielen?

```python
# Problematisch: Unbegrenzte Liste
all_reaction_times = []  # Wird immer größer!

# Besser: Begrenzte Historie
class LimitedHistory:
    def __init__(self, max_size=100):
        self.data = []
        self.max_size = max_size
    
    def add(self, value):
        self.data.append(value)
        if len(self.data) > self.max_size:
            self.data.pop(0)  # Ältestes Element entfernen
```

**Aufgabe:** Teste das Spiel mit unbegrenzten Listen und beobachte den Speicherverbrauch.

## 📊 Experimentelle Aufgaben

### Experiment 1: Reaktionszeit-Analyse
Sammle Daten und analysiere sie:

```python
def analyze_reaction_times(times):
    """Statistischen Analyse der Reaktionszeiten"""
    import math
    
    n = len(times)
    mean = sum(times) / n
    
    # Standardabweichung berechnen
    variance = sum((x - mean) ** 2 for x in times) / n
    std_dev = math.sqrt(variance)
    
    # Perzentile
    sorted_times = sorted(times)
    p25 = sorted_times[n // 4]
    p50 = sorted_times[n // 2]  # Median
    p75 = sorted_times[3 * n // 4]
    
    print(f"Analyse von {n} Spielen:")
    print(f"Durchschnitt: {mean:.1f}ms")
    print(f"Median: {p50}ms")
    print(f"Standardabweichung: {std_dev:.1f}ms")
    print(f"25% Perzentil: {p25}ms")
    print(f"75% Perzentil: {p75}ms")
```

### Experiment 2: Lernkurve
Untersuche, ob sich die Reaktionszeit mit der Übung verbessert:

```python
def plot_learning_curve(times):
    """Lernkurve visualisieren (vereinfacht für Terminal)"""
    window_size = 5  # Gleitender Durchschnitt über 5 Spiele
    
    averages = []
    for i in range(window_size, len(times)):
        window = times[i-window_size:i]
        avg = sum(window) / window_size
        averages.append(avg)
    
    print("Lernkurve (gleitender Durchschnitt):")
    for i, avg in enumerate(averages, window_size):
        bar_length = int(avg / 50)  # Skalierung für Balkendiagramm
        bar = "█" * bar_length
        print(f"Spiel {i:2d}: {avg:5.1f}ms {bar}")
```

### Experiment 3: Circadiane Rhythmen
Teste zu verschiedenen Tageszeiten:

```python
import utime

def get_time_of_day():
    """Tageszeit bestimmen"""
    # Vereinfacht - verwende RTC für echte Zeit
    hour = (utime.time() // 3600) % 24
    
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon" 
    elif 18 <= hour < 22:
        return "evening"
    else:
        return "night"

# Sammle Daten nach Tageszeit
time_data = {
    "morning": [],
    "afternoon": [],
    "evening": [],
    "night": []
}
```

**Aufgabe:** Teste deine Reaktionszeit zu verschiedenen Tageszeiten. Wann bist du am schnellsten?

## 🎯 Abschlussprojekt

**Große Aufgabe:** Implementiere dein eigenes "Ultimate Reaction Game" mit mindestens 3 der oben genannten Erweiterungen. Dokumentiere deine Designentscheidungen und teste ausgiebig.

Mögliche Kombinationen:
- RGB-LED + Schwierigkeitsgrade + High-Score System
- Mehrspielermodus + Statistiken + verschiedene Spielmodi
- Audio-Feedback + Lernkurven-Analyse + persistente Daten

Viel Erfolg beim Experimentieren! 🚀

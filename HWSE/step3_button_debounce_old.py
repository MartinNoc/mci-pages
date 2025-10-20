"""
Schritt 3: Button-Entprellung und Zufallszeiten
==============================================

In diesem Schritt verbessern wir:
- Ordentliche Button-Entprellung
- Zufällige Wartezeiten in READY
- "Zu früh gedrückt" Erkennung
- Bessere Benutzerführung

Hardware:
- LED an GPIO 2 (mit PWM)
- Button an GPIO 0 (mit Pull-up)
"""

import utime
import urandom
import math
from machine import Pin, PWM

# Zustände
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
led_pwm = PWM(Pin(2))
led_pwm.freq(1000)
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Button-Entprellung (verbesserte Version)
last_button_state = 1  # Pull-up: 1 = nicht gedrückt
last_button_change_time = 0
debounce_ms = 50
button_pressed_event = False

# LED-Steuerung
led_phase = 0
led_mode = "off"
led_blink_timer = 0

def update_button_debounced():
    """Button-Zustand prüfen und entprellen - in Hauptschleife aufrufen"""
    global last_button_state, last_button_change_time, button_pressed_event
    
    current_button_state = button.value()
    current_time = utime.ticks_ms()
    
    # Event zurücksetzen
    button_pressed_event = False
    
    # Hat sich der Zustand geändert?
    if current_button_state != last_button_state:
        # Ist genug Zeit seit der letzten Änderung vergangen?
        if utime.ticks_diff(current_time, last_button_change_time) > debounce_ms:
            last_button_change_time = current_time
            last_button_state = current_button_state
            
            # Button wurde gedrückt (von 1 auf 0 wegen Pull-up)
            if current_button_state == 0:
                button_pressed_event = True
                print("Button gedrückt (entprellt)")

def was_button_pressed():
    """Gibt True zurück wenn Button seit letztem update_button_debounced() gedrückt wurde"""
    return button_pressed_event

def generate_random_ready_time():
    """Generiert zufällige Wartezeit zwischen 2-5 Sekunden"""
    return 2000 + urandom.getrandbits(12) % 3001  # 2000-5000ms

def set_led_mode(mode):
    """LED-Modus setzen"""
    global led_mode, led_phase, led_blink_timer
    
    led_mode = mode
    print(f"LED-Modus: {mode}")
    
    if mode == "off":
        led_pwm.duty(0)
    elif mode == "on":
        led_pwm.duty(1023)
    elif mode == "pulse":
        led_phase = 0
    elif mode == "blink":
        led_blink_timer = utime.ticks_ms()

def update_led():
    """LED updaten für Animationen"""
    global led_phase, led_blink_timer
    
    if led_mode == "pulse":
        brightness = int(300 + 200 * math.sin(led_phase))
        led_pwm.duty(brightness)
        led_phase += 0.15
        if led_phase > 2 * math.pi:
            led_phase = 0
    elif led_mode == "blink":
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, led_blink_timer) >= 300:
            led_blink_timer = current_time
            if led_pwm.duty() > 0:
                led_pwm.duty(0)
            else:
                led_pwm.duty(1023)
        elif self.mode == "blink":
            current_time = utime.ticks_ms()
            if utime.ticks_diff(current_time, self.blink_timer) >= 300:
                self.blink_timer = current_time
                if self.pwm.duty() > 0:
                    self.pwm.duty(0)
                else:
                    self.pwm.duty(1023)

class ReactionGameButton:
    """Reaktionsspiel mit Button-Entprellung und Zufallszeiten"""
    
    def __init__(self):
        print("=== Reaktionsspiel Schritt 3: Button-Entprellung ===")
        
        # Hardware initialisieren
        self.led = PulsingLED(2)
        self.button = DebouncedButton(0)  # Entprellter Button
        
        # Zustandsvariablen
        self.state = STATE_WAITING
        self.state_start_time = utime.ticks_ms()
        self.ready_duration = 0  # Zufällige Wartezeit in READY
        
        print("Hardware initialisiert")
        print("Drücke den Button zum Starten!")
    
    def change_state(self, new_state):
        """Zustand wechseln mit zustandsspezifischer Initialisierung"""
        state_names = ["WAITING", "READY", "GO", "RESULT"]
        print(f"State: {state_names[self.state]} → {state_names[new_state]}")
        
        self.state = new_state
        self.state_start_time = utime.ticks_ms()
        
        # Zustandsspezifische Initialisierung
        if new_state == STATE_WAITING:
            self.led.set_mode("off")
            
        elif new_state == STATE_READY:
            # Zufällige Wartezeit zwischen 2-5 Sekunden berechnen
            self.ready_duration = 2000 + urandom.getrandbits(12) % 3001  # 0-3000 + 2000
            print(f"Bereit machen... warte {self.ready_duration}ms")
            print("⚠️  Nicht zu früh drücken!")
            self.led.set_mode("pulse")
            
        elif new_state == STATE_GO:
            print("🚀 JETZT! Drücke den Button so schnell wie möglich!")
            self.led.set_mode("on")
            
        elif new_state == STATE_RESULT:
            self.led.set_mode("blink")
    
    def update(self):
        """Hauptupdate-Schleife"""
        # Hardware-Updates
        self.button.update()  # Button-Entprellung
        self.led.update()     # LED-Animationen
        
        # Zustandslogik
        if self.state == STATE_WAITING:
            self.update_waiting()
        elif self.state == STATE_READY:
            self.update_ready()
        elif self.state == STATE_GO:
            self.update_go()
        elif self.state == STATE_RESULT:
            self.update_result()
    
    def update_waiting(self):
        """WAITING Zustand"""
        if self.button.was_pressed():
            self.change_state(STATE_READY)
    
    def update_ready(self):
        """READY Zustand - mit Zufallszeit und Falschstart-Erkennung"""
        # Zu früh gedrückt?
        if self.button.was_pressed():
            print("❌ Zu früh gedrückt! Das war ein Falschstart.")
            print("   Versuch es nochmal...")
            self.change_state(STATE_WAITING)
            return
        
        # Wartezeit abgelaufen?
        elapsed = utime.ticks_diff(utime.ticks_ms(), self.state_start_time)
        if elapsed >= self.ready_duration:
            self.change_state(STATE_GO)
    
    def update_go(self):
        """GO Zustand - Reaktionszeit messen"""
        if self.button.was_pressed():
            reaction_time = utime.ticks_diff(utime.ticks_ms(), self.state_start_time)
            print(f"⚡ Reaktionszeit: {reaction_time}ms")
            
            # Bewertung der Reaktionszeit
            if reaction_time < 200:
                print("   🔥 Blitzschnell!")
            elif reaction_time < 350:
                print("   ⚡ Sehr gut!")
            elif reaction_time < 500:
                print("   👍 Gut!")
            elif reaction_time < 750:
                print("   😐 Okay...")
            else:
                print("   🐌 Da geht noch was!")
            
            self.change_state(STATE_RESULT)
            return
        
        # Timeout nach 3 Sekunden
        elapsed = utime.ticks_diff(utime.ticks_ms(), self.state_start_time)
        if elapsed >= 3000:
            print("🐌 Timeout! Zu langsam (>3000ms).")
            print("   Übung macht den Meister!")
            self.change_state(STATE_RESULT)
    
    def update_result(self):
        """RESULT Zustand - Ergebnis anzeigen"""
        elapsed = utime.ticks_diff(utime.ticks_ms(), self.state_start_time)
        
        # Nach 2 Sekunden zurück zu WAITING
        if elapsed >= 2000:
            print("\n" + "="*40)
            print("Bereit für neues Spiel!")
            print("Drücke den Button zum Starten!")
            print("="*40)
            self.change_state(STATE_WAITING)

def main():
    """Hauptprogramm"""
    game = ReactionGameButton()
    
    print("\nSpiel läuft... (Strg+C zum Beenden)")
    print("Features: Button-Entprellung, Zufallszeiten, Falschstart-Erkennung")
    
    try:
        while True:
            game.update()
            utime.sleep_ms(10)  # 10ms Update-Rate
    
    except KeyboardInterrupt:
        print("\nSpiel beendet!")
        game.led.set_mode("off")

if __name__ == "__main__":
    main()

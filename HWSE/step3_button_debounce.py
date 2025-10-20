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

def change_state(new_state):
    """Zustand wechseln mit zustandsspezifischer Initialisierung"""
    global current_state, state_start_time, ready_duration
    
    state_names = ["WAITING", "READY", "GO", "RESULT"]
    print(f"State: {state_names[current_state]} → {state_names[new_state]}")
    
    current_state = new_state
    state_start_time = utime.ticks_ms()
    
    # Zustandsspezifische Initialisierung
    if new_state == STATE_WAITING:
        set_led_mode("off")
    elif new_state == STATE_READY:
        set_led_mode("pulse")
        # Zufällige Wartezeit zwischen 2-5 Sekunden
        ready_duration = generate_random_ready_time()
        print(f"Warte {ready_duration}ms... (Nicht zu früh drücken!)")
    elif new_state == STATE_GO:
        set_led_mode("on")
    elif new_state == STATE_RESULT:
        set_led_mode("blink")

def update_waiting():
    """WAITING Zustand"""
    if was_button_pressed():
        change_state(STATE_READY)

def update_ready():
    """READY Zustand - LED pulsiert, warten auf zufällige Zeit"""
    # Zu früh gedrückt?
    if was_button_pressed():
        print("⚠️ ZU FRÜH! Warte auf das helle Signal!")
        print("🔄 Neuer Versuch...")
        change_state(STATE_WAITING)
        return
    
    # Wartezeit abgelaufen?
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= ready_duration:
        print("🚀 JETZT! Drücke den Button so schnell wie möglich!")
        change_state(STATE_GO)

def update_go():
    """GO Zustand - LED leuchtet hell, Reaktionszeit messen"""
    global reaction_time
    
    if was_button_pressed():
        reaction_time = utime.ticks_diff(utime.ticks_ms(), state_start_time)
        print(f"⚡ Reaktionszeit: {reaction_time}ms")
        
        # Bewertung der Reaktionszeit
        if reaction_time < 200:
            print("🏆 Blitzschnell! Sehr gut!")
        elif reaction_time < 300:
            print("👍 Gut!")
        elif reaction_time < 500:
            print("👌 OK")
        else:
            print("🐌 Etwas langsam, aber OK!")
        
        change_state(STATE_RESULT)
        return
    
    # Timeout nach 3 Sekunden
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= 3000:
        print("🐌 Timeout! Zu langsam reagiert.")
        change_state(STATE_RESULT)

def update_result():
    """RESULT Zustand - LED blinkt, dann zurück zu WAITING"""
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    
    # Nach 3 Sekunden zurück zu WAITING
    if elapsed >= 3000:
        print("\n--- Bereit für neues Spiel ---")
        print("Drücke den Button zum Starten!")
        change_state(STATE_WAITING)

def main_loop():
    """Hauptschleife"""
    while True:
        # Button immer entprellen
        update_button_debounced()
        
        # LED immer updaten für Animationen
        update_led()
        
        # Zustandslogik
        if current_state == STATE_WAITING:
            update_waiting()
        elif current_state == STATE_READY:
            update_ready()
        elif current_state == STATE_GO:
            update_go()
        elif current_state == STATE_RESULT:
            update_result()
        
        utime.sleep_ms(20)

# Hauptprogramm
print("=== Reaktionsspiel Schritt 3: Button-Entprellung ===")
print("Verbesserungen:")
print("- Ordentliche Button-Entprellung")
print("- Zufällige Wartezeiten (2-5 Sekunden)")
print("- 'Zu früh gedrückt' Erkennung")
print("\nDrücke den Button zum Starten!")
print("Spiel läuft... (Strg+C zum Beenden)")

# Startzustand setzen
change_state(STATE_WAITING)

try:
    main_loop()
except KeyboardInterrupt:
    print("\nSpiel beendet.")
    led_pwm.deinit()

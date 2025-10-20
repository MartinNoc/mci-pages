"""
Schritt 4: Zufallszeiten und erweiterte Features
===============================================

In diesem Schritt erweitern wir das Spiel um:
- Noch bessere Zufallszeiten mit urandom
- Verschiedene Schwierigkeitsgrade
- Statistiken (beste Zeit, Anzahl Spiele)
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

# Statistiken
games_played = 0
best_time = None
false_starts = 0

# Hardware initialisieren
led_pwm = PWM(Pin(2))
led_pwm.freq(1000)
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Button-Entprellung
last_button_state = 1
last_button_change_time = 0
debounce_ms = 50
button_pressed_event = False

# LED-Steuerung
led_phase = 0
led_mode = "off"
led_blink_timer = 0

def update_button_debounced():
    """Button-Zustand prüfen und entprellen"""
    global last_button_state, last_button_change_time, button_pressed_event
    
    current_button_state = button.value()
    current_time = utime.ticks_ms()
    
    button_pressed_event = False
    
    if current_button_state != last_button_state:
        if utime.ticks_diff(current_time, last_button_change_time) > debounce_ms:
            last_button_change_time = current_time
            last_button_state = current_button_state
            
            if current_button_state == 0:
                button_pressed_event = True

def was_button_pressed():
    """Gibt True zurück wenn Button gedrückt wurde"""
    return button_pressed_event

def generate_random_ready_time():
    """Generiert zufällige Wartezeit zwischen 2-5 Sekunden"""
    # Verwende urandom für bessere Zufallszahlen
    random_ms = urandom.getrandbits(12) % 3001  # 0-3000ms
    return 2000 + random_ms  # 2000-5000ms

def set_led_mode(mode):
    """LED-Modus setzen"""
    global led_mode, led_phase, led_blink_timer
    
    led_mode = mode
    
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
        # Langsames Pulsieren für Bereitschaft
        brightness = int(300 + 200 * math.sin(led_phase))
        led_pwm.duty(brightness)
        led_phase += 0.1  # Langsamere Animation
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

def print_statistics():
    """Statistiken ausgeben"""
    print(f"\n📊 Statistiken:")
    print(f"   Spiele gespielt: {games_played}")
    if best_time:
        print(f"   Beste Zeit: {best_time}ms")
    print(f"   Fehlstarts: {false_starts}")
    
    # Bewertung
    if best_time:
        if best_time < 200:
            print("   Bewertung: 🏆 Profi-Reaktionen!")
        elif best_time < 300:
            print("   Bewertung: 👍 Sehr gut!")
        elif best_time < 400:
            print("   Bewertung: 👌 Gut!")
        else:
            print("   Bewertung: 📈 Noch Potenzial!")

def change_state(new_state):
    """Zustand wechseln"""
    global current_state, state_start_time, ready_duration
    
    state_names = ["WAITING", "READY", "GO", "RESULT"]
    
    current_state = new_state
    state_start_time = utime.ticks_ms()
    
    if new_state == STATE_WAITING:
        set_led_mode("off")
        print("\n--- Neues Spiel ---")
        print("Drücke den Button zum Starten!")
    elif new_state == STATE_READY:
        set_led_mode("pulse")
        ready_duration = generate_random_ready_time()
        print(f"⏳ Bereitmachen... (ca. {ready_duration//1000}s)")
        print("💡 Warte auf das helle Signal!")
    elif new_state == STATE_GO:
        set_led_mode("on")
        print("🚀 JETZT! Drücke den Button!")
    elif new_state == STATE_RESULT:
        set_led_mode("blink")

def update_waiting():
    """WAITING Zustand"""
    if was_button_pressed():
        change_state(STATE_READY)

def update_ready():
    """READY Zustand"""
    global false_starts
    
    if was_button_pressed():
        false_starts += 1
        print("⚠️ ZU FRÜH! Das war ein Fehlstart!")
        print("🔄 Versuch es nochmal...")
        change_state(STATE_WAITING)
        return
    
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= ready_duration:
        change_state(STATE_GO)

def update_go():
    """GO Zustand"""
    global reaction_time, games_played, best_time
    
    if was_button_pressed():
        reaction_time = utime.ticks_diff(utime.ticks_ms(), state_start_time)
        games_played += 1
        
        print(f"⚡ Reaktionszeit: {reaction_time}ms")
        
        # Beste Zeit aktualisieren
        if best_time is None or reaction_time < best_time:
            best_time = reaction_time
            print("🎉 NEUE BESTZEIT!")
        
        # Bewertung
        if reaction_time < 150:
            print("🏆 Unglaublich schnell!")
        elif reaction_time < 200:
            print("🔥 Blitzschnell!")
        elif reaction_time < 250:
            print("👍 Sehr gut!")
        elif reaction_time < 350:
            print("👌 Gut!")
        elif reaction_time < 500:
            print("🆗 OK")
        else:
            print("🐌 Langsam, aber besser als gar nicht!")
        
        change_state(STATE_RESULT)
        return
    
    # Timeout nach 3 Sekunden
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= 3000:
        games_played += 1
        print("⏰ Timeout! Zu langsam.")
        change_state(STATE_RESULT)

def update_result():
    """RESULT Zustand"""
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    
    # Nach 2 Sekunden Statistiken zeigen
    if elapsed >= 2000 and elapsed < 2100:  # Nur einmal ausgeben
        print_statistics()
    
    # Nach 4 Sekunden zurück zu WAITING
    if elapsed >= 4000:
        change_state(STATE_WAITING)

def main_loop():
    """Hauptschleife"""
    while True:
        update_button_debounced()
        update_led()
        
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
print("=== Reaktionsspiel Schritt 4: Erweiterte Features ===")
print("Neue Features:")
print("- Bessere Zufallszeiten mit urandom")
print("- Statistiken (beste Zeit, Fehlstarts)")
print("- Detaillierte Bewertungen")
print("- Erweiterte Benutzerführung")
print("\nDrücke den Button zum Starten!")

change_state(STATE_WAITING)

try:
    main_loop()
except KeyboardInterrupt:
    print("\n\n=== Spiel beendet ===")
    print_statistics()
    led_pwm.deinit()

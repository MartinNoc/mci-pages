"""
Schritt 2: LED-Steuerung mit PWM
===============================

In diesem Schritt erweitern wir die LED-Steuerung:
- PWM für variable Helligkeit
- Sanftes Pulsieren in READY-Phase
- Helles Leuchten in GO-Phase
- Blinken in RESULT-Phase

Hardware:
- LED an GPIO 2 (jetzt mit PWM)
- Button an GPIO 0 (mit Pull-up)
"""

import utime
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
ready_duration = 3000  # 3 Sekunden (später zufällig)
reaction_time = 0

# Hardware initialisieren
led_pwm = PWM(Pin(2))
led_pwm.freq(1000)  # 1 kHz PWM-Frequenz
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Button-Entprellung
last_button_time = 0
debounce_ms = 50

# LED-Steuerung Variablen
led_phase = 0  # Für Sinuswellen-Pulsieren
led_mode = "off"  # "off", "pulse", "on", "blink"
led_blink_timer = 0

def set_led_mode(mode):
    """LED-Modus setzen"""
    global led_mode, led_phase, led_blink_timer
    
    led_mode = mode
    print(f"LED-Modus: {mode}")
    
    if mode == "off":
        led_pwm.duty(0)  # Komplett aus
    elif mode == "on":
        led_pwm.duty(1023)  # Maximale Helligkeit
    elif mode == "pulse":
        led_phase = 0  # Pulsieren-Phase zurücksetzen
    elif mode == "blink":
        led_blink_timer = utime.ticks_ms()

def update_led():
    """LED updaten - für Animationen (in Hauptschleife aufrufen)"""
    global led_phase, led_blink_timer
    
    if led_mode == "pulse":
        # Sanftes Pulsieren mit Sinuswelle
        brightness = int(300 + 200 * math.sin(led_phase))  # 300-500 von 1023
        led_pwm.duty(brightness)
        
        # Phase erhöhen für Animation
        led_phase += 0.15  # Geschwindigkeit des Pulsierens
        if led_phase > 2 * math.pi:
            led_phase = 0  # Zurücksetzen nach vollständigem Zyklus
    
    elif led_mode == "blink":
        # Blinken alle 300ms
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, led_blink_timer) >= 300:
            led_blink_timer = current_time
            
            # Zwischen an und aus wechseln
            if led_pwm.duty() > 0:
                led_pwm.duty(0)      # Aus
            else:
                led_pwm.duty(1023)   # An

def change_state(new_state):
    """Zustand wechseln und LED-Modus anpassen"""
    global current_state, state_start_time
    
    state_names = ["WAITING", "READY", "GO", "RESULT"]
    print(f"State: {state_names[current_state]} → {state_names[new_state]}")
    
    current_state = new_state
    state_start_time = utime.ticks_ms()
    
    # LED-Modus je nach Zustand setzen
    if new_state == STATE_WAITING:
        set_led_mode("off")
    elif new_state == STATE_READY:
        set_led_mode("pulse")  # Pulsieren
    elif new_state == STATE_GO:
        set_led_mode("on")     # Hell
    elif new_state == STATE_RESULT:
        set_led_mode("blink")  # Blinken

def button_pressed():
    """Button mit Entprellung prüfen"""
    global last_button_time
    
    current_time = utime.ticks_ms()
    if not button.value() and utime.ticks_diff(current_time, last_button_time) > debounce_ms:
        last_button_time = current_time
        return True
    return False

def update_waiting():
    """WAITING Zustand"""
    if button_pressed():
        change_state(STATE_READY)

def update_ready():
    """READY Zustand - LED pulsiert sanft"""
    # Zu früh gedrückt?
    if button_pressed():
        print("⚠️ Zu früh gedrückt! Warte auf das Signal!")
        change_state(STATE_WAITING)
        return
    
    # Nach ready_duration zu GO
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= ready_duration:
        print("🚀 JETZT! Drücke den Button!")
        change_state(STATE_GO)

def update_go():
    """GO Zustand - LED leuchtet hell"""
    global reaction_time
    
    # Button-Reaktion prüfen
    if button_pressed():
        reaction_time = utime.ticks_diff(utime.ticks_ms(), state_start_time)
        print(f"⚡ Reaktionszeit: {reaction_time}ms")
        change_state(STATE_RESULT)
        return
    
    # Timeout nach 3 Sekunden
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= 3000:
        print("🐌 Timeout! Zu langsam.")
        change_state(STATE_RESULT)

def update_result():
    """RESULT Zustand - LED blinkt"""
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    
    # Nach 2 Sekunden zurück zu WAITING
    if elapsed >= 2000:
        print("\n--- Bereit für neues Spiel ---")
        print("Drücke den Button zum Starten!")
        change_state(STATE_WAITING)

def main_loop():
    """Hauptschleife"""
    while True:
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
        
        utime.sleep_ms(20)  # Etwas mehr Zeit für PWM-Updates

# Hauptprogramm
print("=== Reaktionsspiel Schritt 2: LED-Steuerung ===")
print("Hardware initialisiert")
print("Drücke den Button zum Starten!")
print("Beobachte die verschiedenen LED-Modi!")
print("\nSpiel läuft... (Strg+C zum Beenden)")

# Startzustand setzen
change_state(STATE_WAITING)

try:
    main_loop()
except KeyboardInterrupt:
    print("\nSpiel beendet.")
    led_pwm.deinit()

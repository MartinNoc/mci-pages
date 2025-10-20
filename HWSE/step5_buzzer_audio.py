"""
Schritt 5: Audio-Feedback mit Buzzer
====================================

In diesem Schritt fügen wir Audio-Feedback hinzu:
- Buzzer für verschiedene Ereignisse
- Start-Sound beim Übergang zu GO
- Erfolgs-/Fehler-Töne
- Audio-Timing mit utime

Hardware:
- LED an GPIO 2 (mit PWM)
- Button an GPIO 0 (mit Pull-up)
- Buzzer an GPIO 4 (neu!)
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
buzzer = PWM(Pin(4))  # NEU: Buzzer an GPIO 4

# Button-Entprellung
last_button_state = 1
last_button_change_time = 0
debounce_ms = 50
button_pressed_event = False

# LED-Steuerung
led_phase = 0
led_mode = "off"
led_blink_timer = 0

# Buzzer-Steuerung
buzzer_stop_time = 0
buzzer_active = False

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

def play_tone(frequency, duration_ms):
    """Ton abspielen"""
    global buzzer_stop_time, buzzer_active
    
    if frequency > 0:
        buzzer.freq(frequency)
        buzzer.duty(512)  # 50% duty cycle
        buzzer_active = True
        buzzer_stop_time = utime.ticks_ms() + duration_ms
        print(f"♪ Ton: {frequency}Hz für {duration_ms}ms")
    else:
        stop_buzzer()

def stop_buzzer():
    """Buzzer stoppen"""
    global buzzer_active
    buzzer.duty(0)
    buzzer_active = False

def update_buzzer():
    """Buzzer-Timer prüfen"""
    if buzzer_active and utime.ticks_ms() >= buzzer_stop_time:
        stop_buzzer()

def play_start_sound():
    """Start-Sound (aufsteigend)"""
    play_tone(800, 100)

def play_success_sound():
    """Erfolgs-Sound (hoch)"""
    play_tone(1000, 200)

def play_error_sound():
    """Fehler-Sound (tief)"""
    play_tone(300, 400)

def play_timeout_sound():
    """Timeout-Sound (sehr tief)"""
    play_tone(200, 600)

def play_best_time_sound():
    """Neue Bestzeit Sound (sehr hoch)"""
    play_tone(1500, 300)

def generate_random_ready_time():
    """Generiert zufällige Wartezeit zwischen 2-5 Sekunden"""
    random_ms = urandom.getrandbits(12) % 3001
    return 2000 + random_ms

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
        brightness = int(300 + 200 * math.sin(led_phase))
        led_pwm.duty(brightness)
        led_phase += 0.1
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
        print("💡 Warte auf das Signal!")
    elif new_state == STATE_GO:
        set_led_mode("on")
        play_start_sound()  # Audio-Feedback!
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
        play_error_sound()  # Audio-Feedback für Fehlstart
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
            play_best_time_sound()  # Spezial-Sound für Bestzeit
            print("🎉 NEUE BESTZEIT!")
        else:
            play_success_sound()  # Normal Erfolgs-Sound
        
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
        play_timeout_sound()  # Audio-Feedback für Timeout
        print("⏰ Timeout! Zu langsam.")
        change_state(STATE_RESULT)

def update_result():
    """RESULT Zustand"""
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    
    # Nach 2 Sekunden Statistiken zeigen
    if elapsed >= 2000 and elapsed < 2100:
        print_statistics()
    
    # Nach 4 Sekunden zurück zu WAITING
    if elapsed >= 4000:
        change_state(STATE_WAITING)

def main_loop():
    """Hauptschleife"""
    while True:
        update_button_debounced()
        update_led()
        update_buzzer()  # NEU: Buzzer-Timer prüfen
        
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
print("=== Reaktionsspiel Schritt 5: Audio-Feedback ===")
print("Neue Features:")
print("- Buzzer an GPIO 4")
print("- Audio-Feedback für alle Ereignisse")
print("- Start-Ton, Erfolgs-/Fehler-Töne")
print("- Spezial-Sound für neue Bestzeit")
print("\nVerbinde einen Buzzer an GPIO 4!")
print("Drücke den Button zum Starten!")

change_state(STATE_WAITING)

try:
    main_loop()
except KeyboardInterrupt:
    print("\n\n=== Spiel beendet ===")
    print_statistics()
    stop_buzzer()
    led_pwm.deinit()
    buzzer.deinit()

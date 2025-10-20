"""
Schritt 6: Vollständiges Reaktionsspiel
======================================

Dies ist die finale Version mit allen Features:
- Zustandsautomat mit 4 Zuständen (funktional, ohne Klassen)
- PWM LED-Steuerung mit verschiedenen Modi
- Button-Entprellung (einfache Variante)
- Präzise Zeitmessung mit utime
- Buzzer für Audio-Feedback
- Zufällige Wartezeiten
- Fehlerbehandlung und Benutzerführung

Hardware:
- LED an GPIO 2
- Button an GPIO 0 (mit Pull-up)
- Buzzer an GPIO 4
"""

import utime  # WICHTIG: utime statt time für Mikrocontroller!
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
buzzer = PWM(Pin(4))

# Button-Entprellung (einfache Variante)
last_button_time = 0
debounce_ms = 50

# LED-Pulsieren Variablen
led_phase = 0
led_mode = "off"  # "off", "pulse", "on", "blink"
led_blink_timer = 0

# Buzzer-Timer
buzzer_stop_time = 0
buzzer_active = False

def button_pressed():
    """Prüft ob Button gedrückt wurde (mit Entprellung)"""
    global last_button_time
    
    current_time = utime.ticks_ms()
    
    # Button gedrückt UND genug Zeit seit letztem Druck vergangen?
    if not button.value() and utime.ticks_diff(current_time, last_button_time) > debounce_ms:
        last_button_time = current_time
        return True
    return False

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
    """LED updaten (für Animationen)"""
    global led_phase, led_blink_timer
    
    if led_mode == "pulse":
        # Sanftes Pulsieren mit Sinuswelle
        brightness = int(300 + 200 * math.sin(led_phase))
        led_pwm.duty(brightness)
        led_phase += 0.15
        if led_phase > 2 * math.pi:
            led_phase = 0
    
    elif led_mode == "blink":
        # Blinken alle 300ms
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, led_blink_timer) >= 300:
            led_blink_timer = current_time
            if led_pwm.duty() > 0:
                led_pwm.duty(0)
            else:
                led_pwm.duty(1023)

def beep(frequency=1000, duration_ms=200):
    """Kurzen Piep abspielen"""
    global buzzer_stop_time, buzzer_active
    
    buzzer.freq(frequency)
    buzzer.duty(512)  # 50% Duty Cycle
    buzzer_stop_time = utime.ticks_ms() + duration_ms
    buzzer_active = True

def update_buzzer():
    """Buzzer updaten (für Timer)"""
    global buzzer_active
    
    if buzzer_active and utime.ticks_ms() >= buzzer_stop_time:
        buzzer.duty(0)
        buzzer_active = False

def change_state(new_state):
    """Zustand wechseln"""
    global current_state, state_start_time, ready_duration
    
    state_names = ["WAITING", "READY", "GO", "RESULT"]
    print(f"State: {state_names[current_state]} → {state_names[new_state]}")
    
    current_state = new_state
    state_start_time = utime.ticks_ms()
    
    # Zustandsspezifische Initialisierung
    if new_state == STATE_WAITING:
        set_led_mode("off")
        
    elif new_state == STATE_READY:
        # Zufällige Wartezeit 2-5 Sekunden
        ready_duration = 2000 + urandom.getrandbits(12) % 3001
        print(f"Bereit machen... ({ready_duration/1000:.1f}s)")
        print("NICHT zu früh drücken!")
        
        set_led_mode("pulse")
        beep(800, 150)  # Kurzer Beep
        
    elif new_state == STATE_GO:
        print("JETZT! So schnell wie möglich!")
        set_led_mode("on")
        
        # 3 kurze Beeps für GO-Signal (vereinfacht: nur einer)
        beep(1200, 150)
        
    elif new_state == STATE_RESULT:
        set_led_mode("blink")

def update_waiting():
    """WAITING Zustand"""
    if button_pressed():
        change_state(STATE_READY)

def update_ready():
    """READY Zustand"""
    global false_starts
    
    # Zu früh gedrückt?
    if button_pressed():
        false_starts += 1
        print(f"Falschstart! ({false_starts} insgesamt)")
        print("   Das war zu früh. Warte auf das GO-Signal!")
        
        # Buzz-Sound für Fehler
        beep(400, 500)
        change_state(STATE_WAITING)
        return
    
    # Wartezeit abgelaufen?
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= ready_duration:
        change_state(STATE_GO)

def update_go():
    """GO Zustand"""
    global reaction_time, games_played, best_time
    
    if button_pressed():
        reaction_time = utime.ticks_diff(utime.ticks_ms(), state_start_time)
        games_played += 1
        
        print(f"⚡ Reaktionszeit: {reaction_time}ms")
        
        # Bewertung
        if reaction_time < 200:
            print("   Blitzschnell! Übermenschlich!")
            beep(1500, 300)
        elif reaction_time < 300:
            print("   Ausgezeichnet!")
            beep(1200, 250)
        elif reaction_time < 450:
            print("   Sehr gut!")
            beep(1000, 200)
        elif reaction_time < 600:
            print("   Ganz okay...")
            beep(800, 200)
        else:
            print("   Da ist noch Luft nach oben!")
            beep(600, 300)
        
        # Neue Bestzeit?
        if best_time is None or reaction_time < best_time:
            if best_time is not None:
                print("   NEUE BESTZEIT!")
            best_time = reaction_time
        
        change_state(STATE_RESULT)
        return
    
    # Timeout nach 3 Sekunden
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= 3000:
        print("🐌 Timeout! Zu langsam (>3000ms)")
        print("   Übung macht den Meister!")
        beep(400, 800)  # Tiefer, langer Ton
        change_state(STATE_RESULT)

def update_result():
    """RESULT Zustand"""
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    
    # Nach 3 Sekunden zurück zu WAITING
    if elapsed >= 3000:
        # Statistiken anzeigen
        print("\n" + "="*50)
        print(f"Spiele gespielt: {games_played}")
        if best_time:
            print(f"Beste Zeit: {best_time}ms")
        if false_starts > 0:
            print(f"Falschstarts: {false_starts}")
        print("="*50)
        print("Drücke den Button für neues Spiel!")
        
        change_state(STATE_WAITING)

def main():
    """Hauptprogramm"""
    print("🎮 === Vollständiges Reaktionsspiel === 🎮")
    print("Features: LED-Effekte, Audio-Feedback, Statistiken")
    print("Hardware initialisiert")
    print("Drücke den Button zum Starten!")
    print("\n🎮 Spiel gestartet! (Strg+C zum Beenden)\n")
    
    try:
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
    
    except KeyboardInterrupt:
        print("\n\nSpiel beendet!")
        print(f"Statistiken:")
        print(f"  Spiele gespielt: {games_played}")
        if best_time:
            print(f"  Beste Zeit: {best_time}ms")
        if false_starts > 0:
            print(f"  Falschstarts: {false_starts}")
        
        # Hardware ausschalten
        led_pwm.duty(0)
        buzzer.duty(0)
        print("Danke fürs Spielen!")

if __name__ == "__main__":
    main()

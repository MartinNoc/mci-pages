"""
Schritt 1: Grundgerüst des Reaktionsspiels
=========================================

Dies ist die einfachste Version des Reaktionsspiels.
Hier lernst du:
- Grundlegende Zustandsmaschine mit Funktionen
- Hardware-Initialisierung
- Einfache Button-Abfrage
- Zeitmessung mit utime.ticks_ms() (nicht time!)

Hardware:
- LED an GPIO 2
- Button an GPIO 0 (mit Pull-up)
"""

import utime  # Verwende utime statt time für Mikrocontroller!
from machine import Pin

# Zustände als Konstanten definieren
STATE_WAITING = 0
STATE_READY = 1
STATE_GO = 2
STATE_RESULT = 3

# Globale Variablen
current_state = STATE_WAITING
state_start_time = 0

# Hardware initialisieren
led = Pin(2, Pin.OUT)
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Button-Entprellung (einfache Variante)
last_button_time = 0
debounce_ms = 50

def change_state(new_state):
    """Zustand wechseln und neue Zeit setzen"""
    global current_state, state_start_time
    
    state_names = ["WAITING", "READY", "GO", "RESULT"]
    print(f"State: {state_names[current_state]} → {state_names[new_state]}")
    
    current_state = new_state
    state_start_time = utime.ticks_ms()

def button_pressed():
    """Prüft ob Button gedrückt wurde (mit einfacher Entprellung)"""
    global last_button_time
    
    current_time = utime.ticks_ms()
    
    # Button gedrückt UND genug Zeit seit letztem Druck vergangen?
    if not button.value() and utime.ticks_diff(current_time, last_button_time) > debounce_ms:
        last_button_time = current_time
        return True
    return False

def update_waiting():
    """WAITING Zustand: Warte auf Button-Druck zum Starten"""
    led.off()
    
    if button_pressed():
        change_state(STATE_READY)

def update_ready():
    """READY Zustand: Feste Wartezeit (später: zufällig)"""
    # LED einfach an (später: pulsieren)
    led.on()
    
    # Nach 3 Sekunden automatisch zu GO
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= 3000:  # 3000ms = 3 Sekunden
        print("🚀 JETZT! Drücke den Button!")
        change_state(STATE_GO)

def update_go():
    """GO Zustand: Messe Reaktionszeit"""
    led.on()  # LED hell (später: maximale Helligkeit)
    
    # Button-Reaktion prüfen
    if button_pressed():
        reaction_time = utime.ticks_diff(utime.ticks_ms(), state_start_time)
        print(f"⚡ Reaktionszeit: {reaction_time}ms")
        change_state(STATE_RESULT)
        return
    
    # Timeout prüfen (3 Sekunden)
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    if elapsed >= 3000:
        print("🐌 Timeout! Zu langsam.")
        change_state(STATE_RESULT)

def update_result():
    """RESULT Zustand: Ergebnis anzeigen, dann zurück"""
    # Einfaches Blinken
    elapsed = utime.ticks_diff(utime.ticks_ms(), state_start_time)
    blink = (elapsed // 300) % 2  # Alle 300ms umschalten
    
    if blink:
        led.on()
    else:
        led.off()
    
    # Nach 2 Sekunden zurück zu WAITING
    if elapsed >= 2000:
        print("\n--- Bereit für neues Spiel ---")
        print("Drücke den Button zum Starten!")
        change_state(STATE_WAITING)

def main():
    """Hauptprogramm"""
    print("=== Reaktionsspiel Schritt 1: Grundgerüst ===")
    print("Hardware initialisiert")
    print("Drücke den Button zum Starten!")
    print("\nSpiel läuft... (Strg+C zum Beenden)")
    
    try:
        while True:
            # Zustandsmaschine updaten
            if current_state == STATE_WAITING:
                update_waiting()
            elif current_state == STATE_READY:
                update_ready()
            elif current_state == STATE_GO:
                update_go()
            elif current_state == STATE_RESULT:
                update_result()
            
            utime.sleep_ms(10)  # Kurze Pause für CPU-Entlastung
    
    except KeyboardInterrupt:
        print("\nSpiel beendet!")
        led.off()  # LED ausschalten

# Programm starten, wenn Datei direkt ausgeführt wird
if __name__ == "__main__":
    main()

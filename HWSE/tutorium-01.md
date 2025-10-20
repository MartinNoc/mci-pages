# Reaktionsspiel mit ESP32 und MicroPython

Willkommen zum Tutorial! In dieser Online-Lesson entwickelst du Schritt für Schritt ein Reaktionsspiel mit dem ESP32 Microcontroller und MicroPython.

## 🎯 Was du lernen wirst

- Zustandsautomaten in embedded Systemen verstehen und implementieren
- Hardware-Komponenten (LEDs, Buttons, Buzzer) mit MicroPython steuern
- Timer und Zeitmessung für präzise Timing-Anwendungen
- PWM für LED-Helligkeitssteuerung verwenden
- Button-Entprellung implementieren
- Strukturierte Programmierung in MicroPython

## 🎮 Das Reaktionsspiel

Du entwickelst ein interaktives Spiel, bei dem Spieler:innen so schnell wie möglich auf ein LED-Signal reagieren müssen. Das Spiel misst die Reaktionszeit und gibt audio-visuelles Feedback.

### Spielablauf:
1. **WAITING**: Das Spiel wartet auf den Start
2. **READY**: Nach dem Drücken des Buttons wartet das Spiel eine zufällige Zeit (2-5 Sekunden)
3. **GO**: Die LED leuchtet auf - jetzt muss schnell reagiert werden!
4. **RESULT**: Die Reaktionszeit wird angezeigt und das Spiel kehrt zum Anfang zurück

## 📋 Tutorial-Struktur

Dieses Tutorial ist in mehrere Abschnitte unterteilt:

1. **[Hardware Setup](hardware-setup.md)** - Schaltung aufbauen und Komponenten verstehen
2. **[Zustandsdiagramm-Aufgabe](state-diagram-exercise.md)** - Das System als Zustandsautomat modellieren
3. **[MicroPython Grundlagen](code-basics.md)** - Grundlagen für ESP32 Programmierung
4. **[Schritt-für-Schritt Implementation](step-by-step-implementation.md)** - Das Spiel entwickeln
5. **[Tests & Erweiterungen](test-exercises.md)** - Das System testen und erweitern

## 🚀 Los geht's!

Starte mit dem [Hardware Setup](hardware-setup.md) und arbeite dich durch die einzelnen Abschnitte. Jeder Abschnitt baut auf dem vorherigen auf, deshalb ist es wichtig, die Reihenfolge einzuhalten.

Viel Spaß beim Programmieren! 🎯
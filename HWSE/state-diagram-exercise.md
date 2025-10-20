# Zustandsdiagramm-Aufgabe

Bevor wir mit der Programmierung beginnen, modellieren wir unser Reaktionsspiel als **Zustandsautomat**. Das hilft uns, das Verhalten des Systems zu verstehen und strukturiert zu programmieren.

## 🧠 Was ist ein Zustandsautomat?

Ein Zustandsautomat beschreibt ein System durch:
- **Zustände**: Verschiedene Betriebsmodi
- **Übergänge**: Bedingungen zum Wechsel zwischen Zuständen  
- **Ereignisse**: Auslöser für Zustandsübergänge
- **Aktionen**: Was in jedem Zustand passiert

## 🎮 Unser Reaktionsspiel

Basierend auf der Aufgabenstellung hat unser Spiel vier Zustände:

### Zustandstabelle

| Zustand | LED-Verhalten | Buzzer | Beschreibung |
|---------|---------------|--------|--------------|
| **WAITING** | LED aus | aus | Spiel bereit, wartet auf Start |
| **READY** | LED pulsiert langsam (PWM) | 1 kurzer Beep | Zufällige Wartezeit (2–5 s) |
| **GO** | LED leuchtet hell | 3 kurze Beeps | Spieler soll so schnell wie möglich drücken |
| **RESULT** | LED blinkt | 1 langer Beep | Zeigt Reaktionszeit oder Timeout an |

## 📝 Aufgabe: Zeichne das Zustandsdiagramm

**Deine Aufgabe:** Zeichne das Zustandsdiagramm für das Reaktionsspiel auf Papier oder digital.

### Hilfestellung:

#### Zustände (als Kreise/Ellipsen):
- WAITING
- READY  
- GO
- RESULT

#### Übergänge (als Pfeile mit Beschriftung):
Überlege dir, welche **Ereignisse** oder **Bedingungen** zu einem Zustandswechsel führen:

- Button gedrückt?
- Timer abgelaufen?
- Timeout erreicht?
- Bereit für neues Spiel?

#### Fragen zum Nachdenken:
1. In welchem Zustand startet das System?
2. Was passiert, wenn der Button zu früh gedrückt wird (in READY)?
3. Was passiert, wenn der Button zu spät gedrückt wird (Timeout)?
4. Wie kommt das System zurück zum Anfang?

### Beispiel-Struktur:
```
[START] → [WAITING] → [READY] → [GO] → [RESULT] → [WAITING]
             ↑                              ↓
             └──────── (zurück zum Start) ───┘
```

## 🔍 Erweiterte Überlegungen

### Timing-Ereignisse:
- **ready_timer**: Zufällige Wartezeit in READY (2-5 Sekunden)
- **timeout_timer**: Maximale Reaktionszeit in GO (z.B. 3 Sekunden)
- **result_timer**: Anzeigezeit für Ergebnis (2-3 Sekunden)

### Fehlerbehandlung:
- Was passiert bei zu frühem Drücken?
- Wie gehst du mit Timeouts um?
- Soll es eine "Falschstart"-Meldung geben?

## 🎯 Selbstcheck

Beantworte diese Fragen mit deinem Diagramm:

1. **Startzustand**: Wo beginnt das Spiel?
2. **Button in WAITING**: Was passiert beim ersten Button-Druck?
3. **Timer in READY**: Wie wechselt das System automatisch zu GO?
4. **Button in GO**: Wie wird die Reaktionszeit gemessen?
5. **Timeout**: Was passiert, wenn nicht rechtzeitig reagiert wird?
6. **Zurück zum Start**: Wie kehrt das System zu WAITING zurück?

## 📋 Arbeitsblatt

Zeichne dein Zustandsdiagramm hier (auf Papier oder digital):

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Platz für dein Zustandsdiagramm                           │
│                                                             │
│  Tipp: Verwende Kreise für Zustände und Pfeile für         │
│        Übergänge. Beschrifte die Pfeile mit den           │
│        Bedingungen für den Übergang.                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Überprüfung

Wenn du dein Zustandsdiagramm gezeichnet hast, vergleiche es mit der [Musterlösung](solution.md#zustandsdiagramm-lösung) am Ende des Tutorials.

Keine Sorge, wenn dein Diagramm anders aussieht - es gibt verschiedene korrekte Darstellungsweisen!

## 🚀 Nächster Schritt

Hast du dein Zustandsdiagramm erstellt? Dann geht es weiter mit den [MicroPython Grundlagen](code-basics.md), wo wir die technischen Grundlagen für die Implementation lernen.

# Lerndata.py – Lektionen für die Lernphase
# trainer.png wird vom User in app/static/ abgelegt

LESSONS = [
    {
        "id": 1,
        "title": "Vorbereitung ist alles",
        "icon": "🗺️",
        "content": [
            "Bevor du auch nur einen Schritt machst: PLANE.",
            "Prüfe das Wetter 3 Tage im Voraus – nicht nur am Starttag.",
            "Teile jemandem deine Route, Startzeit und geplante Rückkehr mit.",
            "Lade deine Route offline herunter – im Gebirge gibt es oft kein Signal.",
            "Plane immer 30% mehr Zeit ein als du denkst zu brauchen.",
        ],
        "tip": "Profi-Tipp: Erstelle eine Checkliste und hake jeden Punkt ab. Vergessene Ausrüstung kann im Gebirge lebensgefährlich sein.",
    },
    {
        "id": 2,
        "title": "Das Drei-Schichten-System",
        "icon": "🧥",
        "content": [
            "Schicht 1 – Funktionsunterwäsche: Leitet Schweiß vom Körper weg. NIEMALS Baumwolle!",
            "Schicht 2 – Isolationsschicht: Fleece oder Daunen halten die Wärme.",
            "Schicht 3 – Wetterschutz: Winddicht, wasserdicht, atmungsaktiv.",
            "Im Gebirge kann die Temperatur in 30 Minuten um 15°C fallen.",
            "Ziehe Schichten aus bevor du schwitzt – nasse Kleidung kühlt extrem schnell.",
        ],
        "tip": "Profi-Tipp: Packe immer eine Notfall-Wärmeschicht extra ein, auch im Sommer. Auf 2000m+ ist Schnee im Juli möglich.",
    },
    {
        "id": 3,
        "title": "Navigation & Orientierung",
        "icon": "🧭",
        "content": [
            "Lerne eine topografische Karte zu lesen – Höhenlinien zeigen Steilheit.",
            "Ein Kompass funktioniert immer, auch ohne Akku.",
            "GPS-Apps: Komoot, AllTrails oder ViewRanger – immer offline speichern.",
            "Orientierungspunkte merken: Gipfel, Täler, Bachläufe.",
            "Bei Nebel: Kompass und Karte sind deine einzige Rettung.",
        ],
        "tip": "Profi-Tipp: Übe Kompass-Navigation zuhause. Im Notfall musst du es ohne Nachdenken können.",
    },
    {
        "id": 4,
        "title": "Wasser & Ernährung",
        "icon": "💧",
        "content": [
            "Mindestens 0,5L pro Stunde – bei Hitze oder steilem Gelände bis 1L.",
            "Trinke bevor du Durst hast – Durst ist bereits ein Zeichen von Dehydration.",
            "Bergquellen können Keime enthalten – Wasserfilter oder Purification Tabs mitnehmen.",
            "Kalorienreiche Snacks: Nüsse, Riegel, Trockenfrüchte alle 45-60 Minuten.",
            "Salzverlust durch Schwitzen: Elektrolyt-Tabs oder Salzstangen helfen.",
        ],
        "tip": "Profi-Tipp: Berechne deinen Wasserbedarf vor der Tour. 0,5L × Stunden + 1L Reserve = Mindestmenge.",
    },
    {
        "id": 5,
        "title": "Erste Hilfe im Gelände",
        "icon": "🩹",
        "content": [
            "PECH-Regel bei Verstauchungen: Pause, Eis/Kühlen, Compression, Hochlagern.",
            "Blasen: Nicht aufstechen! Desinfizieren und mit Blasenpflaster schützen.",
            "Wunden im Gebirge immer desinfizieren – Infektionen heilen langsam.",
            "Notruf Europa: 112 – auch ohne Netz oft erreichbar.",
            "Bergrettung: In Österreich 140, in Deutschland 112.",
        ],
        "tip": "Profi-Tipp: Mache einen Erste-Hilfe-Kurs speziell für Outdoor/Wildnis. Das Wissen kann Leben retten.",
    },
    {
        "id": 6,
        "title": "Wetter & Gefahren",
        "icon": "⛈️",
        "content": [
            "Gewitter: Gipfel und Grate sofort verlassen. Mulden aufsuchen, kauern.",
            "Faustregel: Donner hören = sofort absteigen. Keine Ausnahmen.",
            "Schneefelder im Sommer: Ohne Steigeisen und Pickel extrem rutschig.",
            "Steinschlag: Helm tragen, unter Überhängen nicht rasten.",
            "Nebel: Tempo reduzieren, Orientierungspunkte häufiger prüfen.",
        ],
        "tip": "Profi-Tipp: Lerne Wolkenformationen zu lesen. Cumulonimbus (Amboss-Form) = Gewitter in 30-60 Minuten.",
    },
    {
        "id": 7,
        "title": "Höhenkrankheit",
        "icon": "🏔️",
        "content": [
            "Tritt meist ab 2500m auf – je schneller der Aufstieg, desto höher das Risiko.",
            "Symptome: Kopfschmerzen, Übelkeit, Schwindel, Schlaflosigkeit.",
            "Regel: Nicht mehr als 300-500 Höhenmeter pro Tag über 2500m aufsteigen.",
            "Einzige sichere Behandlung: Abstieg. Sofort, nicht warten.",
            "Ibuprofen kann Kopfschmerzen lindern, behandelt aber nicht die Ursache.",
        ],
        "tip": "Profi-Tipp: 'Climb high, sleep low' – tagsüber höher gehen, nachts tiefer schlafen. Das beschleunigt die Akklimatisation.",
    },
    {
        "id": 8,
        "title": "Notfall & Überleben",
        "icon": "🆘",
        "content": [
            "Bergnot-Signal: 6 Signale pro Minute (Pfeifen/Licht), 1 Min. Pause, wiederholen.",
            "Biwak: Im Notfall Schutz vor Wind suchen, Rettungsdecke einwickeln.",
            "Feuer machen: Nur im absoluten Notfall und wenn erlaubt.",
            "Orientierung ohne Kompass: Sonne geht im Osten auf, im Westen unter.",
            "Wasser finden: Bergab gehen – Wasser fließt immer ins Tal.",
        ],
        "tip": "Profi-Tipp: Packe immer ein Biwaksack, Pfeife, Feuerzeug und Rettungsdecke ein – auch auf Tagestouren.",
    },
]

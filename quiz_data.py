QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Was solltest du vor einer Wanderung immer tun?",
        "options": ["Route planen", "Ohne Wasser starten", "Nur auf Glueck hoffen", "Erst unterwegs entscheiden"],
        "correct_answer": "Route planen",
        "explanation": "Eine gute Tour beginnt mit Planung, Wettercheck und einer klaren Route.",
    },
    {
        "id": 2,
        "question": "Welche Schicht liegt direkt auf der Haut?",
        "options": ["Funktionsschicht", "Regenjacke", "Daunenjacke", "Wintermantel"],
        "correct_answer": "Funktionsschicht",
        "explanation": "Die erste Schicht transportiert Feuchtigkeit vom Koerper weg.",
    },
    {
        "id": 3,
        "question": "Was ist bei Navigation ohne Netz besonders wichtig?",
        "options": ["Offline-Karte", "Mehr Musik", "Hellere Schuhe", "Weniger Pausen"],
        "correct_answer": "Offline-Karte",
        "explanation": "Im Gebirge ist Offline-Navigation oft entscheidend.",
    },
    {
        "id": 4,
        "question": "Wann solltest du trinken?",
        "options": ["Regelmaessig", "Erst bei starkem Durst", "Nur am Gipfel", "Nur bei Regen"],
        "correct_answer": "Regelmaessig",
        "explanation": "Durst ist oft schon ein Spaetsignal fuer beginnende Dehydrierung.",
    },
    {
        "id": 5,
        "question": "Was geht bei einer Bergtour immer vor?",
        "options": ["Sicherheit", "Tempo", "Selfies", "Rekorde"],
        "correct_answer": "Sicherheit",
        "explanation": "Jede Entscheidung sollte zuerst nach dem Sicherheitsrisiko bewertet werden.",
    },
]


def get_quiz_questions(_learned_topics=None):
    return QUIZ_QUESTIONS

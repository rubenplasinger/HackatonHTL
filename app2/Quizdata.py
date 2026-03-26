def get_quiz_questions(learned_topics=None):
    """
    Diese Funktion gibt 20 Quizfragen zurück.
    Aktuell sind die Inhalte absichtlich leer / generisch,
    damit sie später automatisch an die Lernphase angepasst werden können.

    Jede Frage hat:
    - id
    - topic
    - question
    - options
    - correct_answer
    - explanation
    - improvement_tip

    WICHTIG:
    Die Felder question, options, correct_answer, explanation, improvement_tip
    sind Platzhalter und sollen später aus der Lernphase generiert oder befüllt werden.
    """

    if learned_topics is None:
        learned_topics = []

    default_topics = [
        "ausruestung",
        "wetter",
        "navigation",
        "notfall",
        "wasser",
        "nahrung",
        "tempo",
        "pausen",
        "sicherheit",
        "orientierung",
        "hoehenmeter",
        "extremwanderung",
        "erste_hilfe",
        "nachtwanderung",
        "wegplanung",
        "risikobewertung",
        "kommunikation",
        "survival",
        "gruppenverhalten",
        "entscheidungsfindung"
    ]

    # Falls die Lernphase weniger Themen liefert, wird aufgefüllt
    topics_for_quiz = (learned_topics + default_topics)[:20]

    questions = []

    for i in range(20):
        topic = topics_for_quiz[i] if i < len(topics_for_quiz) else f"thema_{i+1}"

        questions.append({
            "id": i + 1,
            "topic": topic,
            "question": f"Platzhalter-Frage {i+1} zu '{topic}'",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "correct_answer": "Option A",
            "explanation": f"Hier kommt später die Erklärung für Thema '{topic}' hin.",
            "improvement_tip": f"Hier kommt später ein Verbesserungsvorschlag für Thema '{topic}' hin."
        })

    return questions
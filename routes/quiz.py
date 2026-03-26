import random

from flask import Blueprint, redirect, render_template, request, session, url_for

from quiz_data import get_quiz_questions


quiz_bp = Blueprint("quiz", __name__)


def _question_by_id(question_id: int):
    questions = session.get("quiz_questions", [])
    return next((question for question in questions if question["id"] == question_id), None)


def _build_quiz_session():
    questions = get_quiz_questions(session.get("learned_topics"))
    question_ids = [question["id"] for question in questions]
    random.shuffle(question_ids)

    option_orders = {}
    for question in questions:
        shuffled_options = question["options"][:]
        random.shuffle(shuffled_options)
        option_orders[str(question["id"])] = shuffled_options

    session["quiz_questions"] = questions
    session["quiz_answers"] = {}
    session["quiz_order"] = question_ids
    session["quiz_options"] = option_orders


@quiz_bp.get("/quiz/start")
def start_quiz():
    _build_quiz_session()
    return redirect(url_for("quiz.question", question_index=1))


@quiz_bp.route("/quiz/question/<int:question_index>", methods=["GET", "POST"])
def question(question_index: int):
    quiz_order = session.get("quiz_order")
    quiz_options = session.get("quiz_options")

    if not quiz_order or not quiz_options:
        return redirect(url_for("quiz.start_quiz"))

    total_questions = len(quiz_order)
    if question_index < 1 or question_index > total_questions:
        return redirect(url_for("quiz.start_quiz"))

    current_question_id = quiz_order[question_index - 1]
    question_data = _question_by_id(current_question_id)
    if question_data is None:
        return redirect(url_for("quiz.start_quiz"))

    if request.method == "POST":
        answer = request.form.get("answer")
        if answer:
            answers = session.get("quiz_answers", {})
            answers[str(current_question_id)] = answer
            session["quiz_answers"] = answers

        next_index = question_index + 1
        if next_index > total_questions:
            return redirect(url_for("quiz.result"))
        return redirect(url_for("quiz.question", question_index=next_index))

    question_view = {
        "id": question_data["id"],
        "question": question_data["question"],
        "options": quiz_options.get(str(current_question_id), question_data["options"]),
    }

    return render_template(
        "quiz.html",
        question=question_view,
        question_index=question_index,
        total=total_questions,
    )


@quiz_bp.get("/quiz/result")
def result():
    answers = session.get("quiz_answers", {})
    quiz_questions = session.get("quiz_questions", [])
    quiz_order = session.get("quiz_order", [question["id"] for question in quiz_questions])

    results = []
    correct_count = 0

    for question_id in quiz_order:
        question = _question_by_id(question_id)
        if question is None:
            continue

        user_answer = answers.get(str(question_id))
        is_correct = user_answer == question["correct_answer"]
        if is_correct:
            correct_count += 1

        results.append(
            {
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
                "explanation": question["explanation"],
            }
        )

    total = len(quiz_order) if quiz_order else len(quiz_questions)
    score_percent = round((correct_count / total) * 100) if total else 0

    if score_percent >= 80:
        score_label = "Stark vorbereitet"
        score_tone = "success"
    elif score_percent >= 50:
        score_label = "Solide Grundlage"
        score_tone = "warning"
    else:
        score_label = "Mehr Uebung noetig"
        score_tone = "danger"

    return render_template(
        "quiz_result.html",
        results=results,
        correct=correct_count,
        total=total,
        score_percent=score_percent,
        score_label=score_label,
        score_tone=score_tone,
    )

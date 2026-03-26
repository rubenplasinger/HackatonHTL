import random

from flask import Blueprint, render_template, request, session, redirect, url_for

from Quizdata import get_quiz_questions

quiz_bp = Blueprint('quiz', __name__)


def _question_by_id(question_id):
    questions = session.get('quiz_questions', [])
    return next((q for q in questions if q['id'] == question_id), None)


def _correct_option(question):
    return question['correct_answer']


def _build_quiz_session():
    learned_topics = session.get('learned_topics')
    questions = get_quiz_questions(learned_topics)
    question_ids = [question['id'] for question in questions]
    random.shuffle(question_ids)

    option_orders = {}
    for question in questions:
        shuffled_options = question['options'][:]
        random.shuffle(shuffled_options)
        option_orders[str(question['id'])] = shuffled_options

    session['quiz_questions'] = questions
    session['quiz_answers'] = {}
    session['quiz_order'] = question_ids
    session['quiz_options'] = option_orders


@quiz_bp.route('/quiz/start')
def start():
    _build_quiz_session()
    return redirect(url_for('quiz.question', q_id=1))


@quiz_bp.route('/quiz/question/<int:q_id>', methods=['GET', 'POST'])
def question(q_id):
    quiz_order = session.get('quiz_order')
    quiz_options = session.get('quiz_options')

    if not quiz_order or not quiz_options:
        return redirect(url_for('quiz.start'))

    total_questions = len(quiz_order)
    if q_id < 1 or q_id > total_questions:
        return redirect(url_for('quiz.start'))

    current_question_id = quiz_order[q_id - 1]
    question_data = _question_by_id(current_question_id)
    if question_data is None:
        return redirect(url_for('quiz.start'))

    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer:
            answers = session.get('quiz_answers', {})
            answers[str(current_question_id)] = answer
            session['quiz_answers'] = answers

        next_id = q_id + 1
        if next_id > total_questions:
            return redirect(url_for('quiz.result'))
        return redirect(url_for('quiz.question', q_id=next_id))

    question_view = {
        'id': question_data['id'],
        'question': question_data['question'],
        'options': quiz_options.get(str(current_question_id), question_data['options']),
    }

    return render_template('quiz.html', question=question_view, q_id=q_id, total=total_questions)


@quiz_bp.route('/quiz/result')
def result():
    answers = session.get('quiz_answers', {})
    quiz_questions = session.get('quiz_questions', [])
    quiz_order = session.get('quiz_order', [question['id'] for question in quiz_questions])
    quiz_options = session.get('quiz_options', {})

    results = []
    correct_count = 0

    for question_id in quiz_order:
        question = _question_by_id(question_id)
        if question is None:
            continue

        correct_answer = _correct_option(question)
        user_answer = answers.get(str(question_id))
        is_correct = user_answer == correct_answer
        if is_correct:
            correct_count += 1

        results.append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question['explanation'] if not is_correct else None,
            'options': quiz_options.get(str(question_id), question['options']),
        })

    total = len(quiz_order) if quiz_order else len(quiz_questions)
    survival_rate = round((correct_count / total) * 100) if total else 0

    if survival_rate >= 80:
        survival_level = 'hoch'
        survival_color = 'green'
        survival_message = 'Du bist gut vorbereitet fuer deine Wanderung!'
    elif survival_rate >= 50:
        survival_level = 'mittel'
        survival_color = 'orange'
        survival_message = 'Du solltest noch einige Bereiche vertiefen, bevor du losgehst.'
    else:
        survival_level = 'niedrig'
        survival_color = 'red'
        survival_message = 'Bitte lerne die Grundlagen nochmal - deine Sicherheit haengt davon ab!'

    return render_template(
        'result.html',
        results=results,
        correct=correct_count,
        total=total,
        survival_rate=survival_rate,
        survival_level=survival_level,
        survival_color=survival_color,
        survival_message=survival_message,
    )

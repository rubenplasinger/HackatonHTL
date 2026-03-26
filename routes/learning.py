from flask import Blueprint, redirect, render_template, url_for

from learning_data import LESSONS


learning_bp = Blueprint("learning", __name__)


@learning_bp.get("/lernen")
def start_learning():
    return redirect(url_for("learning.lesson", lesson_id=1))


@learning_bp.get("/lernen/<int:lesson_id>")
def lesson(lesson_id: int):
    if lesson_id < 1 or lesson_id > len(LESSONS):
        return redirect(url_for("learning.lesson", lesson_id=1))

    lesson_data = LESSONS[lesson_id - 1]
    return render_template(
        "learning.html",
        lesson=lesson_data,
        lesson_id=lesson_id,
        total=len(LESSONS),
    )

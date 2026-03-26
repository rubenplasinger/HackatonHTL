from flask import Blueprint, render_template, redirect, url_for
from Lerndata import LESSONS

lern_bp = Blueprint('lern', __name__)

@lern_bp.route('/lernen')
def start():
    return redirect(url_for('lern.lektion', l_id=1))

@lern_bp.route('/lernen/<int:l_id>')
def lektion(l_id):
    if l_id < 1 or l_id > len(LESSONS):
        return redirect(url_for('lern.lektion', l_id=1))
    lesson = LESSONS[l_id - 1]
    return render_template('lernphase.html', lesson=lesson, l_id=l_id, total=len(LESSONS))

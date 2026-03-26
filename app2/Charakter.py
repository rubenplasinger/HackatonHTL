from flask import Blueprint, render_template, request, session, redirect, url_for

char_bp = Blueprint('char', __name__)

PART_ORDER_BY_GENDER = {
    'm': ['kopf', 'koerper', 'hose', 'schuhe'],
    'w': ['kopf', 'koerper', 'hose', 'schuhe'],
}

DEFAULT_PARTS = {'kopf': 1, 'koerper': 1, 'hose': 1, 'schuhe': 1}

ASSET_FILES = {
    'm': {
        'kopf': {
            1: 'char/Kopf-1-Junge.png',
            2: 'char/Kopf-2-Junge.png',
            3: 'char/Kopf-3-Junge.png',
        },
        'koerper': {
            1: 'char/pulli-1-Junge.png',
            2: 'char/pulli-2-Junge.png',
            3: 'char/pulli-3-Junge.png',
        },
        'hose': {
            1: 'char/hose-1-Junge.png',
            2: 'char/hose-2-Junge.png',
            3: 'char/hose-3-Junge.png',
        },
        'schuhe': {
            1: 'char/schuhe-1-Junge.png',
            2: 'char/schuhe-2-Junge.png',
            3: 'char/schuhe-3-Junge.png',
        },
    },
    'w': {
        'kopf': {
            1: 'char/Kopf-1.png',
            2: 'char/Kopf_2.png',
            3: 'char/Kopf_3.png',
        },
        'koerper': {
            1: 'char/Oberteil_1.png',
            2: 'char/Oberteil_2.png',
            3: 'char/Oberteil-3.png',
        },
        'hose': {
            1: 'char/Hose-1.png',
            2: 'char/Hose-2.png',
            3: 'char/Hose-3.png',
        },
        'schuhe': {
            1: 'char/Füß-1.png',
            2: 'char/Füß-2.png',
            3: 'char/Füß-3.png',
        },
    },
}

PARTS = {
    'm': {'kopf': 3, 'koerper': 3, 'hose': 3, 'schuhe': 3},
    'w': {'kopf': 3, 'koerper': 3, 'hose': 3, 'schuhe': 3},
}


@char_bp.route('/charakter', methods=['GET', 'POST'])
def gender():
    if request.method == 'POST':
        geschlecht = request.form.get('geschlecht')
        if geschlecht in ('m', 'w'):
            session['char_geschlecht'] = geschlecht
            session['char_parts'] = DEFAULT_PARTS.copy()
            return redirect(url_for('char.editor'))
    return render_template('charakter_gender.html')


@char_bp.route('/charakter/editor', methods=['GET', 'POST'])
def editor():
    geschlecht = session.get('char_geschlecht', 'm')
    parts = session.get('char_parts', DEFAULT_PARTS.copy())
    maxima = PARTS[geschlecht]
    part_order = PART_ORDER_BY_GENDER[geschlecht]

    if request.method == 'POST':
        teil = request.form.get('teil')
        richtung = request.form.get('richtung')
        if teil in part_order and richtung in ('vor', 'zurueck'):
            current = parts[teil]
            maximum = maxima[teil]
            if richtung == 'vor':
                parts[teil] = (current % maximum) + 1
            else:
                parts[teil] = ((current - 2) % maximum) + 1
            session['char_parts'] = parts

    image_layers = [
        {'teil': teil, 'filename': ASSET_FILES[geschlecht][teil][parts[teil]]}
        for teil in part_order
    ]

    return render_template(
        'charakter_editor.html',
        geschlecht=geschlecht,
        parts=parts,
        maxima=maxima,
        image_layers=image_layers,
        part_order=part_order,
    )

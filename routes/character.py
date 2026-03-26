from flask import Blueprint, redirect, render_template, request, session, url_for


character_bp = Blueprint("character", __name__)

PART_ORDER = ["kopf", "koerper", "hose", "schuhe"]
DEFAULT_PARTS = {"kopf": 1, "koerper": 1, "hose": 1, "schuhe": 1}

ASSET_FILES = {
    "m": {
        "kopf": {1: "char/Kopf-1-Junge.png", 2: "char/Kopf-2-Junge.png", 3: "char/Kopf-3-Junge.png"},
        "koerper": {1: "char/pulli-1-Junge.png", 2: "char/pulli-2-Junge.png", 3: "char/pulli-3-Junge.png"},
        "hose": {1: "char/hose-1-Junge.png", 2: "char/hose-2-Junge.png", 3: "char/hose-3-Junge.png"},
        "schuhe": {1: "char/schuhe-1-Junge.png", 2: "char/schuhe-2-Junge.png", 3: "char/schuhe-3-Junge.png"},
    },
    "w": {
        "kopf": {1: "char/Kopf-1.png", 2: "char/Kopf_2.png", 3: "char/Kopf_3.png"},
        "koerper": {1: "char/Oberteil_1.png", 2: "char/Oberteil_2.png", 3: "char/Oberteil-3.png"},
        "hose": {1: "char/Hose-1.png", 2: "char/Hose-2.png", 3: "char/Hose-3.png"},
        "schuhe": {1: "char/Fuss-1.png", 2: "char/Fuss-2.png", 3: "char/Fuss-3.png"},
    },
}


@character_bp.route("/charakter", methods=["GET", "POST"])
def select_character():
    if request.method == "POST":
        gender = request.form.get("geschlecht")
        if gender in ("m", "w"):
            session["char_geschlecht"] = gender
            session["char_parts"] = DEFAULT_PARTS.copy()
            return redirect(url_for("character.character_editor"))

    return render_template("character_select.html")


@character_bp.route("/charakter/editor", methods=["GET", "POST"])
def character_editor():
    gender = session.get("char_geschlecht", "m")
    parts = session.get("char_parts", DEFAULT_PARTS.copy())

    if request.method == "POST":
        part = request.form.get("teil")
        direction = request.form.get("richtung")
        if part in PART_ORDER and direction in ("vor", "zurueck"):
            current = parts[part]
            maximum = len(ASSET_FILES[gender][part])
            if direction == "vor":
                parts[part] = (current % maximum) + 1
            else:
                parts[part] = ((current - 2) % maximum) + 1
            session["char_parts"] = parts

    image_layers = [
        {"teil": part, "filename": ASSET_FILES[gender][part][parts[part]]}
        for part in PART_ORDER
    ]

    return render_template(
        "character_editor.html",
        gender=gender,
        parts=parts,
        part_order=PART_ORDER,
        image_layers=image_layers,
    )

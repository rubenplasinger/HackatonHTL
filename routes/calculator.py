from flask import Blueprint, jsonify, request

from models import Provision


calculator_bp = Blueprint("calculator", __name__)

INTENSITY_RULES = {
    "low": {"water_per_day": 2.0, "calories_per_day": 2000},
    "medium": {"water_per_day": 2.5, "calories_per_day": 2500},
    "high": {"water_per_day": 3.0, "calories_per_day": 3000},
}


def error_response(message: str, status_code: int):
    return jsonify({"error": message}), status_code


def parse_json_body():
    payload = request.get_json(silent=True)
    if payload is None:
        return None, error_response("Request body must be valid JSON", 400)
    return payload, None


@calculator_bp.post("/calculate/hiking")
def calculate_hiking():
    """
    curl -X POST http://127.0.0.1:5000/calculate/hiking -H "Content-Type: application/json" -d "{\"duration_days\":3,\"intensity\":\"high\"}"
    """
    payload, error = parse_json_body()
    if error:
        return error

    duration_days = payload.get("duration_days")
    intensity = payload.get("intensity", "medium")

    if not isinstance(duration_days, (int, float)) or duration_days <= 0:
        return error_response("Field 'duration_days' must be a positive number", 400)

    if intensity not in INTENSITY_RULES:
        return error_response(
            "Field 'intensity' must be one of: low, medium, high",
            400,
        )

    duration_days = float(duration_days)
    rules = INTENSITY_RULES[intensity]
    water_liters = round(duration_days * rules["water_per_day"], 2)
    calories_kcal = round(duration_days * rules["calories_per_day"], 2)

    return jsonify(
        {
            "water_liters": water_liters,
            "calories_kcal": calories_kcal,
            "suggested_items": [
                {"name": "Water", "quantity": water_liters, "unit": "L"},
                {"name": "Food", "quantity": calories_kcal, "unit": "kcal"},
            ],
        }
    )


@calculator_bp.post("/calculate/rationing")
def calculate_rationing():
    """
    curl -X POST http://127.0.0.1:5000/calculate/rationing -H "Content-Type: application/json" -d "{\"days\":5}"
    """
    payload, error = parse_json_body()
    if error:
        return error

    days = payload.get("days")
    if not isinstance(days, (int, float)) or days <= 0:
        return error_response("Field 'days' must be a positive number", 400)

    days = float(days)
    provisions = Provision.query.order_by(Provision.name.asc()).all()

    rations = [
        {
            "name": item.name,
            "per_day": round(item.quantity / days, 2),
            "unit": item.unit,
        }
        for item in provisions
    ]

    return jsonify({"rations": rations})

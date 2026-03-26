from flask import Blueprint, jsonify, request

from models import Provision, db


provisions_bp = Blueprint("provisions", __name__)


def error_response(message: str, status_code: int):
    return jsonify({"error": message}), status_code


def parse_json_body():
    payload = request.get_json(silent=True)
    if payload is None:
        return None, error_response("Request body must be valid JSON", 400)
    return payload, None


def validate_provision_payload(payload: dict, require_all_fields: bool = True):
    required_fields = ("name", "quantity", "unit")
    if require_all_fields:
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            return None, error_response(
                f"Missing required fields: {', '.join(missing_fields)}",
                400,
            )

    name = payload.get("name")
    quantity = payload.get("quantity")
    unit = payload.get("unit")

    validated = {}

    if name is not None:
        if not isinstance(name, str) or not name.strip():
            return None, error_response("Field 'name' must be a non-empty string", 400)
        validated["name"] = name.strip()

    if quantity is not None:
        if not isinstance(quantity, (int, float)) or quantity < 0:
            return None, error_response(
                "Field 'quantity' must be a non-negative number",
                400,
            )
        validated["quantity"] = float(quantity)

    if unit is not None:
        if not isinstance(unit, str) or not unit.strip():
            return None, error_response("Field 'unit' must be a non-empty string", 400)
        validated["unit"] = unit.strip()

    return validated, None


@provisions_bp.get("/provisions")
def list_provisions():
    """
    curl http://127.0.0.1:5000/provisions
    """
    provisions = Provision.query.order_by(Provision.name.asc()).all()
    return jsonify({"items": [item.to_dict() for item in provisions]})


@provisions_bp.post("/provisions")
def create_provision():
    """
    curl -X POST http://127.0.0.1:5000/provisions -H "Content-Type: application/json" -d "{\"name\":\"Water\",\"quantity\":10,\"unit\":\"L\"}"
    """
    payload, error = parse_json_body()
    if error:
        return error

    validated, error = validate_provision_payload(payload)
    if error:
        return error

    existing = Provision.query.filter_by(name=validated["name"]).first()
    if existing:
        return error_response("Provision with this name already exists", 409)

    provision = Provision(**validated)
    db.session.add(provision)
    db.session.commit()

    return jsonify(provision.to_dict()), 201


@provisions_bp.put("/provisions/<int:provision_id>")
def update_provision(provision_id: int):
    """
    curl -X PUT http://127.0.0.1:5000/provisions/1 -H "Content-Type: application/json" -d "{\"quantity\":8}"
    """
    provision = Provision.query.get(provision_id)
    if not provision:
        return error_response("Provision not found", 404)

    payload, error = parse_json_body()
    if error:
        return error

    validated, error = validate_provision_payload(payload, require_all_fields=False)
    if error:
        return error

    if not validated:
        return error_response("No valid fields provided for update", 400)

    if "name" in validated:
        duplicate = Provision.query.filter(
            Provision.name == validated["name"], Provision.id != provision_id
        ).first()
        if duplicate:
            return error_response("Provision with this name already exists", 409)

    for field, value in validated.items():
        setattr(provision, field, value)

    db.session.commit()
    return jsonify(provision.to_dict())


@provisions_bp.delete("/provisions/<int:provision_id>")
def delete_provision(provision_id: int):
    """
    curl -X DELETE http://127.0.0.1:5000/provisions/1
    """
    provision = Provision.query.get(provision_id)
    if not provision:
        return error_response("Provision not found", 404)

    db.session.delete(provision)
    db.session.commit()
    return jsonify({"message": "Provision deleted", "id": provision_id})


@provisions_bp.post("/provisions/<int:provision_id>/consume")
def consume_provision(provision_id: int):
    """
    curl -X POST http://127.0.0.1:5000/provisions/1/consume -H "Content-Type: application/json" -d "{\"quantity\":2}"
    """
    provision = Provision.query.get(provision_id)
    if not provision:
        return error_response("Provision not found", 404)

    payload, error = parse_json_body()
    if error:
        return error

    amount = payload.get("quantity")
    if not isinstance(amount, (int, float)) or amount < 0:
        return error_response(
            "Field 'quantity' must be a non-negative number",
            400,
        )

    amount = float(amount)
    if amount > provision.quantity:
        return error_response("Consumption cannot reduce quantity below 0", 400)

    provision.quantity -= amount
    db.session.commit()
    return jsonify(provision.to_dict())


@provisions_bp.post("/provisions/from-calculation")
def create_from_calculation():
    """
    curl -X POST http://127.0.0.1:5000/provisions/from-calculation -H "Content-Type: application/json" -d "{\"items\":[{\"name\":\"Water\",\"quantity\":7.5,\"unit\":\"L\"},{\"name\":\"Food\",\"quantity\":7500,\"unit\":\"kcal\"}]}"
    """
    payload, error = parse_json_body()
    if error:
        return error

    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return error_response("Field 'items' must be a non-empty list", 400)

    updated_items = []

    for item in items:
        if not isinstance(item, dict):
            return error_response("Each item must be an object", 400)

        validated, item_error = validate_provision_payload(item)
        if item_error:
            return item_error

        provision = Provision.query.filter_by(name=validated["name"]).first()
        if provision:
            if provision.unit != validated["unit"]:
                return error_response(
                    f"Unit mismatch for existing provision '{provision.name}'",
                    400,
                )
            provision.quantity += validated["quantity"]
        else:
            provision = Provision(**validated)
            db.session.add(provision)

        updated_items.append(provision)

    db.session.commit()
    return jsonify({"items": [item.to_dict() for item in updated_items]}), 201

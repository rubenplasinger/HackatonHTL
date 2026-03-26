import json
import math
from pathlib import Path

import requests
from flask import Blueprint, jsonify, render_template, request


planner_bp = Blueprint("planner", __name__)

DEFAULT_LAT = 47.5031
DEFAULT_LON = 9.7471

DATA_PATH = Path(__file__).resolve().parent.parent / "planner_locations.json"
with DATA_PATH.open("r", encoding="utf-8") as file:
    LOCATIONS = json.load(file)

CITIES = [
    {"name": "Bregenz", "lat": 47.5031, "lon": 9.7471},
    {"name": "Dornbirn", "lat": 47.4125, "lon": 9.7417},
    {"name": "Feldkirch", "lat": 47.2386, "lon": 9.5990},
    {"name": "Bludenz", "lat": 47.1544, "lon": 9.8222},
    {"name": "Hohenems", "lat": 47.3622, "lon": 9.6883},
    {"name": "Lustenau", "lat": 47.4267, "lon": 9.6583},
    {"name": "Hard", "lat": 47.4851, "lon": 9.6922},
    {"name": "Rankweil", "lat": 47.2711, "lon": 9.6455},
]

SURVIVAL_RULES = {
    "lost": ["S.T.O.P.: Sit, Think, Observe, Plan.", "Bleib an einem sicheren Ort.", "Mach dich sichtbar.", "Bewege dich nur mit Plan."],
    "injured": ["Verletzung beurteilen.", "Blutung stillen und warm bleiben.", "112 anrufen.", "Auf Hilfe aufmerksam machen."],
    "no_water": ["Energie sparen.", "Schatten suchen.", "Nicht ohne Wasser viel essen.", "Nach Feuchtigkeit oder Quellen suchen."],
    "no_food": ["Ruhe bewahren.", "Kraft sparen.", "Nur bekannte essbare Quellen nutzen.", "Prioritaet bleibt Wasser und Sicherheit."],
    "no_reception": ["Hoeheren oder offeneren Punkt suchen.", "Standort wechseln.", "Spaeter erneut versuchen.", "Bei Gefahr nicht weiter isolieren."],
    "cold": ["Windschutz suchen.", "Vom Boden isolieren.", "Trocken bleiben.", "Zusammenruecken und Waerme halten."],
}


def haversine(lat1, lon1, lat2, lon2):
    radius = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a_val = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a_val), math.sqrt(1 - a_val))


def local_matcher(user_input, locations):
    user_lower = user_input.lower()
    feature_keywords = {
        "water": ["water", "see", "lake", "baden", "schwimmen"],
        "mountain": ["berg", "mountain", "gipfel", "alps"],
        "hiking": ["wander", "hike", "trek"],
        "family": ["familie", "family", "kids", "leicht", "einfach"],
        "nature": ["natur", "nature", "wald", "forest"],
        "relaxation": ["relax", "ruhig", "entspannung"],
        "alpine": ["alpin", "alpine", "hoch"],
        "scenic": ["panorama", "aussicht", "blick", "scenic"],
        "challenging": ["schwer", "anspruchsvoll", "hard", "extrem"],
        "multi_day": ["3 tage", "4 tage", "5 tage", "mehrtag", "uebernachtung"],
    }
    duration_keywords = {
        5: ["5 tage", "fuenf tage"],
        4: ["4 tage", "vier tage"],
        3: ["3 tage", "drei tage"],
        2: ["2 tage", "zwei tage"],
        1: ["1 tag", "tagestour", "eintaegig"],
    }

    desired = set()
    for feature, keywords in feature_keywords.items():
        if any(keyword in user_lower for keyword in keywords):
            desired.add(feature)
    if not desired:
        desired = {"water", "mountain", "hiking", "nature"}

    duration = None
    for duration_value, keywords in duration_keywords.items():
        if any(keyword in user_lower for keyword in keywords):
            duration = duration_value
            break

    results = []
    for location in locations:
        score = 0
        reasons = []
        location_features = set(location.get("features", []))
        matched = desired & location_features
        score += len(matched) * 2
        if matched:
            reasons.append(f"Passt zu: {', '.join(sorted(matched))}")
        if duration and duration in location.get("suitable_duration", []):
            score += 2
            reasons.append(f"Geeignet fuer {duration} Tage")

        hiking_info = location.get("hiking_info", {})
        if score >= 3:
            results.append(
                {
                    "name": location["name"],
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                    "reason": ". ".join(reasons) if reasons else "Passt zu deiner Anfrage",
                    "match_score": min(10, score),
                    "distance_km": round(location.get("distance_km", 0), 2),
                    "hiking_info": hiking_info,
                }
            )

    results.sort(key=lambda item: item["match_score"], reverse=True)
    preferences = ", ".join(sorted(desired))
    if duration:
        preferences += f", {duration} Tage"
    return {"preferences_interpreted": preferences, "results": results[:5]}


def search_locations(user_input, user_lat, user_lon):
    enriched = []
    for location in LOCATIONS:
        distance = haversine(user_lat, user_lon, location["latitude"], location["longitude"])
        enriched.append({**location, "distance_km": distance})

    result = local_matcher(user_input, enriched)
    return {
        "radius_used": "Alle Orte",
        "user_location": {"lat": user_lat, "lon": user_lon},
        "locations_found": len(enriched),
        **result,
    }


def calculate_bearing(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    x_val = math.sin(math.radians(lon2 - lon1)) * math.cos(phi2)
    y_val = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(math.radians(lon2 - lon1))
    bearing = (math.degrees(math.atan2(x_val, y_val)) + 360) % 360
    directions = ["N", "NO", "O", "SO", "S", "SW", "W", "NW"]
    return f"{directions[round(bearing / 45) % 8]} ({int(bearing)} Grad)"


@planner_bp.get("/tourenplaner")
def planner_page():
    return render_template("planner.html")


@planner_bp.post("/planner/search")
def planner_search():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get("message", "").strip()
    user_lat = payload.get("lat", DEFAULT_LAT)
    user_lon = payload.get("lon", DEFAULT_LON)
    if not user_message:
        return jsonify({"error": "Keine Suchanfrage uebermittelt"}), 400
    return jsonify(search_locations(user_message, user_lat, user_lon))


@planner_bp.get("/planner/locations")
def planner_locations():
    return jsonify(LOCATIONS)


@planner_bp.post("/planner/nearest")
def planner_nearest():
    payload = request.get_json(silent=True) or {}
    user_lat = payload.get("lat")
    user_lon = payload.get("lon")
    if user_lat is None or user_lon is None:
        return jsonify({"error": "Koordinaten fehlen"}), 400

    closest = min(CITIES, key=lambda city: haversine(user_lat, user_lon, city["lat"], city["lon"]))
    distance = haversine(user_lat, user_lon, closest["lat"], closest["lon"])
    return jsonify(
        {
            "city": closest["name"],
            "distance": round(distance, 2),
            "city_lat": closest["lat"],
            "city_lon": closest["lon"],
            "bearing": calculate_bearing(user_lat, user_lon, closest["lat"], closest["lon"]),
            "walking_time": round(distance / 5 * 60, 0),
        }
    )


@planner_bp.post("/planner/route")
def planner_route():
    payload = request.get_json(silent=True) or {}
    try:
        response = requests.get(
            f"https://router.project-osrm.org/route/v1/foot/{payload['lon']},{payload['lat']};{payload['end_lon']},{payload['end_lat']}",
            params={"overview": "full", "geometries": "geojson"},
            timeout=10,
        ).json()
        if response.get("code") != "Ok":
            return jsonify({"error": "Keine Route gefunden"}), 400
        coordinates = response["routes"][0]["geometry"]["coordinates"]
        return jsonify(
            {
                "route": [[coord[1], coord[0]] for coord in coordinates],
                "distance": round(response["routes"][0]["distance"] / 1000, 2),
                "duration": round(response["routes"][0]["duration"] / 60, 0),
            }
        )
    except Exception:
        return jsonify({"error": "Routenberechnung fehlgeschlagen"}), 500


@planner_bp.post("/planner/decision")
def planner_decision():
    payload = request.get_json(silent=True) or {}
    situation = payload.get("situation")
    return jsonify({"steps": SURVIVAL_RULES.get(situation, ["Keine Daten vorhanden"]), "situation": situation})


@planner_bp.post("/planner/weather")
def planner_weather():
    payload = request.get_json(silent=True) or {}
    lat = payload.get("lat", DEFAULT_LAT)
    lon = payload.get("lon", DEFAULT_LON)

    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
        )
        response = requests.get(url, timeout=10).json()
        current = response.get("current", {})
        weather_codes = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "fog",
            51: "light drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            80: "rain showers",
            95: "thunderstorm",
        }
        closest = min(CITIES, key=lambda city: haversine(lat, lon, city["lat"], city["lon"]))
        return jsonify(
            {
                "temperature": current.get("temperature_2m", 0),
                "humidity": current.get("relative_humidity_2m", 0),
                "feels_like": current.get("apparent_temperature", 0),
                "wind_speed": current.get("wind_speed_10m", 0),
                "condition": weather_codes.get(current.get("weather_code", 0), "unknown"),
                "description": weather_codes.get(current.get("weather_code", 0), "unknown").title(),
                "location": closest["name"],
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

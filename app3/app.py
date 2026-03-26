import json
import math
import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Load travel locations data
with open('locations.json', 'r', encoding='utf-8') as f:
    LOCATIONS = json.load(f)

# API keys - set as environment variables if needed
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2')

# Default user location (Bregenz, Austria)
DEFAULT_LAT = 47.5031
DEFAULT_LON = 9.7471

# === ORIGINAL SURVIVAL APP DATA ===

CITIES = [
    {"name": "Bregenz", "lat": 47.5031, "lon": 9.7471},
    {"name": "Dornbirn", "lat": 47.4125, "lon": 9.7417},
    {"name": "Feldkirch", "lat": 47.2386, "lon": 9.5990},
    {"name": "Bludenz", "lat": 47.1544, "lon": 9.8222},
    {"name": "Hohenems", "lat": 47.3622, "lon": 9.6883},
    {"name": "Lustenau", "lat": 47.4267, "lon": 9.6583},
    {"name": "Hard", "lat": 47.4851, "lon": 9.6922},
    {"name": "Rankweil", "lat": 47.2711, "lon": 9.6455},
    {"name": "Götzis", "lat": 47.3341, "lon": 9.6455},
    {"name": "Lauterach", "lat": 47.4754, "lon": 9.7317},
    {"name": "Wolfurt", "lat": 47.4725, "lon": 9.7547},
    {"name": "Höchst", "lat": 47.4586, "lon": 9.6389},
]

HOSPITALS = [
    {"name": "LKH Bregenz", "lat": 47.4912, "lon": 9.7417},
    {"name": "Krankenhaus Dornbirn", "lat": 47.4101, "lon": 9.7420},
    {"name": "LKH Feldkirch", "lat": 47.2378, "lon": 9.5922},
    {"name": "Krankenhaus Bludenz", "lat": 47.1557, "lon": 9.8188},
    {"name": "Krankenhaus Hohenems", "lat": 47.3592, "lon": 9.6842},
]

SURVIVAL_RULES = {
    "lost": ["S.T.O.P.: Sit, Think, Observe, Plan.", "Stay where you are.", "Make yourself visible.", "Move downhill to find water."],
    "injured": ["Assess injury and stop bleeding.", "Keep warm and calm.", "Call emergency (112).", "Signal for help."],
    "no_water": ["Conserve energy.", "Seek shade.", "Don't eat without water.", "Look for damp soil or dew."],
    "no_food": ["Stay calm and conserve energy.", "Search for edible plants/berries.", "Check for insects and grubs.", "Set up simple snares for small game."],
    "no_reception": ["Climb to higher ground.", "Move to open areas.", "Try different locations.", "Wait and try again later."],
    "cold": ["Seek shelter.", "Insulate from ground.", "Stay dry.", "Huddle with others."]
}

# === TRAVEL PLANNER FUNCTIONS ===

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def get_locations_in_radius(lat, lon, radius_km):
    results = []
    for loc in LOCATIONS:
        dist = haversine(lat, lon, loc['latitude'], loc['longitude'])
        if dist <= radius_km:
            results.append({**loc, 'distance_km': round(dist, 2)})
    return results

# === LOCAL MATCHER (free, no API needed) ===

def local_matcher(user_input, locations):
    user_lower = user_input.lower()
    
    feature_keywords = {
        'water': ['water', 'see', 'lake', 'schwimm', 'swim', 'baden'],
        'mountain': ['berg', 'mountain', 'alps', 'gipfel'],
        'hiking': ['hiking', 'wanderung', 'wandern', 'trek', 'wander'],
        'hot_springs': ['hot spring', 'thermal', 'heiß', 'spa', 'warm'],
        'swimming': ['swim', 'schwimmen', 'pool'],
        'views': ['view', 'ausch', 'panorama', 'blick'],
        'family': ['family', 'familie', 'kinder', 'kids', 'leicht', 'einfach', 'easy', 'leichte', 'einfache'],
        'nature': ['nature', 'natur', 'wald', 'forest'],
        'relaxation': ['relax', 'entspannung', 'ruhig', 'peaceful'],
        'alpine': ['alpine', 'hoch', 'alpen'],
        'scenic': ['scenic', 'schön', 'beautiful', 'malerisch'],
        'challenging': ['schwer', 'hard', 'anspruchsvoll', 'schwierig', 'extrem', 'anspruchsvoll'],
        'multi_day': ['3 tage', '4 tage', '5 tage', 'mehrtägig', 'übernachtung', 'mehr tage', 'mehrtägig', 'mehrmal übernachtung']
    }
    
    duration_keywords = {5: ['5 tage', '5-tag', '5-day', 'fünf tage'], 4: ['4 tage', '4-tag', '4-day', 'vier tage'], 3: ['3 tage', '3-tag', '3-day', 'drei tage'], 2: ['2 tage', '2-tag', '2-day', 'zwei tage'], 1: ['1 tag', '1 tägig', 'eintägig', 'eintägig', 'tagestour', 'day trip']}
    
    # Extract features
    desired = set()
    for feat, kws in feature_keywords.items():
        if any(kw in user_lower for kw in kws):
            desired.add(feat)
    if not desired:
        desired = {'water', 'mountain', 'hiking', 'nature'}
    
    # Extract duration
    duration = None
    for dur, kws in duration_keywords.items():
        if any(kw in user_lower for kw in kws):
            duration = dur
            break
    
    results = []
    for loc in locations:
        score = 0
        reasons = []
        loc_feats = set(loc.get('features', []))
        matched = desired & loc_feats
        score += len(matched) * 2
        if matched:
            reasons.append(f"Has: {', '.join(matched)}")
        if duration and duration in loc.get('suitable_duration', []):
            score += 2
            reasons.append(f"Good for {duration} days")
        
        dist = loc.get('distance_km', 0)
        
        hiking_info = loc.get('hiking_info', {})
        hike_text = ""
        if hiking_info:
            hours = hiking_info.get('duration_hours', 0)
            if hours > 0:
                hike_text = f" • ⏱️ {hours}h hike"
            else:
                hike_text = " • ♨️ (no hike needed)"
            hike_text += f" • {hiking_info.get('difficulty', 'unknown')}"
        
        if score >= 3:
            results.append({
                'name': loc['name'], 
                'latitude': loc.get('latitude'),
                'longitude': loc.get('longitude'),
                'reason': ('. '.join(reasons) if reasons else 'Matches preferences') + hike_text, 
                'match_score': min(10, score), 
                'distance_km': dist,
                'hiking_info': hiking_info
            })
    
    results.sort(key=lambda x: x['match_score'], reverse=True)
    pref_text = ', '.join(desired) + (f', {duration}-day trip' if duration else '')
    return {'preferences_interpreted': pref_text, 'results': results[:5]}

# === OLLAMA (free local AI) ===

def call_ollama(prompt, json_mode=False):
    try:
        payload = {
            'model': OLLAMA_MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.7
        }
        if json_mode:
            payload['format'] = 'json'
        response = requests.post(f'{OLLAMA_URL}/api/chat', json=payload, timeout=120)
        if response.status_code == 200:
            content = response.json().get('message', {}).get('content', '')
            if json_mode:
                try: return json.loads(content)
                except:
                    start, end = content.find('{'), content.rfind('}')+1
                    if start >= 0: return json.loads(content[start:end])
            return content
        return None
    except: return None

# === OPENAI ===

def call_openai(prompt, json_mode=False):
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
    try:
        payload = {
            'model': 'gpt-4o-mini',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.7,
            'max_tokens': 1000
        }
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            if json_mode:
                try: return json.loads(content)
                except:
                    start, end = content.find('{'), content.rfind('}')+1
                    if start >= 0: return json.loads(content[start:end])
            return content
        return None
    except: return None

# === GEMINI ===

def call_gemini(prompt):
    if not GEMINI_API_KEY:
        return None
    try:
        url = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}'
        response = requests.post(url, json={'contents': [{'parts': [{'text': prompt}]}]}, timeout=30)
        print(f"Gemini response status: {response.status_code}")
        print(f"Gemini response: {response.text[:500]}")
        if response.status_code == 200:
            data = response.json()
            return data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        return None
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

def build_prompt(user_input, user_lat, user_lon, locations):
    return f"""User wants a trip location.

INPUT: "{user_input}"
LOCATION: {user_lat}, {user_lon}
LOCATIONS: {json.dumps(locations)}

Return JSON:
{{"preferences_interpreted": "...", "results": [{{"name": "...", "reason": "...", "match_score": 1-10, "distance_km": n}}]}}
Only include match_score >= 5."""

def call_ai_for_matching(user_input, user_lat, user_lon, locations_in_radius):
    if not locations_in_radius:
        return {'results': [], 'error': 'No locations found'}
    
    # Always use local matcher first (more reliable)
    result = local_matcher(user_input, locations_in_radius)
    
    # Only use AI if local matcher returns no results
    if not result.get('results') and (OLLAMA_URL or OPENAI_API_KEY):
        prompt = build_prompt(user_input, user_lat, user_lon, locations_in_radius)
        if OLLAMA_URL:
            ai_result = call_ollama(prompt, json_mode=True)
            if ai_result and ai_result.get('results'):
                return ai_result
        elif OPENAI_API_KEY:
            ai_result = call_openai(prompt, json_mode=True)
            if ai_result and ai_result.get('results'):
                return ai_result

    return result

def search_with_expanding_radius(user_input, user_lat, user_lon):
    # Search all locations without radius limit
    result = call_ai_for_matching(user_input, user_lat, user_lon, LOCATIONS)
    return {'radius_used': 'All', 'user_location': {'lat': user_lat, 'lon': user_lon}, 'locations_found': len(LOCATIONS), **result}

def calculate_bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    x, y = math.sin(math.radians(lon2-lon1))*math.cos(phi2), math.cos(phi1)*math.sin(phi2)-math.sin(phi1)*math.cos(phi2)*math.cos(math.radians(lon2-lon1))
    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    return f"{['N','NE','E','SE','S','SW','W','NW'][round(bearing/45)%8]} ({int(bearing)}°)"

# === ROUTES ===

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get('message', '')
    user_lat = data.get('lat', DEFAULT_LAT)
    user_lon = data.get('lon', DEFAULT_LON)
    general = data.get('general', False)
    
    if not user_message:
        return jsonify({'error': 'No message'}), 400
    
    if general:
        prompt = f"""Du bist ein Wander-Experte. Beantworte die folgende Frage auf Deutsch:

Frage: {user_message}

Antworte kurz und hilfreich."""
        
        if GEMINI_API_KEY:
            response = call_gemini(prompt)
        elif OLLAMA_URL:
            response = call_ollama(prompt)
        elif OPENAI_API_KEY:
            response = call_openai(prompt)
        else:
            response = "Entschuldigung, kein KI-Dienst verfügbar. Bitte GEMINI_API_KEY, OLLAMA_URL oder OPENAI_API_KEY setzen."
        
        return jsonify({'response': response})
    
    return jsonify(search_with_expanding_radius(user_message, user_lat, user_lon))

@app.route("/locations")
def get_all_locations():
    return jsonify(LOCATIONS)

@app.route("/nearest", methods=["POST"])
def nearest():
    u_lat, u_lon = request.json.get('lat'), request.json.get('lon')
    if u_lat is None: return jsonify({'error': 'Missing coords'}), 400
    closest = min(CITIES, key=lambda c: haversine(u_lat, u_lon, c['lat'], c['lon']))
    return jsonify({'city': closest['name'], 'distance': round(haversine(u_lat, u_lon, closest['lat'], closest['lon']), 2), 'city_lat': closest['lat'], 'city_lon': closest['lon'], 'bearing': calculate_bearing(u_lat, u_lon, closest['lat'], closest['lon']), 'walking_time': round(haversine(u_lat, u_lon, closest['lat'], closest['lon'])/5*60, 0)})

@app.route("/nearest_hospital", methods=["POST"])
def nearest_hospital():
    u_lat, u_lon = request.json.get('lat'), request.json.get('lon')
    if u_lat is None: return jsonify({'error': 'Missing coords'}), 400
    closest = min(HOSPITALS, key=lambda h: haversine(u_lat, u_lon, h['lat'], h['lon']))
    return jsonify({'name': closest['name'], 'lat': closest['lat'], 'lon': closest['lon'], 'distance': round(haversine(u_lat, u_lon, closest['lat'], closest['lon']), 2)})

@app.route("/route", methods=["POST"])
def get_route():
    data = request.json
    try:
        route = requests.get(f"https://router.project-osrm.org/route/v1/foot/{data['lon']},{data['lat']};{data['end_lon']},{data['end_lat']}", params={'overview': 'full', 'geometries': 'geojson'}, timeout=10).json()
        if route['code'] != 'Ok': return jsonify({'error': 'No route'}), 400
        geom = route['routes'][0]['geometry']['coordinates']
        return jsonify({'route': [[c[1], c[0]] for c in geom], 'distance': round(route['routes'][0]['distance']/1000, 2), 'duration': round(route['routes'][0]['duration']/60, 0)})
    except: return jsonify({'error': 'Route failed'}), 500

@app.route("/decision", methods=["POST"])
def decision():
    return jsonify({'steps': SURVIVAL_RULES.get(request.json.get('situation'), ['No data']), 'situation': request.json.get('situation')})

@app.route("/weather", methods=["POST"])
def weather():
    data = request.json
    lat = data.get('lat', DEFAULT_LAT)
    lon = data.get('lon', DEFAULT_LON)
    
    try:
        # Use Open-Meteo (free, no API key)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
        resp = requests.get(url, timeout=10).json()
        
        current = resp.get('current', {})
        code = current.get('weather_code', 0)
        
        weather_codes = {
            0: 'clear sky', 1: 'mainly clear', 2: 'partly cloudy', 3: 'overcast',
            45: 'fog', 48: 'depositing rime fog', 51: 'light drizzle', 53: 'moderate drizzle',
            55: 'dense drizzle', 61: 'slight rain', 63: 'moderate rain', 65: 'heavy rain',
            71: 'slight snow', 73: 'moderate snow', 75: 'heavy snow', 80: 'rain showers',
            95: 'thunderstorm', 96: 'thunderstorm with hail'
        }
        
        condition = weather_codes.get(code, 'unknown')
        
        # Find nearest city for location name
        closest = min(CITIES, key=lambda c: haversine(lat, lon, c['lat'], c['lon']))
        
        return jsonify({
            'temperature': current.get('temperature_2m', 0),
            'humidity': current.get('relative_humidity_2m', 0),
            'feels_like': current.get('apparent_temperature', 0),
            'wind_speed': current.get('wind_speed_10m', 0),
            'condition': condition,
            'description': condition.replace('_', ' ').title(),
            'location': closest['name']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)
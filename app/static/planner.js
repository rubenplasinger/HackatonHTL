let userLat = 47.5031;
let userLon = 9.7471;
let map;
let userMarker;
let routeLayer;
let selectedDest = null;

function byId(id) {
    return document.getElementById(id);
}

function setSelectedDetails(html) {
    byId("selected-details").innerHTML = html;
}

function renderResults(results) {
    const container = byId("travel-results");
    container.innerHTML = "";
    if (!results.length) {
        container.innerHTML = '<div class="planner-detail-card">Keine passenden Orte gefunden.</div>';
        return;
    }

    results.forEach((result, index) => {
        const card = document.createElement("div");
        card.className = "location-card";
        card.innerHTML = `
            <strong>#${index + 1} ${result.name}</strong>
            <p>${result.reason}</p>
            <div class="location-meta">
                <span>${result.match_score}/10 Match</span>
                <span>${result.distance_km} km entfernt</span>
                <span>${result.hiking_info?.duration_hours || 0} h Wanderzeit</span>
            </div>
            <button class="planner-button" type="button">Auswaehlen</button>
        `;
        card.querySelector("button").addEventListener("click", () => selectLocation(result));
        container.appendChild(card);
    });
}

async function searchTrips() {
    const message = byId("travel-message").value.trim();
    if (!message) {
        return;
    }

    byId("travel-loading").classList.remove("hidden");
    byId("travel-results").innerHTML = "";
    try {
        const response = await fetch("/planner/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, lat: userLat, lon: userLon }),
        });
        const data = await response.json();
        byId("travel-loading").classList.add("hidden");

        if (data.error) {
            renderResults([]);
            return;
        }

        byId("travel-radius").textContent = `${data.radius_used} · ${data.locations_found} Orte`;
        byId("travel-radius").classList.remove("hidden");
        byId("travel-preferences").textContent = data.preferences_interpreted;
        byId("travel-preferences").classList.remove("hidden");
        renderResults(data.results || []);
    } catch (_error) {
        byId("travel-loading").classList.add("hidden");
        renderResults([]);
    }
}

function selectLocation(result) {
    selectedDest = result;
    setSelectedDetails(`
        <strong>${result.name}</strong>
        <p>${result.reason}</p>
        <p>Entfernung: ${result.distance_km} km</p>
        <p>Wanderung: ${result.hiking_info?.duration_hours || 0} Stunden · ${result.hiking_info?.difficulty || "unbekannt"}</p>
    `);
    if (map) {
        showRoute(result.latitude, result.longitude);
    }
}

async function updateWeather() {
    const response = await fetch("/planner/weather", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat: userLat, lon: userLon }),
    });
    const data = await response.json();
    if (data.error) {
        byId("weather-desc").textContent = data.error;
        return;
    }
    byId("temp-value").textContent = Math.round(data.temperature);
    byId("weather-desc").textContent = data.description;
    byId("weather-location").textContent = data.location;
    byId("humidity").textContent = `${data.humidity}%`;
    byId("wind").textContent = `${data.wind_speed} km/h`;
    byId("feels-like").textContent = `${Math.round(data.feels_like)}°C`;
}

async function loadNearestCity() {
    const response = await fetch("/planner/nearest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat: userLat, lon: userLon }),
    });
    const data = await response.json();
    byId("city-name").textContent = data.city;
    byId("city-dist").textContent = data.distance;
    byId("city-walking").textContent = data.walking_time;
    byId("route-info").classList.remove("hidden");
}

async function showRoute(endLat, endLon) {
    if (!map) {
        return;
    }
    const response = await fetch("/planner/route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat: userLat, lon: userLon, end_lat: endLat, end_lon: endLon }),
    });
    const data = await response.json();
    if (!data.route) {
        return;
    }

    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    routeLayer = L.polyline(data.route, { color: "#f3c57d", weight: 5 }).addTo(map);
    map.fitBounds(routeLayer.getBounds(), { padding: [20, 20] });
}

function initMap() {
    map = L.map("map").setView([userLat, userLon], 11);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "" }).addTo(map);
    userMarker = L.marker([userLat, userLon]).addTo(map);
}

async function showDecision(situation) {
    const response = await fetch("/planner/decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ situation }),
    });
    const data = await response.json();
    byId("survival-result").innerHTML = `<strong>${situation}</strong><br>${data.steps.map((step, idx) => `${idx + 1}. ${step}`).join("<br>")}`;
}

function locateUser() {
    if (!navigator.geolocation) {
        return;
    }
    navigator.geolocation.getCurrentPosition(async (position) => {
        userLat = position.coords.latitude;
        userLon = position.coords.longitude;
        if (map) {
            map.setView([userLat, userLon], 12);
            userMarker.setLatLng([userLat, userLon]);
        }
        await loadNearestCity();
        await updateWeather();
        if (selectedDest) {
            await showRoute(selectedDest.latitude, selectedDest.longitude);
        }
    });
}

byId("travel-btn").addEventListener("click", searchTrips);
byId("refresh-weather-btn").addEventListener("click", updateWeather);
byId("find-pos-btn").addEventListener("click", locateUser);
byId("open-maps-btn").addEventListener("click", () => {
    if (selectedDest) {
        window.open(`https://www.google.com/maps/dir/?api=1&destination=${selectedDest.latitude},${selectedDest.longitude}`, "_blank");
    }
});

document.querySelectorAll(".emergency-btn").forEach((button) => {
    button.addEventListener("click", () => showDecision(button.dataset.situation));
});

initMap();
loadNearestCity();
updateWeather();

const responseOutput = document.getElementById("response-output");
const provisionTableBody = document.getElementById("provision-table-body");
const provisionCount = document.getElementById("provision-count");
const lastAction = document.getElementById("last-action");

let lastCalculationItems = null;

function setLastAction(text) {
    lastAction.textContent = text;
}

function showResponse(data) {
    responseOutput.textContent = JSON.stringify(data, null, 2);
}

function showError(error) {
    const payload = typeof error === "string" ? { error } : error;
    showResponse(payload);
}

async function apiRequest(url, method = "GET", payload = null) {
    const options = {
        method,
        headers: {
            "Content-Type": "application/json",
        },
    };

    if (payload !== null) {
        options.body = JSON.stringify(payload);
    }

    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
        throw data;
    }

    return data;
}

function updateProvisionTable(items) {
    provisionCount.textContent = items.length;

    if (!items.length) {
        provisionTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">Noch keine Proviantdaten gespeichert.</td>
            </tr>
        `;
        return;
    }

    provisionTableBody.innerHTML = items
        .map(
            (item) => `
                <tr>
                    <td>${item.id}</td>
                    <td>${item.name}</td>
                    <td>${item.quantity}</td>
                    <td>${item.unit}</td>
                </tr>
            `
        )
        .join("");
}

async function refreshProvisions() {
    try {
        const data = await apiRequest("/provisions");
        updateProvisionTable(data.items);
        setLastAction("Proviantbestand geladen");
        return data;
    } catch (error) {
        showError(error);
        setLastAction("Laden fehlgeschlagen");
        throw error;
    }
}

function formToPayload(form) {
    const formData = new FormData(form);
    const payload = {};

    for (const [key, value] of formData.entries()) {
        if (value === "") {
            continue;
        }

        if (["quantity", "duration_days", "days", "id"].includes(key)) {
            payload[key] = Number(value);
        } else {
            payload[key] = value;
        }
    }

    return payload;
}

document.getElementById("refresh-provisions").addEventListener("click", async () => {
    await refreshProvisions();
});

document.getElementById("clear-response").addEventListener("click", () => {
    responseOutput.textContent = "Fuehre eine Aktion aus, um die JSON-Antwort hier zu sehen.";
    setLastAction("Antwort geleert");
});

document.getElementById("create-provision-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formToPayload(form);

    try {
        const data = await apiRequest("/provisions", "POST", payload);
        showResponse(data);
        setLastAction(`Proviant #${data.id} angelegt`);
        form.reset();
        await refreshProvisions();
    } catch (error) {
        showError(error);
        setLastAction("Anlegen fehlgeschlagen");
    }
});

document.getElementById("update-provision-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formToPayload(form);
    const id = payload.id;
    delete payload.id;

    try {
        const data = await apiRequest(`/provisions/${id}`, "PUT", payload);
        showResponse(data);
        setLastAction(`Proviant #${id} aktualisiert`);
        await refreshProvisions();
    } catch (error) {
        showError(error);
        setLastAction("Aktualisierung fehlgeschlagen");
    }
});

document.getElementById("consume-provision-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formToPayload(form);
    const id = payload.id;
    delete payload.id;

    try {
        const data = await apiRequest(`/provisions/${id}/consume`, "POST", payload);
        showResponse(data);
        setLastAction(`Verbrauch fuer #${id} gebucht`);
        form.reset();
        await refreshProvisions();
    } catch (error) {
        showError(error);
        setLastAction("Verbrauch fehlgeschlagen");
    }
});

document.getElementById("delete-provision-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formToPayload(form);

    try {
        const data = await apiRequest(`/provisions/${payload.id}`, "DELETE");
        showResponse(data);
        setLastAction(`Proviant #${payload.id} geloescht`);
        form.reset();
        await refreshProvisions();
    } catch (error) {
        showError(error);
        setLastAction("Loeschen fehlgeschlagen");
    }
});

document.getElementById("hiking-calculator-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formToPayload(form);

    try {
        const data = await apiRequest("/calculate/hiking", "POST", payload);
        lastCalculationItems = data.suggested_items;
        showResponse(data);
        setLastAction("Wanderbedarf berechnet");
    } catch (error) {
        showError(error);
        setLastAction("Wanderrechner fehlgeschlagen");
    }
});

document.getElementById("rationing-calculator-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formToPayload(form);

    try {
        const data = await apiRequest("/calculate/rationing", "POST", payload);
        showResponse(data);
        setLastAction("Rationen berechnet");
    } catch (error) {
        showError(error);
        setLastAction("Rationierung fehlgeschlagen");
    }
});

document.getElementById("custom-import-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const rawItems = new FormData(form).get("items");

    try {
        const items = JSON.parse(rawItems);
        const data = await apiRequest("/provisions/from-calculation", "POST", { items });
        showResponse(data);
        setLastAction("Eigene Artikel importiert");
        await refreshProvisions();
    } catch (error) {
        showError(error.error ? error : { error: "Das Artikel-JSON ist ungueltig" });
        setLastAction("Import fehlgeschlagen");
    }
});

document.getElementById("import-last-calculation").addEventListener("click", async () => {
    if (!lastCalculationItems) {
        showError({ error: "Fuehre zuerst den Wanderrechner aus, bevor du die Vorschlaege importierst." });
        setLastAction("Keine Berechnung zum Importieren");
        return;
    }

    try {
        const data = await apiRequest("/provisions/from-calculation", "POST", {
            items: lastCalculationItems,
        });
        showResponse(data);
        setLastAction("Letzte Wanderberechnung importiert");
        await refreshProvisions();
    } catch (error) {
        showError(error);
        setLastAction("Import aus Berechnung fehlgeschlagen");
    }
});

refreshProvisions().catch(() => {
    showError({ error: "Der erste Ladevorgang des Proviantbestands ist fehlgeschlagen." });
});

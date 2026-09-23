const API = "/api";

async function laeOlek() {
    const el = document.getElementById("health");
    try {
        const r = await fetch(`${API}/health`);
        const data = await r.json();
        el.textContent = `API: ${data.status} · andmebaas: ${data.database ? "ühendatud" : "ühenduseta"}`;
        el.classList.toggle("muted", false);
    } catch (err) {
        el.textContent = "API ei vasta.";
    }
}

async function laeInimesed() {
    const list = document.getElementById("inimesed");
    try {
        const r = await fetch(`${API}/inimesed`);
        const inimesed = await r.json();
        list.innerHTML = "";
        for (const i of inimesed) {
            const li = document.createElement("li");
            li.textContent = `${i.eesnimi} ${i.perenimi}`;
            list.appendChild(li);
        }
        if (!inimesed.length) {
            list.innerHTML = '<li class="muted">Hääletajaid ei leitud.</li>';
        }
    } catch (err) {
        list.innerHTML = '<li class="muted">Hääletajate laadimine ebaõnnestus.</li>';
    }
}

laeOlek();
laeInimesed();

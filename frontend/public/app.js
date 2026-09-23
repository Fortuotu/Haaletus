const API = "/api";
const el = (id) => document.getElementById(id);

let olek = null;

async function api(tee, valikud) {
    const vastus = await fetch(API + tee, {
        headers: { "Content-Type": "application/json" },
        ...valikud,
    });
    const sisu = await vastus.json();
    if (!vastus.ok) {
        throw new Error(sisu.detail || "Viga " + vastus.status);
    }
    return sisu;
}

function loenda(sekundid) {
    const m = Math.floor(sekundid / 60);
    const s = sekundid % 60;
    return m + ":" + String(s).padStart(2, "0");
}

function jaanudSekundid() {
    if (!olek || !olek.lopp_aeg) return 0;
    return Math.max(0, Math.round((new Date(olek.lopp_aeg) - new Date()) / 1000));
}

function naitaTaimer() {
    if (!olek || !olek.tulemus_id) {
        el("taimer").textContent = "--:--";
        return;
    }
    el("taimer").textContent = loenda(olek.aktiivne ? jaanudSekundid() : 0);
    if (olek.aktiivne && jaanudSekundid() === 0) {
        uuenda();
    }
}

async function laeInimesed() {
    const inimesed = await api("/inimesed");
    const valik = el("inimene");
    valik.textContent = "";
    for (const i of inimesed) {
        const option = document.createElement("option");
        option.value = i.id;
        option.textContent = i.eesnimi + " " + i.perenimi;
        valik.appendChild(option);
    }
}

async function laeOlek() {
    olek = await api("/haaletus/olek");
    el("alusta").disabled = Boolean(olek.aktiivne);
    naitaTaimer();
}

async function laeMinuHaal() {
    const id = el("inimene").value;
    if (!id) return;
    const minu = await api("/haaletus/minu/" + id);
    for (const nupp of [el("poolt"), el("vastu")]) {
        nupp.disabled = !minu.saab_muuta;
        nupp.classList.toggle("valitud", minu.otsus === nupp.dataset.otsus);
    }
}

async function uuenda() {
    try {
        await laeOlek();
        await laeMinuHaal();
    } catch (viga) {
        console.error(viga);
    }
}

async function haaleta(otsus) {
    try {
        await api("/haaletus/haal", {
            method: "POST",
            body: JSON.stringify({ inimene_id: Number(el("inimene").value), otsus }),
        });
    } catch (viga) {
        console.error(viga);
    }
    await uuenda();
}

async function alusta() {
    try {
        await api("/haaletus/alusta", { method: "POST" });
    } catch (viga) {
        console.error(viga);
    }
    await uuenda();
}

el("alusta").addEventListener("click", alusta);
el("inimene").addEventListener("change", laeMinuHaal);
el("poolt").addEventListener("click", () => haaleta("poolt"));
el("vastu").addEventListener("click", () => haaleta("vastu"));

setInterval(naitaTaimer, 1000);
setInterval(uuenda, 3000);

(async () => {
    try {
        await laeInimesed();
    } catch (viga) {
        console.error(viga);
    }
    await uuenda();
})();

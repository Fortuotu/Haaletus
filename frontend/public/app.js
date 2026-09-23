const API = "/api";

const el = (id) => document.getElementById(id);
const nupud = () => [el("poolt"), el("vastu")];

let olek = null;
let inimesed = [];

async function api(tee, valikud = {}) {
    const vastus = await fetch(`${API}${tee}`, {
        headers: { "Content-Type": "application/json" },
        ...valikud,
    });
    const sisu = vastus.status === 204 ? null : await vastus.json();
    if (!vastus.ok) {
        throw new Error(sisu?.detail ?? `Viga ${vastus.status}`);
    }
    return sisu;
}

function kellaaeg(iso) {
    return new Date(iso).toLocaleTimeString("et-EE");
}

function loenda(sekundid) {
    const m = Math.floor(sekundid / 60);
    const s = sekundid % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
}

async function laeInimesed() {
    inimesed = await api("/inimesed");
    el("inimene").innerHTML = inimesed
        .map((i) => `<option value="${i.id}">${i.eesnimi} ${i.perenimi}</option>`)
        .join("");
}

async function laeOlek() {
    olek = await api("/haaletus/olek");

    const silt = el("olek-silt");
    if (!olek.tulemus_id) {
        silt.textContent = "alustamata";
        silt.className = "silt";
        el("alguse-aeg").textContent = "Haaletust ei ole alustatud.";
        el("taimer").textContent = "--:--";
    } else if (olek.aktiivne) {
        silt.textContent = "haaletus kaib";
        silt.className = "silt silt-aktiivne";
        el("alguse-aeg").textContent = `Algas ${kellaaeg(olek.h_alguse_aeg)}, lopeb ${kellaaeg(olek.lopp_aeg)}.`;
    } else {
        silt.textContent = "loppenud";
        silt.className = "silt silt-loppenud";
        el("alguse-aeg").textContent = `Loppes ${kellaaeg(olek.lopp_aeg)}. Tulemused on loplikud.`;
        el("taimer").textContent = "0:00";
    }

    el("alusta").disabled = Boolean(olek.aktiivne);
    el("poolt-arv").textContent = olek.poolt_haali;
    el("vastu-arv").textContent = olek.vastu_haali;
    el("haaletanud").textContent = `${olek.haaletanute_arv} / ${olek.inimeste_arv}`;
    el("tulemus-markus").textContent = olek.aktiivne
        ? "Hetkeseis - haaletus kaib veel."
        : olek.tulemus_id
          ? "Loplik tulemus."
          : "";

    uuendaTaimer();
}

function uuendaTaimer() {
    if (!olek?.aktiivne) return;
    const jaanud = Math.max(0, Math.round((new Date(olek.lopp_aeg) - new Date()) / 1000));
    el("taimer").textContent = loenda(jaanud);
    if (jaanud === 0) {
        olek.aktiivne = false;
        laeOlek();
        laeMinuHaal();
    }
}

async function laeMinuHaal() {
    const id = el("inimene").value;
    if (!id) return;
    const minu = await api(`/haaletus/minu/${id}`);
    const tekst = minu.otsus
        ? `Viimane otsus: ${minu.otsus.toUpperCase()} (${kellaaeg(minu.haaletuse_aeg)})`
        : "Sa ei ole veel haaletanud.";
    el("minu-haal").textContent = minu.saab_muuta
        ? `${tekst} - saad seda veel muuta.`
        : `${tekst}${minu.otsus ? " - haaletus on loppenud, otsus on loplik." : ""}`;

    for (const nupp of nupud()) {
        nupp.disabled = !minu.saab_muuta;
        nupp.classList.toggle("valitud", minu.otsus === nupp.dataset.otsus);
    }
}

async function laeLogi() {
    const read = await api("/logi?limiit=25");
    const keha = el("logi");
    if (!read.length) {
        keha.innerHTML = '<tr><td colspan="4" class="muted">Kandeid ei ole.</td></tr>';
        return;
    }
    keha.innerHTML = read
        .map((r) => {
            const nimi = r.eesnimi ? `${r.eesnimi} ${r.perenimi}` : "-";
            const muutus = r.vana_otsus
                ? `${r.vana_otsus} -> ${r.uus_otsus}`
                : (r.uus_otsus ?? r.markus ?? "-");
            return `<tr><td>${kellaaeg(r.aeg)}</td><td>${r.tegevus}</td><td>${nimi}</td><td>${muutus}</td></tr>`;
        })
        .join("");
}

async function haaleta(otsus) {
    try {
        await api("/haaletus/haal", {
            method: "POST",
            body: JSON.stringify({ inimene_id: Number(el("inimene").value), otsus }),
        });
    } catch (err) {
        el("minu-haal").textContent = err.message;
    }
    await Promise.all([laeOlek(), laeMinuHaal(), laeLogi()]);
}

async function alusta() {
    try {
        await api("/haaletus/alusta", { method: "POST" });
    } catch (err) {
        el("alguse-aeg").textContent = err.message;
    }
    await Promise.all([laeOlek(), laeMinuHaal(), laeLogi()]);
}

el("alusta").addEventListener("click", alusta);
el("inimene").addEventListener("change", laeMinuHaal);
for (const nupp of nupud()) {
    nupp.addEventListener("click", () => haaleta(nupp.dataset.otsus));
}

setInterval(uuendaTaimer, 1000);
setInterval(() => {
    laeOlek();
    laeMinuHaal();
    laeLogi();
}, 3000);

(async () => {
    await laeInimesed();
    await Promise.all([laeOlek(), laeMinuHaal(), laeLogi()]);
})();

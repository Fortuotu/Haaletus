# Haaletussusteem - baasseadistus

I osa: andmebaas (MariaDB + phpMyAdmin), FastAPI backend ja staatiline frontend, koik Dockeris.
Andmebaasi skeem on loodud, 11 haaletajat on seemendatud ja haaletamise loogika on teostatud.

## Ulesehitus

```
db/init/        andmebaasi skeem (01) ja seemendus (02) - kaivituvad esmakaivitusel
backend/        FastAPI rakendus (app/), Dockerfile, requirements.txt, .venv
frontend/       staatiline leht (public/), nginx konfiga, mis proxib /api/ backendi
docker-compose.yml
```

## Tabelid

| Tabel | Sisu |
|---|---|
| `INIMESED` | 11 eelnevalt kantud haaletajat (eesnimi, perenimi) |
| `TULEMUSED` | haaletusvoor: `h_alguse_aeg`, haaletanute arv, poolt- ja vastuhaalte arv |
| `HAALETUS` | haaletaja kehtiv otsus: nimi, `haaletuse_aeg`, `otsus` (poolt/vastu) |
| `LOGI` | koik muutused kellaajaliselt (`aeg`, tegevus, vana ja uus otsus) |

## Kaivitamine

```bash
cp .env.example .env     # vajadusel muuda porte/paroole
docker compose up -d --build
```

| Teenus | Aadress |
|---|---|
| Frontend | http://localhost:8080 |
| API dokumentatsioon | http://localhost:8000/docs |
| phpMyAdmin | http://localhost:8081 (kasutaja `haaletus`, parool `haaletus`) |
| MariaDB | localhost:3306 |

Andmebaasi skript `db/init/` kaivitub ainult siis, kui andmemaht on tuhi.
Skeemi muutmisel tuleb maht lahtestada: `docker compose down -v && docker compose up -d --build`.

## Backend lokaalselt (ilma Dockerita)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DB_HOST=127.0.0.1 uvicorn app.main:app --reload
```

## Haaletamise reeglid

* Uks voor kestab **5 minutit** (`VOTE_DURATION_SECONDS` failis `.env`) ja algab koigile samal hetkel -
  voor on uks rida tabelis `TULEMUSED`, mille `h_alguse_aeg` kehtib koigile haaletajatele.
* Haaletaja saab olla `poolt` voi `vastu` ja voib vooru ajal otsust vabalt muuta;
  tabelis `HAALETUS` on tema kehtiv otsus (uks rida vooru ja inimese kohta).
* Iga muutus kirjutatakse millisekundi tapsusega tabelisse `LOGI`:
  `HAALETUS_ALGAS`, `HAAL_ANTUD`, `HAAL_MUUDETUD`, `HAAL_KORDUS`, `HAALETUS_LOPPES`, `HAAL_HILINES`.
* Peale 5 minuti moodumist tagastab API haale andmisel `403` ja tulemused on loplikud.
  Hilinenud katse ei muuda tulemust, aga jaab logisse kandena `HAAL_HILINES`.
* Haaletaja naeb oma viimast otsust ka peale vooru loppu (`saab_muuta: false`).

Vooru lopp tuletatakse ajast (`h_alguse_aeg + kestus`), mitte taustaprotsessist - seega ei soltu
tulemuste lukustumine sellest, kas keegi parajasti API-t kasutab. Paralleelsed haaled
serialiseeritakse `SELECT ... FOR UPDATE`-ga vooru real, nii et loendurid ei jookse paigast ara.

## Endpointid

| Meetod | Tee | Kirjeldus |
|---|---|---|
| GET | `/api/health` | teenuse ja andmebaasiuhenduse olek |
| GET | `/api/inimesed` | koik haaletajad |
| GET | `/api/inimesed/{id}` | uks haaletaja |
| POST | `/api/haaletus/alusta` | alusta uus voor (`409`, kui voor juba kaib) |
| GET | `/api/haaletus/olek` | vooru seis: algus, lopp, jarelejaanud sekundid, hetketulemus |
| POST | `/api/haaletus/haal` | anna voi muuda haalt (`{"inimene_id": 1, "otsus": "poolt"}`) |
| GET | `/api/haaletus/minu/{id}` | haaletaja viimane otsus, ka peale vooru loppu |
| GET | `/api/tulemused` | koik voorud |
| GET | `/api/tulemused/{id}` | uhe vooru tulemus |
| GET | `/api/tulemused/{id}/haaled` | nimelised haaled (alles peale vooru loppu) |
| GET | `/api/logi?tulemus_id=&limiit=` | logikanded kellaajaliselt, uuemad ees |

Ajad on API-s UTC-s (`...Z`); frontend kuvab need kohalikus ajas.

### Naide

```bash
curl -X POST localhost:8000/api/haaletus/alusta
curl -X POST localhost:8000/api/haaletus/haal \
     -H 'Content-Type: application/json' \
     -d '{"inimene_id": 1, "otsus": "poolt"}'
curl localhost:8000/api/haaletus/olek
```

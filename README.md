# Hääletussüsteem — baasseadistus

I osa: andmebaas (MariaDB + phpMyAdmin), FastAPI backend ja staatiline frontend, kõik Dockeris.
Hetkel on tegemist boilerplate'iga: andmebaasi skeem on loodud ja 11 hääletajat on seemendatud,
hääletamise loogikat veel ei ole.

## Ülesehitus

```
db/init/        andmebaasi skeem (01) ja seemendus (02) — käivituvad esmakäivitusel
backend/        FastAPI rakendus (app/), Dockerfile, requirements.txt, .venv
frontend/       staatiline leht (public/), nginx konfiga, mis proxib /api/ backendi
docker-compose.yml
```

## Tabelid

| Tabel | Sisu |
|---|---|
| `INIMESED` | 11 eelnevalt kantud hääletajat (eesnimi, perenimi) |
| `TULEMUSED` | hääletusvoor: `h_alguse_aeg`, hääletanute arv, poolt- ja vastuhäälte arv |
| `HAALETUS` | hääletaja kehtiv otsus: nimi, `haaletuse_aeg`, `otsus` (poolt/vastu) |
| `LOGI` | kõik muutused kellaajaliselt (`aeg`, tegevus, vana ja uus otsus) |

## Käivitamine

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

Andmebaasi skript `db/init/` käivitub ainult siis, kui andmemaht on tühi.
Skeemi muutmisel tuleb maht lähtestada: `docker compose down -v && docker compose up -d --build`.

## Backend lokaalselt (ilma Dockerita)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DB_HOST=127.0.0.1 uvicorn app.main:app --reload
```

## Olemasolevad endpointid

| Meetod | Tee | Kirjeldus |
|---|---|---|
| GET | `/api/health` | teenuse ja andmebaasiühenduse olek |
| GET | `/api/inimesed` | kõik hääletajad |
| GET | `/api/inimesed/{id}` | üks hääletaja |

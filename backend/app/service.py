from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.aeg import nyyd, nyyd_ms
from app.config import get_settings
from app.models import Haaletus, Inimene, Logi, Tulemus


class HaaletusViga(Exception):
    def __init__(self, sonum: str, kood: int = 409) -> None:
        super().__init__(sonum)
        self.sonum = sonum
        self.kood = kood


def kestus() -> timedelta:
    return timedelta(seconds=get_settings().vote_duration_seconds)


def lopp_aeg(tulemus: Tulemus) -> datetime:
    return tulemus.h_alguse_aeg + kestus()


def on_aktiivne(tulemus: Tulemus, hetk: datetime | None = None) -> bool:
    hetk = hetk or nyyd()
    return tulemus.h_alguse_aeg <= hetk < lopp_aeg(tulemus)


def logi(
    db: Session,
    tegevus: str,
    *,
    tulemus: Tulemus | None = None,
    inimene: Inimene | None = None,
    vana_otsus: str | None = None,
    uus_otsus: str | None = None,
    markus: str | None = None,
) -> None:
    db.add(
        Logi(
            aeg=nyyd_ms(),
            tulemus_id=tulemus.id if tulemus else None,
            inimene_id=inimene.id if inimene else None,
            eesnimi=inimene.eesnimi if inimene else None,
            perenimi=inimene.perenimi if inimene else None,
            tegevus=tegevus,
            vana_otsus=vana_otsus,
            uus_otsus=uus_otsus,
            markus=markus,
        )
    )


def viimane_voor(db: Session, *, lukusta: bool = False) -> Tulemus | None:
    paring = select(Tulemus).order_by(Tulemus.h_alguse_aeg.desc(), Tulemus.id.desc()).limit(1)
    if lukusta:
        paring = paring.with_for_update()
    return db.scalars(paring).first()


def sulge_loppenud_voor(db: Session, tulemus: Tulemus | None) -> None:
    if tulemus is None or on_aktiivne(tulemus):
        return
    juba_suletud = db.scalar(
        select(func.count())
        .select_from(Logi)
        .where(Logi.tulemus_id == tulemus.id, Logi.tegevus == "HAALETUS_LOPPES")
    )
    if juba_suletud:
        return
    db.add(
        Logi(
            aeg=lopp_aeg(tulemus),
            tulemus_id=tulemus.id,
            tegevus="HAALETUS_LOPPES",
            markus=(
                f"Loplik tulemus: poolt {tulemus.poolt_haali}, "
                f"vastu {tulemus.vastu_haali}, haaletanuid {tulemus.haaletanute_arv}"
            ),
        )
    )
    db.commit()


def alusta_voor(db: Session) -> Tulemus:
    kaib = viimane_voor(db)
    if kaib is not None and on_aktiivne(kaib):
        raise HaaletusViga("Haaletus juba kaib")
    sulge_loppenud_voor(db, kaib)

    tulemus = Tulemus(h_alguse_aeg=nyyd(), haaletanute_arv=0, poolt_haali=0, vastu_haali=0)
    db.add(tulemus)
    db.flush()
    logi(
        db,
        "HAALETUS_ALGAS",
        tulemus=tulemus,
        markus=f"Kestus {get_settings().vote_duration_seconds} sekundit",
    )
    db.commit()
    db.refresh(tulemus)
    return tulemus


def _arvuta_tulemus(db: Session, tulemus: Tulemus) -> None:
    db.flush()
    read = db.execute(
        select(Haaletus.otsus, func.count())
        .where(Haaletus.tulemus_id == tulemus.id)
        .group_by(Haaletus.otsus)
    ).all()
    loendur = {otsus: arv for otsus, arv in read}
    tulemus.poolt_haali = loendur.get("poolt", 0)
    tulemus.vastu_haali = loendur.get("vastu", 0)
    tulemus.haaletanute_arv = tulemus.poolt_haali + tulemus.vastu_haali


def anna_haal(db: Session, inimene_id: int, otsus: str) -> Haaletus:
    inimene = db.get(Inimene, inimene_id)
    if inimene is None:
        raise HaaletusViga("Haaletajat ei leitud", kood=404)

    tulemus = viimane_voor(db)
    if tulemus is None:
        raise HaaletusViga("Haaletust ei ole alustatud")

    if not on_aktiivne(tulemus):
        logi(
            db,
            "HAAL_HILINES",
            tulemus=tulemus,
            inimene=inimene,
            uus_otsus=otsus,
            markus="Haaletus oli loppenud, otsust ei arvestatud",
        )
        sulge_loppenud_voor(db, tulemus)
        db.commit()
        raise HaaletusViga("Haaletus on loppenud, otsust ei saa enam muuta", kood=403)

    tulemus = db.scalars(
        select(Tulemus).where(Tulemus.id == tulemus.id).with_for_update()
    ).one()
    if not on_aktiivne(tulemus):
        raise HaaletusViga("Haaletus on loppenud, otsust ei saa enam muuta", kood=403)

    haal = db.scalars(
        select(Haaletus)
        .where(Haaletus.tulemus_id == tulemus.id, Haaletus.inimene_id == inimene.id)
        .with_for_update()
    ).first()

    if haal is None:
        haal = Haaletus(
            tulemus_id=tulemus.id,
            inimene_id=inimene.id,
            eesnimi=inimene.eesnimi,
            perenimi=inimene.perenimi,
            haaletuse_aeg=nyyd(),
            otsus=otsus,
        )
        db.add(haal)
        db.flush()
        logi(db, "HAAL_ANTUD", tulemus=tulemus, inimene=inimene, uus_otsus=otsus)
    elif haal.otsus == otsus:
        logi(
            db,
            "HAAL_KORDUS",
            tulemus=tulemus,
            inimene=inimene,
            vana_otsus=haal.otsus,
            uus_otsus=otsus,
            markus="Otsus jai samaks",
        )
    else:
        vana = haal.otsus
        haal.otsus = otsus
        haal.haaletuse_aeg = nyyd()
        logi(
            db,
            "HAAL_MUUDETUD",
            tulemus=tulemus,
            inimene=inimene,
            vana_otsus=vana,
            uus_otsus=otsus,
        )

    _arvuta_tulemus(db, tulemus)
    db.commit()
    db.refresh(haal)
    return haal


def minu_haal(db: Session, inimene_id: int) -> dict[str, object]:
    inimene = db.get(Inimene, inimene_id)
    if inimene is None:
        raise HaaletusViga("Haaletajat ei leitud", kood=404)

    tulemus = viimane_voor(db)
    haal = None
    if tulemus is not None:
        haal = db.scalars(
            select(Haaletus).where(
                Haaletus.tulemus_id == tulemus.id, Haaletus.inimene_id == inimene.id
            )
        ).first()

    return {
        "inimene_id": inimene.id,
        "eesnimi": inimene.eesnimi,
        "perenimi": inimene.perenimi,
        "tulemus_id": tulemus.id if tulemus else None,
        "otsus": haal.otsus if haal else None,
        "haaletuse_aeg": haal.haaletuse_aeg if haal else None,
        "saab_muuta": bool(tulemus and on_aktiivne(tulemus)),
    }


def olek(db: Session) -> dict[str, object]:
    tulemus = viimane_voor(db)
    sulge_loppenud_voor(db, tulemus)
    inimeste_arv = db.scalar(select(func.count()).select_from(Inimene)) or 0

    if tulemus is None:
        return {
            "kestus_sekundid": get_settings().vote_duration_seconds,
            "inimeste_arv": inimeste_arv,
        }

    hetk = nyyd()
    aktiivne = on_aktiivne(tulemus, hetk)
    return {
        "tulemus_id": tulemus.id,
        "h_alguse_aeg": tulemus.h_alguse_aeg,
        "lopp_aeg": lopp_aeg(tulemus),
        "aktiivne": aktiivne,
        "jaanud_sekundid": max(0, int((lopp_aeg(tulemus) - hetk).total_seconds())) if aktiivne else 0,
        "kestus_sekundid": get_settings().vote_duration_seconds,
        "inimeste_arv": inimeste_arv,
        "haaletanute_arv": tulemus.haaletanute_arv,
        "poolt_haali": tulemus.poolt_haali,
        "vastu_haali": tulemus.vastu_haali,
    }

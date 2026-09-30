from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.aeg import nyyd
from app.config import get_settings
from app.models import Haaletus, Inimene, Tulemus


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


def viimane_voor(db: Session, *, lukusta: bool = False) -> Tulemus | None:
    paring = select(Tulemus).order_by(Tulemus.h_alguse_aeg.desc(), Tulemus.id.desc()).limit(1)
    if lukusta:
        paring = paring.with_for_update()
    return db.scalars(paring).first()


def alusta_voor(db: Session) -> Tulemus:
    kaib = viimane_voor(db)
    if kaib is not None and on_aktiivne(kaib):
        raise HaaletusViga("Haaletus juba kaib")

    tulemus = Tulemus(h_alguse_aeg=nyyd(), haaletanute_arv=0, poolt_haali=0, vastu_haali=0)
    db.add(tulemus)
    db.flush()
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
    elif haal.otsus != otsus:
        haal.otsus = otsus
        haal.haaletuse_aeg = nyyd()

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

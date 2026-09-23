from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import service
from app.database import get_db
from app.schemas import HaalIn, HaaletusOut, MinuHaalOut, OlekOut, TulemusOut

router = APIRouter(prefix="/api/haaletus", tags=["haaletus"])


def _viga(exc: service.HaaletusViga) -> HTTPException:
    return HTTPException(status_code=exc.kood, detail=exc.sonum)


@router.get("/olek", response_model=OlekOut)
def olek(db: Session = Depends(get_db)) -> dict[str, object]:
    return service.olek(db)


@router.post("/alusta", response_model=TulemusOut, status_code=201)
def alusta(db: Session = Depends(get_db)):
    try:
        return service.alusta_voor(db)
    except service.HaaletusViga as exc:
        raise _viga(exc) from exc


@router.post("/haal", response_model=HaaletusOut)
def haaleta(sisend: HaalIn, db: Session = Depends(get_db)):
    try:
        return service.anna_haal(db, sisend.inimene_id, sisend.otsus)
    except service.HaaletusViga as exc:
        raise _viga(exc) from exc


@router.get("/minu/{inimene_id}", response_model=MinuHaalOut)
def minu_haal(inimene_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        return service.minu_haal(db, inimene_id)
    except service.HaaletusViga as exc:
        raise _viga(exc) from exc

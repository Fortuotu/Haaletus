from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import service
from app.database import get_db
from app.models import Haaletus, Tulemus
from app.schemas import HaaletusOut, TulemusOut

router = APIRouter(prefix="/api/tulemused", tags=["tulemused"])


@router.get("", response_model=list[TulemusOut])
def loe_tulemused(db: Session = Depends(get_db)) -> list[Tulemus]:
    return list(db.scalars(select(Tulemus).order_by(Tulemus.id.desc())))


@router.get("/{tulemus_id}", response_model=TulemusOut)
def loe_tulemus(tulemus_id: int, db: Session = Depends(get_db)) -> Tulemus:
    tulemus = db.get(Tulemus, tulemus_id)
    if tulemus is None:
        raise HTTPException(status_code=404, detail="Haaletusvooru ei leitud")
    return tulemus


@router.get("/{tulemus_id}/haaled", response_model=list[HaaletusOut])
def loe_haaled(tulemus_id: int, db: Session = Depends(get_db)) -> list[Haaletus]:
    tulemus = db.get(Tulemus, tulemus_id)
    if tulemus is None:
        raise HTTPException(status_code=404, detail="Haaletusvooru ei leitud")
    if service.on_aktiivne(tulemus):
        raise HTTPException(status_code=403, detail="Haaletus kaib veel")
    return list(
        db.scalars(
            select(Haaletus)
            .where(Haaletus.tulemus_id == tulemus_id)
            .order_by(Haaletus.haaletuse_aeg)
        )
    )

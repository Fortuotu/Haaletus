from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Inimene
from app.schemas import InimeneOut

router = APIRouter(prefix="/api/inimesed", tags=["inimesed"])


@router.get("", response_model=list[InimeneOut])
def loe_inimesed(db: Session = Depends(get_db)) -> list[Inimene]:
    return list(db.scalars(select(Inimene).order_by(Inimene.id)))


@router.get("/{inimene_id}", response_model=InimeneOut)
def loe_inimene(inimene_id: int, db: Session = Depends(get_db)) -> Inimene:
    inimene = db.get(Inimene, inimene_id)
    if inimene is None:
        raise HTTPException(status_code=404, detail="Inimest ei leitud")
    return inimene

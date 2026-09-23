from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Logi
from app.schemas import LogiOut

router = APIRouter(prefix="/api/logi", tags=["logi"])


@router.get("", response_model=list[LogiOut])
def loe_logi(
    tulemus_id: int | None = None,
    limiit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[Logi]:
    paring = select(Logi).order_by(Logi.aeg.desc(), Logi.id.desc()).limit(limiit)
    if tulemus_id is not None:
        paring = paring.where(Logi.tulemus_id == tulemus_id)
    return list(db.scalars(paring))

from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict

Otsus = Literal["poolt", "vastu"]


def _utc(v: datetime) -> datetime:
    return v.replace(tzinfo=timezone.utc) if v.tzinfo is None else v


UtcDatetime = Annotated[datetime, AfterValidator(_utc)]


class InimeneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    eesnimi: str
    perenimi: str


class HaaletusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inimene_id: int
    eesnimi: str
    perenimi: str
    haaletuse_aeg: UtcDatetime
    otsus: Otsus


class TulemusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    h_alguse_aeg: UtcDatetime
    haaletanute_arv: int
    poolt_haali: int
    vastu_haali: int


class OlekOut(BaseModel):
    tulemus_id: int | None = None
    h_alguse_aeg: UtcDatetime | None = None
    lopp_aeg: UtcDatetime | None = None
    aktiivne: bool = False
    jaanud_sekundid: int = 0
    kestus_sekundid: int
    inimeste_arv: int
    haaletanute_arv: int = 0
    poolt_haali: int = 0
    vastu_haali: int = 0


class HaalIn(BaseModel):
    inimene_id: int
    otsus: Otsus


class MinuHaalOut(BaseModel):
    inimene_id: int
    eesnimi: str
    perenimi: str
    tulemus_id: int | None = None
    otsus: Otsus | None = None
    haaletuse_aeg: UtcDatetime | None = None
    saab_muuta: bool = False


class LogiOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    aeg: UtcDatetime
    tulemus_id: int | None
    inimene_id: int | None
    eesnimi: str | None
    perenimi: str | None
    tegevus: str
    vana_otsus: Otsus | None
    uus_otsus: Otsus | None
    markus: str | None

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Otsus = Literal["poolt", "vastu"]


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
    haaletuse_aeg: datetime
    otsus: Otsus


class TulemusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    h_alguse_aeg: datetime
    haaletanute_arv: int
    poolt_haali: int
    vastu_haali: int


class LogiOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    aeg: datetime
    tulemus_id: int | None
    inimene_id: int | None
    eesnimi: str | None
    perenimi: str | None
    tegevus: str
    vana_otsus: Otsus | None
    uus_otsus: Otsus | None
    markus: str | None

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

OtsusEnum = Enum("poolt", "vastu", name="otsus")


class Inimene(Base):
    __tablename__ = "INIMESED"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    eesnimi: Mapped[str] = mapped_column(String(50), nullable=False)
    perenimi: Mapped[str] = mapped_column(String(50), nullable=False)

    haaled: Mapped[list["Haaletus"]] = relationship(back_populates="inimene")


class Tulemus(Base):
    __tablename__ = "TULEMUSED"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    h_alguse_aeg: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    haaletanute_arv: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    poolt_haali: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vastu_haali: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    haaled: Mapped[list["Haaletus"]] = relationship(
        back_populates="tulemus", cascade="all, delete-orphan"
    )


class Haaletus(Base):
    __tablename__ = "HAALETUS"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tulemus_id: Mapped[int] = mapped_column(ForeignKey("TULEMUSED.id"), nullable=False)
    inimene_id: Mapped[int] = mapped_column(ForeignKey("INIMESED.id"), nullable=False)
    eesnimi: Mapped[str] = mapped_column(String(50), nullable=False)
    perenimi: Mapped[str] = mapped_column(String(50), nullable=False)
    haaletuse_aeg: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    otsus: Mapped[str] = mapped_column(OtsusEnum, nullable=False)

    tulemus: Mapped[Tulemus] = relationship(back_populates="haaled")
    inimene: Mapped[Inimene] = relationship(back_populates="haaled")


class Logi(Base):
    __tablename__ = "LOGI"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aeg: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    tulemus_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    inimene_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    eesnimi: Mapped[str | None] = mapped_column(String(50), nullable=True)
    perenimi: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tegevus: Mapped[str] = mapped_column(String(30), nullable=False)
    vana_otsus: Mapped[str | None] = mapped_column(OtsusEnum, nullable=True)
    uus_otsus: Mapped[str | None] = mapped_column(OtsusEnum, nullable=True)
    markus: Mapped[str | None] = mapped_column(String(255), nullable=True)

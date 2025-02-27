from __future__ import annotations

from typing import Optional, Any, Self

from pydantic import BaseModel, Field
from sqlalchemy import String, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database_util import Base

from app.models.partida_models import ChildPartidaDTO, PartidaModel


class GolModel(Base):
    __tablename__ = "gols"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    partida_id: Mapped[int] = mapped_column(ForeignKey("partidas.id"))
    rodada: Mapped[int] = mapped_column(Integer)
    clube: Mapped[str] = mapped_column(String)
    atleta: Mapped[str] = mapped_column(String)
    minuto: Mapped[str] = mapped_column(String)
    tipo_de_gol: Mapped[str] = mapped_column(String)
    partida: Mapped["PartidaModel"] = relationship("PartidaModel", back_populates="gols")


class GolDTO(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    partida_id: int
    rodada: int
    clube: str
    atleta: str
    minuto: str
    tipo_de_gol: str
    partida: ChildPartidaDTO = Field()

    @classmethod
    def from_orm(cls, gol) -> Self:
        partida_model: PartidaModel = gol.partida

        return cls(
            id=gol.id,
            partida_id=gol.partida_id,
            rodada=gol.rodada,
            clube=gol.clube,
            atleta=gol.atleta,
            minuto=gol.minuto,
            tipo_de_gol=gol.tipo_de_gol,
            partida=ChildPartidaDTO.from_orm(partida_model)
        )


class ChildGolDTO(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    rodada: int
    clube: str
    atleta: str
    minuto: str
    tipo_de_gol: str

    @classmethod
    def from_orm(cls, gol) -> Self:
        return cls(
            id=gol.id,
            rodada=gol.rodada,
            clube=gol.clube,
            atleta=gol.atleta,
            minuto=gol.minuto,
            tipo_de_gol=gol.tipo_de_gol
        )
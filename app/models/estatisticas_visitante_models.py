from __future__ import annotations

from typing import Optional, Any, Self

from pydantic import BaseModel, Field
from sqlalchemy import String, ForeignKey, Integer, DOUBLE_PRECISION, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database_util import Base

from app.models.partida_models import ChildPartidaDTO, PartidaModel

class EstatisticasVisitanteModel(Base):
    __tablename__ = "estatisticas_visitantes"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    partida_id: Mapped[int] = mapped_column(ForeignKey("partidas.id"))
    rodada: Mapped[int] = mapped_column(Integer)
    clube: Mapped[str] = mapped_column(String)
    chutes: Mapped[int] = mapped_column(Integer)
    chutes_no_alvo: Mapped[int] = mapped_column(Integer)
    posse_de_bola: Mapped[float] = mapped_column(DOUBLE_PRECISION)
    passes: Mapped[int] = mapped_column(Integer)
    precisao_passes: Mapped[float] = mapped_column(DOUBLE_PRECISION)
    faltas: Mapped[int] = mapped_column(Integer)
    cartao_amarelo: Mapped[int] = mapped_column(Integer)
    cartao_vermelho: Mapped[int] = mapped_column(Integer)
    impedimentos: Mapped[int] = mapped_column(Integer)
    escanteios: Mapped[int] = mapped_column(Integer)
    vencedor: Mapped[bool] = mapped_column(Boolean)
    partida: Mapped["PartidaModel"] = relationship("PartidaModel", back_populates="estatisticas_visitante")


class EstatisticasVisitanteDTO(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    partida_id: int
    rodada: int
    clube: str
    chutes: int
    chutes_no_alvo: int
    posse_de_bola: float
    passes: int
    precisao_passes: float
    faltas: int
    cartao_amarelo: int
    cartao_vermelho: int
    impedimentos: int
    escanteios: int
    vencedor: bool
    partida: ChildPartidaDTO = Field()

    @classmethod
    def from_orm(cls, estatisticas_visitante) -> Self:
        partida_model:PartidaModel = estatisticas_visitante.partida

        return cls(
            id=estatisticas_visitante.id,
            partida_id=estatisticas_visitante.partida_id,
            rodada=estatisticas_visitante.rodada,
            clube=estatisticas_visitante.clube,
            chutes=estatisticas_visitante.chutes,
            chutes_no_alvo=estatisticas_visitante.chutes_no_alvo,
            posse_de_bola=estatisticas_visitante.posse_de_bola,
            passes=estatisticas_visitante.passes,
            precisao_passes=estatisticas_visitante.precisao_passes,
            faltas=estatisticas_visitante.faltas,
            cartao_amarelo=estatisticas_visitante.cartao_amarelo,
            cartao_vermelho=estatisticas_visitante.cartao_vermelho,
            impedimentos=estatisticas_visitante.impedimentos,
            escanteios=estatisticas_visitante.escanteios,
            vencedor=estatisticas_visitante.vencedor,
            partida=ChildPartidaDTO.from_orm(partida_model)
        )

class ChildEstatisticasVisitanteDTO(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    rodada: int
    clube: str
    chutes: int
    chutes_no_alvo: int
    posse_de_bola: float
    passes: int
    precisao_passes: float
    faltas: int
    cartao_amarelo: int
    cartao_vermelho: int
    impedimentos: int
    escanteios: int
    vencedor: bool

    @classmethod
    def from_orm(cls, estatisticas_visitante) -> Self:
        return cls(
            id=estatisticas_visitante.id,
            rodada=estatisticas_visitante.rodada,
            clube=estatisticas_visitante.clube,
            chutes=estatisticas_visitante.chutes,
            chutes_no_alvo=estatisticas_visitante.chutes_no_alvo,
            posse_de_bola=estatisticas_visitante.posse_de_bola,
            passes=estatisticas_visitante.passes,
            precisao_passes=estatisticas_visitante.precisao_passes,
            faltas=estatisticas_visitante.faltas,
            cartao_amarelo=estatisticas_visitante.cartao_amarelo,
            cartao_vermelho=estatisticas_visitante.cartao_vermelho,
            impedimentos=estatisticas_visitante.impedimentos,
            escanteios=estatisticas_visitante.escanteios,
            vencedor=estatisticas_visitante.vencedor
        )
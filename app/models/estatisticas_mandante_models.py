from __future__ import annotations

from typing import Optional, Any, Self

from pydantic import BaseModel, Field
from sqlalchemy import String, ForeignKey, Integer, DOUBLE_PRECISION, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database_util import Base

from app.models.partida_models import ChildPartidaDTO, PartidaModel

class EstatisticasMandanteModel(Base):
    __tablename__ = "estatisticas_mandantes"
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
    partida: Mapped["PartidaModel"] = relationship("PartidaModel", back_populates="estatisticas_mandante")


class EstatisticasMandanteDTO(BaseModel):
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
    def from_orm(cls, estatisticas_mandante) -> Self:
        partida_model: PartidaModel = estatisticas_mandante.partida

        return cls(
            id=estatisticas_mandante.id,
            partida_id=estatisticas_mandante.partida_id,
            rodada=estatisticas_mandante.rodada,
            clube=estatisticas_mandante.clube,
            chutes=estatisticas_mandante.chutes,
            chutes_no_alvo=estatisticas_mandante.chutes_no_alvo,
            posse_de_bola=estatisticas_mandante.posse_de_bola,
            passes=estatisticas_mandante.passes,
            precisao_passes=estatisticas_mandante.precisao_passes,
            faltas=estatisticas_mandante.faltas,
            cartao_amarelo=estatisticas_mandante.cartao_amarelo,
            cartao_vermelho=estatisticas_mandante.cartao_vermelho,
            impedimentos=estatisticas_mandante.impedimentos,
            escanteios=estatisticas_mandante.escanteios,
            vencedor=estatisticas_mandante.vencedor,
            partida=ChildPartidaDTO.from_orm(partida_model)
        )


class ChildEstatisticasMandanteDTO(BaseModel):
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
    def from_orm(cls, estatisticas_mandante) -> Self:
        return cls(
            id=estatisticas_mandante.id,
            rodada=estatisticas_mandante.rodada,
            clube=estatisticas_mandante.clube,
            chutes=estatisticas_mandante.chutes,
            chutes_no_alvo=estatisticas_mandante.chutes_no_alvo,
            posse_de_bola=estatisticas_mandante.posse_de_bola,
            passes=estatisticas_mandante.passes,
            precisao_passes=estatisticas_mandante.precisao_passes,
            faltas=estatisticas_mandante.faltas,
            cartao_amarelo=estatisticas_mandante.cartao_amarelo,
            cartao_vermelho=estatisticas_mandante.cartao_vermelho,
            impedimentos=estatisticas_mandante.impedimentos,
            escanteios=estatisticas_mandante.escanteios,
            vencedor=estatisticas_mandante.vencedor
        )
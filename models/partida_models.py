from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field
from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database_util import Base


class PartidaModel(Base):
    __tablename__ = "partidas"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rodada: Mapped[int] = mapped_column(BigInteger)
    data: Mapped[str] = mapped_column(String)
    hora: Mapped[str] = mapped_column(String)
    mandante: Mapped[str] = mapped_column(String)
    visitante: Mapped[str] = mapped_column(String)
    formacao_mandante: Mapped[str] = mapped_column(String)
    formacao_visitante: Mapped[str] = mapped_column(String)
    tecnico_mandante: Mapped[str] = mapped_column(String)
    tecnico_visitante: Mapped[str] = mapped_column(String)
    vencedor: Mapped[Optional[str]] = mapped_column(String)
    arena: Mapped[str] = mapped_column(String)
    mandante_placar: Mapped[Optional[int]] = mapped_column(BigInteger)
    visitante_placar: Mapped[Optional[int]] = mapped_column(BigInteger)
    mandante_estado: Mapped[str] = mapped_column(String)
    visitante_estado: Mapped[str] = mapped_column(String)
    gols: Mapped[List["GolModel"]] = relationship(
        "GolModel", back_populates="partida", uselist=True
    )
    # dados_times_partida: Mapped[List["DadosTimePartidaModel"]] = relationship(
    #     "DadosTimePartidaModel", back_populates="partida", uselist=True
    # )
    # cartoes:  Mapped[List["CartaoModel"]] = relationship(
    #     "CartaoModel", back_populates="partida", uselist=True
    # )



class PartidaDTO(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    rodada: int
    data: str
    hora: str
    mandante: str
    visitante: str
    formacao_mandante: str
    formacao_visitante: str
    tecnico_mandante: str
    tecnico_visitante: str
    vencedor: Optional[str]
    arena: str
    mandante_placar: Optional[int]
    visitante_placar: Optional[int]
    mandante_estado: str
    visitante_estado: str
    gols: List["GolDTO"] = Field(default_factory=list)
    # dados_times_partida: Optional[List["DadosTimePartidaDTO"]] = Field(default_factory=list)
    # cartoes: Optional[List["CartaoDTO"]] = Field(default_factory=list)

    @classmethod
    def resolve_refs(cls):
        from models.gol_models import GolDTO
        # from models.dados_time_partida_dto import DadosTimePartidaDTO
        # from models.cartao_dto import CartaoDTO
        #
        cls.model_rebuild(_types_namespace={
            "GolDTO": GolDTO,
        #     "DadosTimePartidaDTO": DadosTimePartidaDTO,
        #     "CartaoDTO": CartaoDTO
        })
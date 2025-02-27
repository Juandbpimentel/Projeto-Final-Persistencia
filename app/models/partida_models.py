from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field
from sqlalchemy import String, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database_util import Base


class PartidaModel(Base):
    __tablename__ = "partidas"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rodada: Mapped[int] = mapped_column(Integer)
    data: Mapped[str] = mapped_column(String)
    hora: Mapped[str] = mapped_column(String)
    formacao_mandante: Mapped[str] = mapped_column(String)
    formacao_visitante: Mapped[str] = mapped_column(String)
    tecnico_mandante: Mapped[str] = mapped_column(String)
    tecnico_visitante: Mapped[str] = mapped_column(String)
    arena: Mapped[str] = mapped_column(String)
    mandante_placar: Mapped[Optional[int]] = mapped_column(Integer)
    visitante_placar: Mapped[Optional[int]] = mapped_column(Integer)
    mandante_estado: Mapped[str] = mapped_column(String)
    visitante_estado: Mapped[str] = mapped_column(String)
    gols: Mapped[Optional[List["GolModel"]]] = relationship(
        "GolModel", back_populates="partida", uselist=True
    )
    cartoes: Mapped[Optional[List["CartaoModel"]]] = relationship(
        "CartaoModel", back_populates="partida", uselist=True
    )
    estatisticas_visitante: Mapped[Optional["EstatisticasVisitanteModel"]] = relationship(
        "EstatisticasVisitanteModel", back_populates="partida", uselist=False
    )
    estatisticas_mandante: Mapped[Optional["EstatisticasMandanteModel"]] = relationship(
        "EstatisticasMandanteModel", back_populates="partida", uselist=False
    )


class PartidaDTO(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    rodada: int
    data: str
    hora: str
    formacao_mandante: str
    formacao_visitante: str
    tecnico_mandante: str
    tecnico_visitante: str
    arena: str
    mandante_placar: int
    visitante_placar: int
    mandante_estado: str
    visitante_estado: str
    gols: Optional[List["ChildGolDTO"]] = list
    cartoes: Optional[List["ChildCartaoDTO"]] = list
    estatisticas_visitante: Optional["ChildEstatisticasVisitanteDTO"] = None
    estatisticas_mandante: Optional["ChildEstatisticasMandanteDTO"] = None

    @classmethod
    def resolve_refs(cls):
        from models.gol_models import ChildGolDTO
        from models.cartoes_models import ChildCartaoDTO
        from models.estatisticas_mandante_models import ChildEstatisticasMandanteDTO
        from models.estatisticas_visitante_models import ChildEstatisticasVisitanteDTO

        cls.model_rebuild(_types_namespace={
            "ChildGolDTO": ChildGolDTO,
            "ChildCartaoDTO": ChildCartaoDTO,
            "ChildEstatisticasVisitanteDTO": ChildEstatisticasMandanteDTO,
            "ChildEstatisticasMandanteDTO": ChildEstatisticasVisitanteDTO
        })

    @classmethod
    def from_orm(cls, partida):
        from models.gol_models import ChildGolDTO
        from models.cartoes_models import ChildCartaoDTO
        from models.estatisticas_mandante_models import ChildEstatisticasMandanteDTO
        from models.estatisticas_visitante_models import ChildEstatisticasVisitanteDTO

        return cls(
            id=partida.id,
            rodada=partida.rodada,
            data=partida.data,
            hora=partida.hora,
            formacao_mandante=partida.formacao_mandante,
            formacao_visitante=partida.formacao_visitante,
            tecnico_mandante=partida.tecnico_mandante,
            tecnico_visitante=partida.tecnico_visitante,
            arena=partida.arena,
            mandante_placar=partida.mandante_placar,
            visitante_placar=partida.visitante_placar,
            mandante_estado=partida.mandante_estado,
            visitante_estado=partida.visitante_estado,
            gols=[ChildGolDTO.from_orm(gol) for gol in partida.gols],
            cartoes=[ChildCartaoDTO.from_orm(cartao) for cartao in partida.cartoes],
            estatisticas_visitante= ChildEstatisticasMandanteDTO.from_orm(partida.estatisticas_visitante),
            estatisticas_mandante= ChildEstatisticasVisitanteDTO.from_orm(partida.estatisticas_mandante)
        )


class ChildPartidaDTO(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    rodada: int
    data: str
    hora: str
    formacao_mandante: str
    formacao_visitante: str
    tecnico_mandante: str
    tecnico_visitante: str
    arena: str
    mandante_placar: Optional[int]
    visitante_placar: Optional[int]
    mandante_estado: str
    visitante_estado: str
    gols_ids: List[int] = list
    cartoes_ids: List[int] = list
    estatisticas_visitante_id: Optional[int] = None
    estatisticas_mandante_id: Optional[int] = None

    @classmethod
    def from_orm(cls,partida) -> ChildPartidaDTO:
        return cls(
            id=partida.id,
            rodada=partida.rodada,
            data=partida.data,
            hora=partida.hora,
            formacao_mandante=partida.formacao_mandante,
            formacao_visitante=partida.formacao_visitante,
            tecnico_mandante=partida.tecnico_mandante,
            tecnico_visitante=partida.tecnico_visitante,
            arena=partida.arena,
            mandante_placar=partida.mandante_placar,
            visitante_placar=partida.visitante_placar,
            mandante_estado=partida.mandante_estado,
            visitante_estado=partida.visitante_estado,
            gols_ids=[gol.id for gol in partida.gols],
            cartoes_ids=[cartao.id for cartao in partida.cartoes],
            estatisticas_visitante_id=partida.estatisticas_visitante.id,
            estatisticas_mandante_id=partida.estatisticas_visitante.id
        )


class CreatePartidaDTO(BaseModel):
    rodada: int
    data: str
    hora: str
    formacao_mandante: str
    formacao_visitante: str
    tecnico_mandante: str
    tecnico_visitante: str
    arena: str
    mandante_placar: int
    visitante_placar: int
    mandante_estado: str
    visitante_estado: str
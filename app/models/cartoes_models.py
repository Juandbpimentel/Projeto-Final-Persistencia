from __future__ import annotations

from typing import Optional, Any, Self

from pydantic import BaseModel, Field
from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database_util import Base

from app.models.partida_models import ChildPartidaDTO, PartidaModel

class CartaoModel(Base):
    __tablename__ = "cartoes"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    partida_id: Mapped[int] = mapped_column(ForeignKey("partidas.id"))
    rodada: Mapped[int] = mapped_column(BigInteger)
    clube: Mapped[str] = mapped_column(String)
    cartao: Mapped[str] = mapped_column(String)
    atleta: Mapped[str] = mapped_column(String)
    num_camisa: Mapped[BigInteger] = mapped_column(BigInteger)
    posicao: Mapped[str] = mapped_column(String)
    minuto: Mapped[str] = mapped_column(String)
    partida: Mapped["PartidaModel"] = relationship("PartidaModel", back_populates="cartoes")


class CartaoDTO(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    partida_id: int
    rodada: int
    clube: str
    cartao: str
    atleta: str
    num_camisa: int
    posicao: str
    minuto: str
    partida: ChildPartidaDTO = Field()

    @classmethod
    def from_orm(cls, cartao) -> Self:
        partida_model: PartidaModel = cartao.partida

        return cls(
            id=cartao.id,
            partida_id=cartao.partida_id,
            rodada=cartao.rodada,
            clube=cartao.clube,
            cartao=cartao.cartao,
            atleta=cartao.atleta,
            num_camisa=cartao.num_camisa,
            posicao=cartao.posicao,
            minuto=cartao.minuto,
            partida=ChildPartidaDTO.from_orm(partida_model)
        )


class ChildCartaoDTO(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    rodada: int
    clube: str
    cartao: str
    atleta: str
    num_camisa: int
    posicao: str
    minuto: str

    @classmethod
    def from_orm(cls, cartao) -> Self:
        return cls(
            id=cartao.id,
            rodada=cartao.rodada,
            clube=cartao.clube,
            cartao=cartao.cartao,
            atleta=cartao.atleta,
            num_camisa=cartao.num_camisa,
            posicao=cartao.posicao,
            minuto=cartao.minuto
        )
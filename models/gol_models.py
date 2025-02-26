from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database_util import Base

class GolModel(Base):
    __tablename__ = "gols"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    partida_id: Mapped[int] = mapped_column(ForeignKey("partidas.id"))
    rodada: Mapped[int] = mapped_column(BigInteger)
    clube: Mapped[str] = mapped_column(String)
    atleta: Mapped[str] = mapped_column(String)
    minuto: Mapped[int] = mapped_column(BigInteger)
    tipo_de_gol: Mapped[str] = mapped_column(String)
    partida: Mapped["PartidaModel"] = relationship("PartidaModel", back_populates="gols")



class GolDTO(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    partida_id: int
    rodada: int
    clube: str
    atleta: str
    minuto: int
    tipo_de_gol: str
    partida: "PartidaDTO" = Field(default_factory=dict)

    @classmethod
    def resolve_refs(cls):
        from models.partida_models import PartidaDTO

        cls.model_rebuild(_types_namespace={"PartidaDTO": PartidaDTO})
# Compare this snippet from models/cartao_models.py:
# from typing import Optional
#
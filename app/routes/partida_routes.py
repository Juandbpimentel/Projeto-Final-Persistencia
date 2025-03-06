from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from sqlalchemy.orm import subqueryload, selectinload

from app.database_util import get_db
from app.models.partida_models import PartidaModel, PartidaDTO, CreatePartidaDTO

router = APIRouter(
    prefix="/partidas",
    tags=["partidas"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"},
    },
)

class PartidasResponse(BaseModel):
    partidas: List[PartidaDTO]
    next_cursor: Optional[int]

@router.get("/list", response_model=PartidasResponse)
async def fetch_partidas_with_cursor(
        session: AsyncSession = Depends(get_db),
        limit: int = Query(10, ge=1),
        start_cursor: Optional[int] = Query(None)
) -> PartidasResponse:
    query = select(PartidaModel).order_by(PartidaModel.id).options(
        selectinload(PartidaModel.gols),
        selectinload(PartidaModel.cartoes),
        selectinload(PartidaModel.estatisticas_visitante),
        selectinload(PartidaModel.estatisticas_mandante)
    ).limit(limit)

    if start_cursor:
        query = query.where(PartidaModel.id > start_cursor)

    result = await session.execute(query)
    partidas = result.scalars().all()
    partidas_dto = [PartidaDTO.from_orm(partida) for partida in partidas]

    next_cursor = partidas_dto[-1].id if partidas_dto else None

    return PartidasResponse(partidas=partidas_dto, next_cursor=next_cursor)


@router.get("/{partida_id}", response_model=PartidaDTO)
async def get_partida(partida_id: int, session: AsyncSession = Depends(get_db)) -> PartidaDTO:
    async with session.begin():
        query = select(PartidaModel).options(
            selectinload(PartidaModel.gols),
            selectinload(PartidaModel.cartoes),
            selectinload(PartidaModel.estatisticas_visitante),
            selectinload(PartidaModel.estatisticas_mandante)
        ).where(PartidaModel.id == partida_id)

        result = await session.execute(query)
        partida = result.scalars().first()

        if not partida:
            raise HTTPException(status_code=404, detail="Partida not found")

        return PartidaDTO.from_orm(partida)

@router.post("", response_model=PartidaDTO)
async def post_partida(*, session: AsyncSession = Depends(get_db), partida: CreatePartidaDTO) -> PartidaDTO:
    new_partida = PartidaModel(
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
        visitante_estado=partida.visitante_estado
    )
    session.add(new_partida)
    await session.commit()
    await session.refresh(new_partida, [attr.key for attr in inspect(PartidaModel).attrs])
    return PartidaDTO.from_orm(new_partida)

@router.put("/{partida_id}", response_model=PartidaDTO)
async def update_partida(partida_id: int, partida: CreatePartidaDTO, session: AsyncSession = Depends(get_db)) -> PartidaDTO:
    existing_partida = await session.get(PartidaModel, partida_id, options=[
        selectinload(PartidaModel.gols),
        selectinload(PartidaModel.cartoes),
        selectinload(PartidaModel.estatisticas_visitante),
        selectinload(PartidaModel.estatisticas_mandante)
    ])
    if not existing_partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    for key, value in partida.model_dump().items():
        setattr(existing_partida, key, value)

    session.add(existing_partida)
    await session.commit()
    await session.refresh(existing_partida)
    return PartidaDTO.from_orm(existing_partida)

@router.delete("/{partida_id}", response_model=dict)
async def delete_partida(partida_id: int, session: AsyncSession = Depends(get_db)) -> dict:
    async with session.begin():
        partida = await session.get(PartidaModel, partida_id)
        if not partida:
            raise HTTPException(status_code=404, detail="Partida not found")

        await session.delete(partida)
        await session.commit()
    return {"detail": "Partida deleted successfully"}
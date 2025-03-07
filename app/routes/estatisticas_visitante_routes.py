from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from sqlalchemy.orm import selectinload

from app.models.estatisticas_visitante_models import EstatisticasVisitanteModel, EstatisticasVisitanteDTO, \
    CreateEstatisticasVisitanteDTO
from app.database_util import get_db
from app.models.partida_models import PartidaModel

router = APIRouter(
    prefix="/estatisticas_visitante",
    tags=["estatisticas_visitante"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"},
    },
)

class EstatisticasVisitanteResponse(BaseModel):
    estatisticas: List[EstatisticasVisitanteDTO]
    next_cursor: Optional[int]

@router.get("/list", response_model=EstatisticasVisitanteResponse)
async def fetch_estatisticas_visitante_with_cursor(
        session: AsyncSession = Depends(get_db),
        limit: int = Query(10, ge=0),
        start_cursor: Optional[int] = Query(None),
        rodada: Optional[int] = Query(None),
        clube: Optional[str] = Query(None),
        chutes: Optional[int] = Query(None),
        chutes_no_alvo: Optional[int] = Query(None),
        posse_de_bola: Optional[float] = Query(None),
        passes: Optional[int] = Query(None),
        precisao_passes: Optional[float] = Query(None),
        faltas: Optional[int] = Query(None),
        cartao_amarelo: Optional[int] = Query(None),
        cartao_vermelho: Optional[int] = Query(None),
        impedimentos: Optional[int] = Query(None),
        escanteios: Optional[int] = Query(None),
        vencedor: Optional[str] = Query(None)
) -> EstatisticasVisitanteResponse:
    query = select(EstatisticasVisitanteModel).order_by(EstatisticasVisitanteModel.id).options(
        selectinload(EstatisticasVisitanteModel.partida),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.gols),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.cartoes),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.estatisticas_visitante),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.estatisticas_mandante),
    )

    if not limit and limit != 0:
        query = query.limit(10)
    elif limit > 0:
        query = query.limit(limit)

    if start_cursor:
        query = query.where(EstatisticasVisitanteModel.id > start_cursor)
    if rodada:
        query = query.where(EstatisticasVisitanteModel.rodada == rodada)
    if clube:
        query = query.where(EstatisticasVisitanteModel.clube == clube)
    if chutes:
        query = query.where(EstatisticasVisitanteModel.chutes >= chutes)
    if chutes_no_alvo:
        query = query.where(EstatisticasVisitanteModel.chutes_no_alvo >= chutes_no_alvo)
    if posse_de_bola:
        query = query.where(EstatisticasVisitanteModel.posse_de_bola >= posse_de_bola)
    if passes:
        query = query.where(EstatisticasVisitanteModel.passes >= passes)
    if precisao_passes:
        query = query.where(EstatisticasVisitanteModel.precisao_passes >= precisao_passes)
    if faltas:
        query = query.where(EstatisticasVisitanteModel.faltas >= faltas)
    if cartao_amarelo:
        query = query.where(EstatisticasVisitanteModel.cartao_amarelo >= cartao_amarelo)
    if cartao_vermelho:
        query = query.where(EstatisticasVisitanteModel.cartao_vermelho >= cartao_vermelho)
    if impedimentos:
        query = query.where(EstatisticasVisitanteModel.impedimentos >= impedimentos)
    if escanteios:
        query = query.where(EstatisticasVisitanteModel.escanteios >= escanteios)
    if vencedor:
        query = query.where(EstatisticasVisitanteModel.vencedor == vencedor)


    result = await session.execute(query)
    estatisticas = result.scalars().all()
    estatisticas_dto = [EstatisticasVisitanteDTO.from_orm(estatistica) for estatistica in estatisticas]

    next_cursor = estatisticas_dto[-1].id if estatisticas_dto else None

    return EstatisticasVisitanteResponse(estatisticas=estatisticas_dto, next_cursor=next_cursor)

@router.get("/count", response_model=int)
async def count_estatisticas_visitante(session: AsyncSession = Depends(get_db)) -> int:
    query = select(EstatisticasVisitanteModel.id)
    result = await session.execute(query)
    return len(result.scalars().all())

@router.get("/{estatistica_id}", response_model=EstatisticasVisitanteDTO)
async def get_estatistica_visitante(estatistica_id: int, session: AsyncSession = Depends(get_db)) -> EstatisticasVisitanteDTO:
    async with session.begin():
        query = select(EstatisticasVisitanteModel).options(
            selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.gols),
            selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.cartoes),
            selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.estatisticas_visitante),
            selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.estatisticas_mandante),
        ).where(EstatisticasVisitanteModel.id == estatistica_id)

        result = await session.execute(query)
        estatistica = result.scalars().first()

        if not estatistica:
            raise HTTPException(status_code=404, detail="Estatística não encontrada")

        return EstatisticasVisitanteDTO.from_orm(estatistica)

@router.post("", response_model=EstatisticasVisitanteDTO)
async def post_estatistica_visitante(*, session: AsyncSession = Depends(get_db), estatistica: CreateEstatisticasVisitanteDTO) -> EstatisticasVisitanteDTO:
    new_estatistica = EstatisticasVisitanteModel(
        partida_id=estatistica.partida_id,
        rodada=estatistica.rodada,
        clube=estatistica.clube,
        chutes=estatistica.chutes,
        chutes_no_alvo=estatistica.chutes_no_alvo,
        posse_de_bola=estatistica.posse_de_bola,
        passes=estatistica.passes,
        precisao_passes=estatistica.precisao_passes,
        faltas=estatistica.faltas,
        cartao_amarelo=estatistica.cartao_amarelo,
        cartao_vermelho=estatistica.cartao_vermelho,
        impedimentos=estatistica.impedimentos,
        escanteios=estatistica.escanteios,
        vencedor=estatistica.vencedor
    )
    session.add(new_estatistica)
    await session.commit()
    await session.refresh(new_estatistica)

    query = select(EstatisticasVisitanteModel).options(
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.gols),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.cartoes),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.estatisticas_visitante),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.estatisticas_mandante),
    ).where(EstatisticasVisitanteModel.id == new_estatistica.id)
    result = (await session.execute(query)).scalars().first()
    return EstatisticasVisitanteDTO.from_orm(result)

@router.put("/{estatistica_id}", response_model=EstatisticasVisitanteDTO)
async def update_estatistica_visitante(estatistica_id: int, estatistica: CreateEstatisticasVisitanteDTO, session: AsyncSession = Depends(get_db)) -> EstatisticasVisitanteDTO:
    existing_estatistica = await session.get(EstatisticasVisitanteModel, estatistica_id,options=[
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.gols),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.cartoes),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.estatisticas_visitante),
        selectinload(EstatisticasVisitanteModel.partida).selectinload(PartidaModel.estatisticas_mandante),
    ])
    if not existing_estatistica:
        raise HTTPException(status_code=404, detail="Estatística não encontrada")

    for key, value in estatistica.model_dump().items():
        setattr(existing_estatistica, key, value)

    session.add(existing_estatistica)
    await session.commit()
    await session.refresh(existing_estatistica)
    return EstatisticasVisitanteDTO.from_orm(existing_estatistica)

@router.delete("/{estatistica_id}", response_model=dict)
async def delete_estatistica_visitante(estatistica_id: int, session: AsyncSession = Depends(get_db)) -> dict:
    async with session.begin():
        estatistica = await session.get(EstatisticasVisitanteModel, estatistica_id)
        if not estatistica:
            raise HTTPException(status_code=404, detail="Estatística não encontrada")

        await session.delete(estatistica)
        await session.commit()
    return {"detail": "Estatística deletada com sucesso"}
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from sqlalchemy.orm import selectinload

from app.models.estatisticas_mandante_models import EstatisticasMandanteModel, EstatisticasMandanteDTO, CreateEstatisticasMandanteDTO
from app.database_util import get_db
from app.models.partida_models import PartidaModel

router = APIRouter(
    prefix="/estatisticas_mandante",
    tags=["estatisticas_mandante"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"},
    },
)

class EstatisticasMandanteResponse(BaseModel):
    estatisticas: List[EstatisticasMandanteDTO]
    next_cursor: Optional[int]

@router.get("/list", response_model=EstatisticasMandanteResponse)
async def fetch_estatisticas_mandante_with_cursor(
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
) -> EstatisticasMandanteResponse:
    query = select(EstatisticasMandanteModel).order_by(EstatisticasMandanteModel.id).options(
        selectinload(EstatisticasMandanteModel.partida),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.gols),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.cartoes),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.estatisticas_visitante),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.estatisticas_mandante),
    )

    if not limit and limit != 0:
        query = query.limit(10)
    elif limit > 0:
        query = query.limit(limit)

    if start_cursor:
        query = query.where(EstatisticasMandanteModel.id > start_cursor)
    if rodada:
        query = query.where(EstatisticasMandanteModel.rodada == rodada)
    if clube:
        query = query.where(EstatisticasMandanteModel.clube == clube)
    if chutes:
        query = query.where(EstatisticasMandanteModel.chutes >= chutes)
    if chutes_no_alvo:
        query = query.where(EstatisticasMandanteModel.chutes_no_alvo >= chutes_no_alvo)
    if posse_de_bola:
        query = query.where(EstatisticasMandanteModel.posse_de_bola >= posse_de_bola)
    if passes:
        query = query.where(EstatisticasMandanteModel.passes >= passes)
    if precisao_passes:
        query = query.where(EstatisticasMandanteModel.precisao_passes >= precisao_passes)
    if faltas:
        query = query.where(EstatisticasMandanteModel.faltas >= faltas)
    if cartao_amarelo:
        query = query.where(EstatisticasMandanteModel.cartao_amarelo >= cartao_amarelo)
    if cartao_vermelho:
        query = query.where(EstatisticasMandanteModel.cartao_vermelho >= cartao_vermelho)
    if impedimentos:
        query = query.where(EstatisticasMandanteModel.impedimentos >= impedimentos)
    if escanteios:
        query = query.where(EstatisticasMandanteModel.escanteios >= escanteios)
    if vencedor:
        query = query.where(EstatisticasMandanteModel.vencedor == vencedor)

    result = await session.execute(query)
    estatisticas = result.scalars().all()
    estatisticas_dto = [EstatisticasMandanteDTO.from_orm(estatistica) for estatistica in estatisticas]

    next_cursor = estatisticas_dto[-1].id if estatisticas_dto else None

    return EstatisticasMandanteResponse(estatisticas=estatisticas_dto, next_cursor=next_cursor)

@router.get("/count", response_model=int)
async def count_estatisticas_mandante(session: AsyncSession = Depends(get_db)) -> int:
    query = select(EstatisticasMandanteModel.id)
    result = await session.execute(query)
    return len(result.scalars().all())

@router.get("/{estatistica_id}", response_model=EstatisticasMandanteDTO)
async def get_estatistica_mandante(estatistica_id: int, session: AsyncSession = Depends(get_db)) -> EstatisticasMandanteDTO:
    async with session.begin():
        query = select(EstatisticasMandanteModel).options(
            selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.gols),
            selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.cartoes),
            selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.estatisticas_visitante),
            selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.estatisticas_mandante),
        ).where(EstatisticasMandanteModel.id == estatistica_id)

        result = await session.execute(query)
        estatistica = result.scalars().first()

        if not estatistica:
            raise HTTPException(status_code=404, detail="Estatística não encontrada")

        return EstatisticasMandanteDTO.from_orm(estatistica)

@router.post("", response_model=EstatisticasMandanteDTO)
async def post_estatistica_mandante(*, session: AsyncSession = Depends(get_db), estatistica: CreateEstatisticasMandanteDTO) -> EstatisticasMandanteDTO:
    new_estatistica = EstatisticasMandanteModel(
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

    query = select(EstatisticasMandanteModel).options(
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.gols),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.cartoes),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.estatisticas_visitante),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.estatisticas_mandante),
    ).where(EstatisticasMandanteModel.id == new_estatistica.id)
    result = (await session.execute(query)).scalars().first()
    return EstatisticasMandanteDTO.from_orm(result)

@router.put("/{estatistica_id}", response_model=EstatisticasMandanteDTO)
async def update_estatistica_mandante(estatistica_id: int, estatistica: CreateEstatisticasMandanteDTO, session: AsyncSession = Depends(get_db)) -> EstatisticasMandanteDTO:
    existing_estatistica = await session.get(EstatisticasMandanteModel, estatistica_id, options=[
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.gols),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.cartoes),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.estatisticas_visitante),
        selectinload(EstatisticasMandanteModel.partida).selectinload(PartidaModel.estatisticas_mandante),
    ])
    if not existing_estatistica:
        raise HTTPException(status_code=404, detail="Estatística não encontrada")

    for key, value in estatistica.model_dump().items():
        setattr(existing_estatistica, key, value)

    session.add(existing_estatistica)
    await session.commit()
    await session.refresh(existing_estatistica)
    return EstatisticasMandanteDTO.from_orm(existing_estatistica)

@router.delete("/{estatistica_id}", response_model=dict)
async def delete_estatistica_mandante(estatistica_id: int, session: AsyncSession = Depends(get_db)) -> dict:
    async with session.begin():
        estatistica = await session.get(EstatisticasMandanteModel, estatistica_id)
        if not estatistica:
            raise HTTPException(status_code=404, detail="Estatística não encontrada")

        await session.delete(estatistica)
        await session.commit()
    return {"detail": "Estatística deletada com sucesso"}
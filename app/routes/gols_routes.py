from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from sqlalchemy.orm import selectinload

from app.models.gol_models import GolModel, GolDTO, CreateGolDTO
from app.database_util import get_db

router = APIRouter(
    prefix="/gols",
    tags=["gols"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"},
    },
)

class GolsResponse(BaseModel):
    gols: List[GolDTO]
    next_cursor: Optional[int]

@router.get("/list", response_model=GolsResponse)
async def fetch_gols_with_cursor(
    session: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1),
    start_cursor: Optional[int] = Query(None)
) -> GolsResponse:
    query = select(GolModel).order_by(GolModel.id).options(
        selectinload(GolModel.partida)
    ).limit(limit)
    
    if start_cursor:
        query = query.where(GolModel.id > start_cursor)

    result = await session.execute(query)
    gols = result.scalars().all()
    gols_dto = [GolDTO.from_orm(gol) for gol in gols]

    next_cursor = gols_dto[-1].id if gols_dto else None

    return GolsResponse(gols=gols_dto, next_cursor=next_cursor)


@router.get("/{gol_id}", response_model=GolDTO)
async def get_gol(gol_id: int, session: AsyncSession = Depends(get_db)) -> GolDTO:
    async with session.begin():
        query = select(GolModel).options(
            selectinload(GolModel.partida)
        ).where(GolModel.id == gol_id)

        result = await session.execute(query)
        gol = result.scalars().first()

        if not gol:
            raise HTTPException(status_code=404, detail="Gol não encontrado")

        return GolDTO.from_orm(gol)


@router.post("", response_model=GolDTO)
async def post_gol(*, session: AsyncSession = Depends(get_db), gol: CreateGolDTO) -> GolDTO:
    new_gol = GolModel(
        partida_id=gol.partida_id,
        rodada=gol.rodada,
        clube=gol.clube,
        atleta=gol.atleta,
        minuto=gol.minuto,
        tipo_de_gol=gol.tipo_de_gol
    )
    session.add(new_gol)
    
    await session.commit()
    await session.refresh(new_gol)
    
    return GolDTO.from_orm(new_gol)


@router.put("/{gol_id}", response_model=GolDTO)
async def update_gol(gol_id: int, gol: CreateGolDTO, session: AsyncSession = Depends(get_db)) -> GolDTO:
    existing_gol = await session.get(GolModel, gol_id, options=[
        selectinload(GolModel.partida)
    ])
    
    if not existing_gol:
        raise HTTPException(status_code=404, detail="Gol not found")

    for key, value in gol.model_dump().items():
        setattr(existing_gol, key, value)

    session.add(existing_gol)
    
    await session.commit()
    await session.refresh(existing_gol)
    
    return GolDTO.from_orm(existing_gol)


@router.delete("/{gol_id}", response_model=dict)
async def delete_gol(gol_id: int, session: AsyncSession = Depends(get_db)) -> dict:
    async with session.begin():
        gol = await session.get(GolModel, gol_id)
        
        if not gol:
            raise HTTPException(status_code=404, detail="Gol not found")

        await session.delete(gol)
        await session.commit()
    
        return {"detail": "Gol deleted successfully"}
    
    
@router.get("/contagem-por-tipo-e-clube", response_model=Dict[str, Dict[str, int]])
async def get_contagem_gols_por_tipo_e_clube(
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Dict[str, int]]:
    async with session.begin():
        query = (
            select(
                GolModel.clube,
                GolModel.tipo_de_gol,
                func.count(GolModel.id).label("total")
            )
            .group_by(GolModel.clube, GolModel.tipo_de_gol)
        )
        
        result = await session.execute(query)
        gols_por_clube = result.all()
        estatisticas = {}
    
        for clube, tipo_gol, total in gols_por_clube:
            if clube not in estatisticas:
                estatisticas[clube] = {}
            estatisticas[clube][tipo_gol] = total

        return estatisticas
    

@router.get("/jogador/{nome_jogador}", response_model=List[GolDTO])
async def get_gols_por_jogador(
    nome_jogador: str,
    session: AsyncSession = Depends(get_db)
) -> List[GolDTO]:
    async with session.begin():
        query = (
            select(GolModel)
            .options(selectinload(GolModel.partida))
            .where(GolModel.atleta == nome_jogador)
        )

        result = await session.execute(query)
        gols = result.scalars().all()

        if not gols:
            raise HTTPException(status_code=404, detail="Nenhum gol encontrado para este jogador")

        gols_dto = [GolDTO.from_orm(gol) for gol in gols]

        return gols_dto
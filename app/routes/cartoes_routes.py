from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from sqlalchemy.orm import selectinload

from app.models.cartoes_models import CartaoModel, CartaoDTO, CreateCartaoDTO
from app.database_util import get_db

router = APIRouter(
    prefix="/cartoes",
    tags=["cartoes"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"},
    },
)

class CartoesResponse(BaseModel):
    cartoes: List[CartaoDTO]
    next_cursor: Optional[int]

@router.get("/list", response_model=CartoesResponse)
async def fetch_cartoes_with_cursor(
    session: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1),
    start_cursor: Optional[int] = Query(None)
) -> CartoesResponse:
    query = select(CartaoModel).order_by(CartaoModel.id).options(
        selectinload(CartaoModel.partida)
    ).limit(limit)

    if start_cursor:
        query = query.where(CartaoModel.id > start_cursor)

    result = await session.execute(query)
    cartoes = result.scalars().all()
    cartoes_dto = [CartaoDTO.from_orm(cartao) for cartao in cartoes]

    next_cursor = cartoes_dto[-1].id if cartoes_dto else None

    return CartoesResponse(cartoes=cartoes_dto, next_cursor=next_cursor)


@router.get("/{cartao_id}", response_model=CartaoDTO)
async def get_cartao(cartao_id: int, session: AsyncSession = Depends(get_db)) -> CartaoDTO:
    async with session.begin():
        query = select(CartaoModel).options(
            selectinload(CartaoModel.partida)
        ).where(CartaoModel.id == cartao_id)

        result = await session.execute(query)
        cartao = result.scalars().first()

        if not cartao:
            raise HTTPException(status_code=404, detail="Cartão não encontrado")

        return CartaoDTO.from_orm(cartao)


@router.post("", response_model=CartaoDTO)
async def post_cartao(*, session: AsyncSession = Depends(get_db), cartao: CreateCartaoDTO) -> CartaoDTO:
    new_cartao = CartaoModel(
        partida_id=cartao.partida_id,
        rodada=cartao.rodada,
        clube=cartao.clube,
        cartao=cartao.cartao,
        atleta=cartao.atleta,
        num_camisa=cartao.num_camisa,
        posicao=cartao.posicao,
        minuto=cartao.minuto
    )
    session.add(new_cartao)
    
    await session.commit()
    await session.refresh(new_cartao)
    
    return CartaoDTO.from_orm(new_cartao)


@router.put("/{cartao_id}", response_model=CartaoDTO)
async def update_cartao(cartao_id: int, cartao: CreateCartaoDTO, session: AsyncSession = Depends(get_db)) -> CartaoDTO:
    existing_cartao = await session.get(CartaoModel, cartao_id, options=[
        selectinload(CartaoModel.partida)
    ])
    
    if not existing_cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")

    for key, value in cartao.model_dump().items():
        setattr(existing_cartao, key, value)

    session.add(existing_cartao)
    
    await session.commit()
    await session.refresh(existing_cartao)
    
    return CartaoDTO.from_orm(existing_cartao)


@router.delete("/{cartao_id}", response_model=dict)
async def delete_cartao(cartao_id: int, session: AsyncSession = Depends(get_db)) -> dict:
    async with session.begin():
        cartao = await session.get(CartaoModel, cartao_id)
        
        if not cartao:
            raise HTTPException(status_code=404, detail="Cartão não encontrado")

        await session.delete(cartao)
        await session.commit()
    
        return {"detail": "Cartão deletado com sucesso"}
    

@router.get("/contagem-por-clube", response_model=Dict[str, Dict[str, int]])
async def get_contagem_cartoes_por_clube(
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Dict[str, int]]:
    async with session.begin():
        query = (
            select(
                CartaoModel.clube,
                CartaoModel.cartao,
                func.count(CartaoModel.id).label("total")
            )
            .group_by(CartaoModel.clube, CartaoModel.cartao)
        )
        
        result = await session.execute(query)
        cartoes_por_clube = result.all()
        estatisticas = {}
        
        for clube, tipo_cartao, total in cartoes_por_clube:
            if clube not in estatisticas:
                estatisticas[clube] = {"amarelo": 0, "vermelho": 0}
            
            if tipo_cartao.lower() == "amarelo":
                estatisticas[clube]["amarelo"] += total
            elif tipo_cartao.lower() == "vermelho":
                estatisticas[clube]["vermelho"] += total

        return estatisticas
    

@router.get("/jogador/{nome_jogador}", response_model=List[CartaoDTO])
async def get_cartoes_por_jogador(
    nome_jogador: str,
    session: AsyncSession = Depends(get_db)
) -> List[CartaoDTO]:
    async with session.begin():
        query = (
            select(CartaoModel)
            .options(selectinload(CartaoModel.partida))
            .where(CartaoModel.atleta == nome_jogador)
        )
        
        result = await session.execute(query)
        cartoes = result.scalars().all()

        if not cartoes:
            raise HTTPException(status_code=404, detail="Nenhum cartão encontrado para este jogador")

        cartoes_dto = [CartaoDTO.from_orm(cartao) for cartao in cartoes]

        return cartoes_dto
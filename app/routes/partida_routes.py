from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, inspect, func, or_, and_, case
from unidecode import unidecode
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from app.models.partida_models import EstatisticasPartidasResponse, VitoriasGolsPorRodadaResponse
from sqlalchemy.orm import subqueryload, selectinload
import matplotlib.pyplot as plt
from fastapi.responses import StreamingResponse
import io
from app.models.estatisticas_mandante_models import EstatisticasMandanteModel
from app.models.estatisticas_visitante_models import EstatisticasVisitanteModel
import logging
from app.models.partida_models import PartidaModel, PartidaDTO, CreatePartidaDTO
from app.database_util import get_db

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
        limit: int = Query(10, ge=0),
        start_cursor: Optional[int] = Query(None),
        rodada: Optional[int] = Query(None),
        data_inicio: Optional[str] = Query(None),
        data_fim: Optional[str] = Query(None),
        mandante: Optional[str] = Query(None),
        visitante: Optional[str] = Query(None),
        estado: Optional[str] = Query(None),
) -> PartidasResponse:
    query = select(PartidaModel).order_by(PartidaModel.id).options(
        selectinload(PartidaModel.gols),
        selectinload(PartidaModel.cartoes),
        selectinload(PartidaModel.estatisticas_visitante),
        selectinload(PartidaModel.estatisticas_mandante)
    )

    if not limit and limit != 0:
        query = query.limit(10)
    elif limit > 0:
        query = query.limit(limit)

    if start_cursor:
        query = query.where(PartidaModel.id > start_cursor)
    if rodada:
        query = query.where(PartidaModel.rodada == rodada)
    from sqlalchemy import func
    if data_inicio:
        query = query.where(func.to_date(PartidaModel.data, 'DD/MM/YYYY') >= func.to_date(data_inicio, 'DD/MM/YYYY'))
    if data_fim:
        query = query.where(func.to_date(PartidaModel.data, 'DD/MM/YYYY') <= func.to_date(data_fim, 'DD/MM/YYYY'))
    if mandante:
        query = query.where(PartidaModel.estatisticas_mandante.has(clube=mandante))
    if visitante:
        query = query.where(PartidaModel.estatisticas_visitante.has(clube=visitante))
    if estado:
        query = query.where(PartidaModel.mandante_estado == estado)

    result = await session.execute(query)
    partidas = result.scalars().all()
    partidas_dto = [PartidaDTO.from_orm(partida) for partida in partidas]

    next_cursor = partidas_dto[-1].id if partidas_dto else None

    return PartidasResponse(partidas=partidas_dto, next_cursor=next_cursor)

@router.get("/count", response_model=int)
async def count_partidas(session: AsyncSession = Depends(get_db)) -> int:
    query = select(PartidaModel.id)
    result = await session.execute(query)
    return len(result.scalars().all())

@router.get("/estatisticas", response_model=EstatisticasPartidasResponse)
async def get_estatisticas(session: AsyncSession = Depends(get_db)) -> EstatisticasPartidasResponse:
    query = select(
        func.avg(PartidaModel.mandante_placar).label("media_gols_mandante"),
        func.avg(PartidaModel.visitante_placar).label("media_gols_visitante"),
        func.sum(PartidaModel.mandante_placar).label("total_gols_mandante"),
        func.sum(PartidaModel.visitante_placar).label("total_gols_visitante")
    )
    
    result = await session.execute(query)
    estatisticas = result.fetchone()
    
    return EstatisticasPartidasResponse(
        media_gols_mandante=estatisticas.media_gols_mandante,
        media_gols_visitante=estatisticas.media_gols_visitante,
        total_gols_mandante=estatisticas.total_gols_mandante,
        total_gols_visitante=estatisticas.total_gols_visitante
    )



@router.get("/vitorias", response_model=dict)
async def calcular_vitorias(
    session: AsyncSession = Depends(get_db),
    clube_a: str = Query(..., description="Nome do primeiro clube"),
    clube_b: str = Query(..., description="Nome do segundo clube")
) -> dict:
    
    clube_a_normalizado = unidecode(clube_a.strip().lower())
    clube_b_normalizado = unidecode(clube_b.strip().lower())

    
    query = (
        select(PartidaModel)
        .options(
            selectinload(PartidaModel.estatisticas_mandante),
            selectinload(PartidaModel.estatisticas_visitante)
        )
        .join(EstatisticasMandanteModel)
        .join(EstatisticasVisitanteModel)
    )

    result = await session.execute(query)
    partidas = result.scalars().all()

    
    partidas_filtradas = []
    for partida in partidas:
        mandante = unidecode(partida.estatisticas_mandante.clube.strip().lower())
        visitante = unidecode(partida.estatisticas_visitante.clube.strip().lower())
        
        if (mandante == clube_a_normalizado and visitante == clube_b_normalizado) or \
           (mandante == clube_b_normalizado and visitante == clube_a_normalizado):
            partidas_filtradas.append(partida)

    
    vitorias_clube_a = 0
    vitorias_clube_b = 0

    for partida in partidas_filtradas:
        if partida.mandante_placar > partida.visitante_placar:
            vencedor = unidecode(partida.estatisticas_mandante.clube.strip().lower())
        elif partida.visitante_placar > partida.mandante_placar:
            vencedor = unidecode(partida.estatisticas_visitante.clube.strip().lower())
        else:
            continue

        if vencedor == clube_a_normalizado:
            vitorias_clube_a += 1
        elif vencedor == clube_b_normalizado:
            vitorias_clube_b += 1

    return {
        "clube_a": clube_a,
        "clube_b": clube_b,
        "vitorias_clube_a": vitorias_clube_a,
        "vitorias_clube_b": vitorias_clube_b
    }

from unidecode import unidecode

@router.get("/vitorias-por-rodada", response_model=List[VitoriasGolsPorRodadaResponse])
async def get_vitorias_gols_por_rodada(
    clube: str = Query(..., description="Nome do clube"),
    session: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    # Normaliza o nome do clube (remove acentos, espaços e converte para minúsculas)
    clube_normalizado = unidecode(clube.strip().lower())

    # Busca todas as partidas do clube (mandante ou visitante)
    query = (
        select(PartidaModel)
        .options(
            selectinload(PartidaModel.estatisticas_mandante),
            selectinload(PartidaModel.estatisticas_visitante)
        )
        .join(EstatisticasMandanteModel)
        .join(EstatisticasVisitanteModel)
        .where(
            or_(
                func.lower(EstatisticasMandanteModel.clube) == clube_normalizado,
                func.lower(EstatisticasVisitanteModel.clube) == clube_normalizado
            )
        )
    )

    result = await session.execute(query)
    partidas = result.scalars().all()

    # Processamento local para calcular vitórias e gols por rodada
    dados_por_rodada = {}
    for partida in partidas:
        rodada = partida.rodada
        mandante_normalizado = unidecode(partida.estatisticas_mandante.clube.strip().lower())
        visitante_normalizado = unidecode(partida.estatisticas_visitante.clube.strip().lower())

        # Verifica se o clube é mandante ou visitante
        if mandante_normalizado == clube_normalizado:
            gols = partida.mandante_placar
            vitoria = 1 if partida.mandante_placar > partida.visitante_placar else 0
        else:
            gols = partida.visitante_placar
            vitoria = 1 if partida.visitante_placar > partida.mandante_placar else 0

        # Atualiza os dados da rodada
        if rodada not in dados_por_rodada:
            dados_por_rodada[rodada] = {"vitorias": 0, "gols": 0}
        dados_por_rodada[rodada]["vitorias"] += vitoria
        dados_por_rodada[rodada]["gols"] += gols

    # Formata a resposta
    resposta = [
        {"rodada": rodada, "vitorias": dados["vitorias"], "gols": dados["gols"]}
        for rodada, dados in sorted(dados_por_rodada.items())
    ]

    return resposta

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


@router.get("/grafico/gols", response_class=StreamingResponse)
async def grafico_gols(session: AsyncSession = Depends(get_db)):
    query = select(
        PartidaModel.data,
        PartidaModel.mandante_placar,
        PartidaModel.visitante_placar
    ).order_by(PartidaModel.data)

    result = await session.execute(query)
    partidas = result.fetchall()

    datas = [partida.data for partida in partidas]
    mandante_gols = [partida.mandante_placar for partida in partidas]
    visitante_gols = [partida.visitante_placar for partida in partidas]

    plt.figure(figsize=(10, 5))
    plt.plot(datas, mandante_gols, label='Mandante Gols')
    plt.plot(datas, visitante_gols, label='Visitante Gols')
    plt.xlabel('Data')
    plt.ylabel('Gols')
    plt.title('Gols por Data')
    plt.legend()
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


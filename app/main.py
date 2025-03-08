# app/main.py
from fastapi import FastAPI, Depends
import pandas as pd
from panel.io.fastapi import add_applications
import panel as pn
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import logging
from contextlib import asynccontextmanager

from yaml import load, FullLoader
import uuid
import uvicorn

from app.logging_utils import setup_logging, log_exceptions_middleware
from app.database_util import Base, engine, get_db, init_db
from app.models import (
    partida_models
)

from app.routes import (
    partida_routes,
    cartoes_routes,
    gols_routes,
    estatisticas_mandante_routes,
    estatisticas_visitante_routes,
    telas_routes,
    tratamento_routes,
)

partida_models.PartidaDTO.resolve_refs()

setup_logging()

configs = load(open("app/configs.yml", "r"), Loader=FullLoader)
SERVER_PORT = configs["configs"]["server"]["port"]
SERVER_HOST = configs["configs"]["server"]["host"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.middleware("http")(log_exceptions_middleware)

app.include_router(partida_routes.router)
app.include_router(cartoes_routes.router)
app.include_router(estatisticas_visitante_routes.router)
app.include_router(estatisticas_mandante_routes.router)
app.include_router(gols_routes.router)
app.include_router(tratamento_routes.router)


@app.get("/")
async def read_root(session: AsyncSession = Depends(get_db)):
    logging.info("Handling request to root endpoint")
    async with session.begin():
        await session.execute(text("CREATE TABLE IF NOT EXISTS teste (id VARCHAR PRIMARY KEY, nome VARCHAR(255))"))
        new_id = str(uuid.uuid4())
        new_id2 = str(uuid.uuid4())
        await session.execute(text("INSERT INTO teste (id, nome) VALUES (:id, :nome)"), {"id": new_id, "nome": "teste"})
        await session.execute(text("INSERT INTO teste (id, nome) VALUES (:id, :nome)"), {"id": new_id2, "nome": "teste2"})
        result = await session.execute(text("SELECT * FROM teste"))
        result = result.fetchall()
        await session.execute(text("DROP TABLE teste"))
        await session.commit()
    logging.info(f"Query result: {result}")
    result_dicts = pd.DataFrame(result).to_dict(orient='records')
    return {"Hello": "World", "resultado de teste de banco de dados": result_dicts}

def create_panel_app():
    slider = pn.widgets.IntSlider(name='Slider', start=0, end=10, value=3)
    return slider.rx() * '⭐'

add_applications({
    "/tela_vitorias_entre_times": telas_routes.telaVitoriasEntreDoisTimes,
    "/tela_vitorias_por_rodadas": telas_routes.telaVitoriasPorRodada,
    "/tela_partida_estatiscas": telas_routes.tela_estatisticas,
    "/tela_grafico_gols": telas_routes.tela_grafico_gols
}, app=app)

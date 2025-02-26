# main.py
import uuid
import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from yaml import load, FullLoader
import logging
from logging_utils import setup_logging, log_exceptions_middleware
from database_util import Base, engine, get_db

from models import partida_models
from models import gol_models
from models import cartoes_models
from models import estatisticas_mandante_models
from models import estatisticas_visitante_models

partida_models.PartidaDTO.resolve_refs()

setup_logging()

configs = load(open("configs.yml", "r"), Loader=FullLoader)
SERVER_PORT = configs["configs"]["server"]["port"]
SERVER_HOST = configs["configs"]["server"]["host"]

app = FastAPI()

app.middleware("http")(log_exceptions_middleware)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root(*, session: Session = Depends(get_db)):
    logging.info("Handling request to root endpoint")
    session.execute(text("CREATE TABLE IF NOT EXISTS teste (id VARCHAR PRIMARY KEY, nome VARCHAR(255))"))
    new_id = str(uuid.uuid4())
    new_id2 = str(uuid.uuid4())
    session.execute(text("INSERT INTO teste (id, nome) VALUES (:id, :nome)"), {"id": new_id, "nome": "teste"})
    session.execute(text("INSERT INTO teste (id, nome) VALUES (:id, :nome)"), {"id": new_id2, "nome": "teste2"})
    result = session.execute(text("SELECT * FROM teste")).all()
    session.execute(text("DROP TABLE teste"))
    session.commit()
    logging.info(f"Query result: {result}")
    result_dicts = [row._mapping for row in result]
    return {"Hello": "World", "result": result_dicts}

@app.get("/partida")
def get_partidas(*, session: Session = Depends(get_db)):
    partida = session.query(partida_models.PartidaModel).limit(1).offset(8000).one()
    partidas_dto = partida_models.PartidaDTO.from_orm(partida)
    return partidas_dto

@app.post("/partida")
def post_partida(*, session: Session = Depends(get_db)):
    new_partida = partida_models.PartidaModel(
        rodada=1,
        data="2025-01-01",
        hora="00:00",
        formacao_mandante="4-4-2",
        formacao_visitante="4-4-2",
        tecnico_mandante="Tite",
        tecnico_visitante="Guardiola",
        arena="Maracanã",
        mandante_placar=1,
        visitante_placar=0,
        mandante_estado="RJ",
        visitante_estado="SP"
    )
    session.add(new_partida)
    session.commit()
    return {"status": "ok"}

@app.get("/gol")
def get_gols(*, session: Session = Depends(get_db)):
    gol = session.query(gol_models.GolModel).limit(1).offset(1000).one()
    gols_dto = gol_models.GolDTO.from_orm(gol)
    return gols_dto

@app.get("/cartao")
def get_cartoes(*, session: Session = Depends(get_db)):
    cartao = session.query(gol_models.GolModel).limit(1).offset(1000).one()
    cartoes_dto = gol_models.GolDTO.from_orm(cartao)
    return cartoes_dto

@app.get("/estatisticas_mandante")
def get_estatisticas_mandantes(*, session: Session = Depends(get_db)):
    estatisticas_mandante = session.query(estatisticas_mandante_models.EstatisticasMandanteModel).limit(1).offset(1000).one()
    estatisticas_mandantes_dto = estatisticas_mandante_models.EstatisticasMandanteDTO.from_orm(estatisticas_mandante)
    return estatisticas_mandantes_dto

@app.get("/estatisticas_visitante")
def get_estatisticas_visitantes(*, session: Session = Depends(get_db)):
    estatisticas_visitante = session.query(estatisticas_visitante_models.EstatisticasVisitanteModel).limit(1).offset(1000).one()
    estatisticas_visitantes_dto = estatisticas_visitante_models.EstatisticasVisitanteDTO.from_orm(estatisticas_visitante)
    return estatisticas_visitantes_dto
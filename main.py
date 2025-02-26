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

partida_models.PartidaDTO.resolve_refs()
gol_models.GolDTO.resolve_refs()

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

@app.get("/partidas")
def get_partidas(*, session: Session = Depends(get_db)):
    logging.info("Handling request to partidas endpoint")
    partidas = session.query(partida_models.PartidaModel).limit(500).offset(4000).all()
    return partidas

if __name__ == "__main__":
    logging.info("Starting FastAPI application")
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True
    )
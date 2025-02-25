from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database_util import Base, engine, get_db

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root(*, session: Session = Depends(get_db)):
    # Executa a query
    result = session.execute(text("SELECT * FROM cartoes OFFSET 0 LIMIT 10")).fetchall()
    # Pega o resultado
    print(result)
    return {"Hello": "World"}
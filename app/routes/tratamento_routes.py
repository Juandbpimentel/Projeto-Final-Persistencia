from io import BytesIO
from zipfile import ZipFile
import asyncio

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.params import Depends
from pandas import DataFrame
from sqlalchemy import create_engine, text
import re

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.database_util import get_db

router = APIRouter(
    prefix="/tratamentos",
    tags=["tratamentos"],
    responses={
        404: {"description": "Não encontrado"},
        200: {"description": "Sucesso"},
        201: {"description": "Criado com sucesso"},
        500: {"description": "Erro interno"},
        400: {"description": "Requisição inválida"},
    },
)

@router.post("/tratar_dados", response_model=dict, status_code=200)
async def tratar_dados(
    cartoes: UploadFile = File(..., media_type="multipart/form-data"),
    estatisticas_full: UploadFile = File(..., media_type="multipart/form-data"),
    full: UploadFile = File(..., media_type="multipart/form-data"),
    gols: UploadFile = File(..., media_type="multipart/form-data")
):
    try:
        cartoes_df = pd.read_csv(cartoes.file)
        estatisticas_full_df = pd.read_csv(estatisticas_full.file)
        full_df = pd.read_csv(full.file)
        gols_df = pd.read_csv(gols.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler os arquivos CSV: {e}")

    trata_e_salva_dados_dos_csvs(cartoes_df, estatisticas_full_df, full_df, gols_df)

    return {"detail": "Dados tratados e salvos com sucesso"}

def trata_e_salva_dados_dos_csvs(cartoes: DataFrame, estatisticas_full: DataFrame, full: DataFrame, gols: DataFrame):
    pd.set_option('display.max_rows', None)

    cartoes = cartoes.rename(columns={'rodata': 'rodada'})
    estatisticas_full = estatisticas_full.rename(columns={'rodata': 'rodada'})
    full = full.rename(columns={
        'ID': 'id',
        'rodata': 'rodada',
        'mandante_Estado': 'mandante_estado',
        'visitante_Estado': 'visitante_estado',
        'mandante_Placar': 'mandante_placar',
        'visitante_Placar': 'visitante_placar',
    })
    gols = gols.rename(columns={'rodata': 'rodada'})

    cartoes[cartoes['atleta'].isna()].index.tolist()

    cartoes[(cartoes['clube'].fillna('') == 'Vitoria') & (cartoes['num_camisa'].fillna(0) == 14)]
    cartoes.loc[[8966], 'atleta'] = 'Lucas Ribeiro'
    cartoes.loc[[8471], 'atleta'] = 'Lucas Ribeiro'

    cartoes[(cartoes['clube'].fillna('') == 'Internacional') & (cartoes['num_camisa'].fillna(0) == 14)]
    cartoes.loc[[12359], 'atleta'] = 'Lucas Ribeiro'
    cartoes.loc[[13106], 'atleta'] = 'Lucas Ribeiro'
    cartoes.loc[[13174], 'atleta'] = 'Lucas Ribeiro'
    cartoes.loc[[13281], 'atleta'] = 'Lucas Ribeiro'

    cartoes[cartoes['atleta'].isna()].index.tolist()

    pos_vazio = cartoes[cartoes["posicao"].isna()]

    def verificar_atleta_duplicado(cartoes_funcao, linhas_com_nan) -> pd.DataFrame:
        resultado_funcao = linhas_com_nan.copy()
        resultado_funcao['atleta_duplicado'] = resultado_funcao['atleta'].apply(
            lambda atleta: (cartoes_funcao['atleta'] == atleta).sum() > 1
        )
        return resultado_funcao

    verificar_atleta_duplicado(cartoes, pos_vazio)

    def preencher_posicao_na_duplicatas(df):
        df_atualizado = df.copy()
        for atleta, group in df_atualizado.groupby('atleta'):
            if group.shape[0] > 1:
                posicoes_validas = group['posicao'].dropna().unique()
                if len(posicoes_validas) > 0:
                    df_atualizado.loc[
                        (df_atualizado['atleta'] == atleta) & (df_atualizado['posicao'].isna()),
                        'posicao'
                    ] = posicoes_validas[0]
        return df_atualizado

    cartoes = preencher_posicao_na_duplicatas(cartoes)

    cartoes['num_camisa'] = cartoes['num_camisa'].fillna(0).astype(int)
    cartoes['posicao'] = cartoes['posicao'].fillna("Indeterminado").astype(str)

    estatisticas_full['posse_de_bola'] = estatisticas_full['posse_de_bola'].str.replace('%', '').fillna(-1).astype(int)
    estatisticas_full['precisao_passes'] = estatisticas_full['precisao_passes'].str.replace('%', '').fillna(-1).astype(
        int)

    estatisticas_full['posse_de_bola'] = estatisticas_full['posse_de_bola'].replace('%', '').fillna(-1).astype(float)
    estatisticas_full['precisao_passes'] = estatisticas_full['precisao_passes'].replace('%', '').fillna(-1).astype(
        float)
    colunas = ["posse_de_bola", "precisao_passes"]
    estatisticas_full[colunas] = estatisticas_full[colunas] / 100

    gols["tipo_de_gol"] = gols["tipo_de_gol"].fillna("Gol Normal").astype(str)

    full['formacao_mandante'] = full['formacao_mandante'].fillna("Sem Informação").astype(str)
    full['formacao_visitante'] = full['formacao_visitante'].fillna("Sem Informação").astype(str)
    full['tecnico_mandante'] = full['tecnico_mandante'].fillna("Sem Informação").astype(str)
    full['tecnico_visitante'] = full['tecnico_visitante'].fillna("Sem Informação").astype(str)
    full["vencedor"] = full["vencedor"].replace("-", "Empate").astype(str)

    def add_sequential_id_column(df, sort_by_columns):
        df = df.sort_values(by=sort_by_columns).reset_index(drop=True)
        df['id'] = df.index + 1
        return df

    cartoes = add_sequential_id_column(cartoes, ['rodada', 'partida_id'])
    gols = add_sequential_id_column(gols, ['rodada', 'partida_id'])

    estatisticas_full['tipo'] = None
    partida_map = full.set_index(['id', 'rodada'])[['mandante', 'visitante', 'vencedor']].to_dict('index')

    for index, row in estatisticas_full.iterrows():
        partida_id = row['partida_id']
        rodada = row['rodada']
        clube = row['clube']
        if (partida_id, rodada) in partida_map:
            if clube == partida_map[(partida_id, rodada)]['mandante']:
                estatisticas_full.at[index, 'tipo'] = 'Mandante'
            elif clube == partida_map[(partida_id, rodada)]['visitante']:
                estatisticas_full.at[index, 'tipo'] = 'Visitante'
            if partida_map[(partida_id, rodada)]['vencedor'] == 'Empate':
                estatisticas_full.at[index, 'vencedor'] = False
            else:
                if clube == partida_map[(partida_id, rodada)]['vencedor']:
                    estatisticas_full.at[index, 'vencedor'] = True
                else:
                    estatisticas_full.at[index, 'vencedor'] = False

    full = full.drop(columns=['mandante', 'visitante', 'vencedor'])

    estatisticas_mandante = estatisticas_full[estatisticas_full['tipo'] == 'Mandante'].drop(columns=['tipo'])
    estatisticas_visitante = estatisticas_full[estatisticas_full['tipo'] == 'Visitante'].drop(columns=['tipo'])

    estatisticas_mandante = add_sequential_id_column(estatisticas_mandante, ['rodada', 'partida_id'])
    estatisticas_visitante = add_sequential_id_column(estatisticas_visitante, ['rodada', 'partida_id'])

    # Save data to the database
    engine = create_engine('postgresql://postgres:postgres@localhost:4002/postgres')

    with engine.connect() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public AUTHORIZATION postgres;"))
        connection.commit()

    cartoes.to_sql('cartoes', engine, if_exists='replace', index=id)
    full.to_sql('partidas', engine, if_exists='replace', index=id)
    gols.to_sql('gols', engine, if_exists='replace', index=id)
    estatisticas_mandante.to_sql('estatisticas_mandantes', engine, if_exists='replace', index=id)
    estatisticas_visitante.to_sql('estatisticas_visitantes', engine, if_exists='replace', index=id)

    # Execute SQL script to create constraints
    try:
        with open("data_mining/CriacaoDeConstraints.sql") as file:
            string = file.read()
    except FileNotFoundError:
        print("Erro: Arquivo SQL não encontrado")
        string = ""
    except IOError:
        print("Erro ao ler o arquivo SQL")
        string = ""

    def remove_comments_and_empty_lines(sql):
        sql = re.sub(r'--.*', '', sql)
        sql = re.sub(r'\n\s*\n', '\n', sql)
        return sql

    if string:
        print("Executando o código SQL para criar as constraints das tabelas")
        string = remove_comments_and_empty_lines(string)
        statements = string.split(';')
        with engine.connect() as connection:
            for statement in statements:
                if statement.strip():
                    connection.execute(text(statement.strip()))
                    connection.commit()
        print("Constraints criadas com sucesso")
    else:
        print("Erro: Conteúdo do arquivo SQL está vazio ou não pôde ser lido")

async def fetch_data(query, session):
    result = await session.execute(query)
    return result.fetchall()

@router.get("/exportar_dados")
async def exportar_dados(
        session: AsyncSession = Depends(get_db)):
    async with session.begin():
        cartoes_query = text("SELECT id,partida_id,rodada,num_camisa,atleta,clube,cartao,minuto FROM cartoes order by id")
        partidas_query = text("SELECT  id, rodada, data, hora, formacao_mandante, formacao_visitante, tecnico_mandante, tecnico_visitante, arena, mandante_placar, visitante_placar, mandante_estado,visitante_estado FROM partidas order by id")
        gols_query = text("SELECT id, partida_id, rodada, clube, atleta, minuto, tipo_de_gol FROM gols order by id")
        estatisticas_mandantes_query = text("SELECT id, partida_id, rodada, clube, chutes, chutes_no_alvo, posse_de_bola, passes, precisao_passes, faltas, cartao_amarelo, cartao_vermelho,impedimentos,escanteios, vencedor FROM estatisticas_mandantes order by id")
        estatisticas_visitantes_query = text("SELECT id, partida_id, rodada, clube, chutes, chutes_no_alvo, posse_de_bola, passes, precisao_passes, faltas, cartao_amarelo, cartao_vermelho,impedimentos,escanteios, vencedor FROM estatisticas_visitantes order by id              ")

        tasks = [
            fetch_data(cartoes_query, session),
            fetch_data(partidas_query, session),
            fetch_data(gols_query, session),
            fetch_data(estatisticas_mandantes_query, session),
            fetch_data(estatisticas_visitantes_query, session)
        ]

        results = await asyncio.gather(*tasks)

        cartoes, partidas, gols, estatisticas_mandantes, estatisticas_visitantes = results

        cartoes_df = pd.DataFrame(cartoes)
        partidas_df = pd.DataFrame(partidas)
        gols_df = pd.DataFrame(gols)
        estatisticas_mandantes_df = pd.DataFrame(estatisticas_mandantes)
        estatisticas_visitantes_df = pd.DataFrame(estatisticas_visitantes)

        buffer = BytesIO()

        with ZipFile(buffer, 'w') as zip_file:
            zip_file.writestr("cartoes.csv", cartoes_df.to_csv(index=False))
            zip_file.writestr("partidas.csv", partidas_df.to_csv(index=False))
            zip_file.writestr("gols.csv", gols_df.to_csv(index=False))
            zip_file.writestr("estatisticas_mandantes.csv", estatisticas_mandantes_df.to_csv(index=False))
            zip_file.writestr("estatisticas_visitantes.csv", estatisticas_visitantes_df.to_csv(index=False))

        buffer.seek(0)

        return StreamingResponse(buffer, media_type="application/x-zip-compressed",
                                 headers={"Content-Disposition": "attachment; filename=exported_data.zip"})
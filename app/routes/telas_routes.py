import aiohttp
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import panel as pn
import io
from PIL import Image

pn.extension()
pn.extension('tabulator')
pn.extension(notifications=True)

def telaVitoriasPorRodada():
    clubeInput = pn.widgets.TextInput(
        name="Nome do Clube",
        value='',
        placeholder='Digite o nome do clube',
        disabled=False
    )

    buttonBuscar = pn.widgets.Button(name='Buscar', button_type='default')

    async def on_buscar():
        try:
            clube = clubeInput.value
            url = f"http://localhost:8000/partidas/vitorias-por-rodada?clube={clube}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.json()
                        df = pd.DataFrame(content)
                        # Plot for Rodada vs Gols
                        fig1, ax1 = plt.subplots(figsize=(10, 5))
                        ax1.bar(df['rodada'], df['gols'], label='Gols', color='yellow')
                        ax1.set_xlabel('Rodada')
                        ax1.set_ylabel('Gols')
                        ax1.set_title('Gols por Rodada')
                        ax1.legend()
                        ax1.grid(True)

                        # Plot for Rodada vs Vitórias
                        fig2, ax2 = plt.subplots(figsize=(10, 5))
                        ax2.bar(df['rodada'], df['vitorias'], label='Vitórias', color='green')
                        ax2.set_xlabel('Rodada')
                        ax2.set_ylabel('Vitórias')
                        ax2.set_title('Vitórias por Rodada')
                        ax2.legend()
                        ax2.grid(True)

                        # Create Panel objects for the plots
                        plot1 = pn.pane.Matplotlib(fig1, tight=True)
                        plot2 = pn.pane.Matplotlib(fig2, tight=True)

                        # Return the plots in a Panel layout
                        return pn.Column(plot1, plot2)
                    else:
                        return pn.pane.Alert('Erro ao buscar dados!', alert_type='danger')
        except Exception as e:
            print(f'Erro: {e}')
            return pn.pane.Alert('Erro ao buscar dados!' + str(e), alert_type='danger')

    async def table_creator_buscar(ins):
        if ins:
            return await on_buscar()

    interactive_table_buscar = pn.bind(lambda ins: asyncio.create_task(table_creator_buscar(ins)), buttonBuscar)

    formulario_de_busca = pn.Column(
        "Buscar Vitórias por Rodada",
        clubeInput,
        buttonBuscar,
        interactive_table_buscar
    ).servable()

    return formulario_de_busca

def tela_estatisticas():
    buttonCarregar = pn.widgets.Button(name='Carregar', button_type='default')

    async def on_carregar():
        try:
            url = f"http://localhost:8000/partidas/estatisticas"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # {
                        #     "media_gols_mandante": 1.5412254610350982,
                        #     "media_gols_visitante": 1.0270077334919692,
                        #     "total_gols_mandante": 12954,
                        #     "total_gols_visitante": 8632
                        # }
                        content = await response.json()
                        data = {
                            "media_gols_mandante": [content["media_gols_mandante"]],
                            "media_gols_visitante": [content["media_gols_visitante"]],
                            "total_gols_mandante": [content["total_gols_mandante"]],
                            "total_gols_visitante": [content["total_gols_visitante"]]
                        }
                        df = pd.DataFrame(data)

                        # Plot for Rodada vs Gols
                        fig1, ax1 = plt.subplots(figsize=(10, 5))
                        ax1.bar('Mandate', df['media_gols_mandante'], label='Media de gols de todas as partidas', color='red')
                        ax1.bar('Visitante', df['media_gols_visitante'], label='Media de gols de todas as partidas', color='black')
                        ax1.set_xlabel('Prioridade dos clubes')
                        ax1.set_ylabel('Media de gols')
                        ax1.set_title('Media de Gols Geral')
                        ax1.legend()
                        ax1.grid(True)

                        # Plot for Rodada vs Gols
                        fig2, ax2 = plt.subplots(figsize=(20, 5))
                        ax2.bar('Mandate', df['total_gols_mandante'], label='Total de gols de todas as partidas', color='red')
                        ax2.bar('Visitante', df['total_gols_visitante'], label='Total de gols de todas as partidas', color='black')
                        ax2.set_xlabel('Prioridade dos clubes')
                        ax2.set_ylabel('Total de gols')
                        ax2.set_title('Total de Gols Geral')
                        ax2.legend()
                        ax2.grid(True)

                        # # Plot for Rodada vs Vitórias
                        # fig2, ax2 = plt.subplots(figsize=(10, 5))
                        # ax2.bar(df['rodada'], df['vitorias'], label='Vitórias', color='green')
                        # ax2.set_xlabel('Rodada')
                        # ax2.set_ylabel('Vitórias')
                        # ax2.set_title('Vitórias por Rodada')
                        # ax2.legend()
                        # ax2.grid(True)

                        # Create Panel objects for the plots
                        plot1 = pn.pane.Matplotlib(fig1, tight=True)
                        plot2 = pn.pane.Matplotlib(fig2, tight=True)

                        # Return the plots in a Panel layout
                        return pn.Column(plot1, plot2)
                    else:
                        return pn.pane.Alert('Erro ao buscar dados!', alert_type='danger')
        except Exception as e:
            print(f'Erro: {e}')
            return pn.pane.Alert('Erro ao buscar dados!' + str(e), alert_type='danger')


    async def table_creator_carregar(ins):
        if ins:
            return await on_carregar()

    interactive_table_buscar = pn.bind(lambda ins: asyncio.create_task(table_creator_carregar(ins)), buttonCarregar)

    formulario_de_estatisticas = pn.Column(
        "Buscar Estatisticas por Mandantes e Visitantes",
        buttonCarregar,
        interactive_table_buscar
    ).servable()

    return formulario_de_estatisticas

def telaVitoriasEntreDoisTimes():
    clube_a_input = pn.widgets.TextInput(
        name="Nome do Clube A",
        value='',
        placeholder='Digite o nome do clube A',
        disabled=False
    )

    clube_b_input = pn.widgets.TextInput(
        name="Nome do Clube B",
        value='',
        placeholder='Digite o nome do clube B',
        disabled=False
    )

    buttonBuscar = pn.widgets.Button(name='Buscar', button_type='default')

    async def on_buscar():
        try:
            clubea = clube_a_input.value
            clubeb = clube_b_input.value
            url = f"http://localhost:8000/partidas/vitorias?clube_a={clubea}&clube_b={clubeb}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.json()
                        data = {
                            "clube_a":  [content["clube_a"]],
                            "clube_b":  [content["clube_b"]],
                            "vitorias_clube_a": [content["vitorias_clube_a"]],
                            "vitorias_clube_b": [content["vitorias_clube_b"]]
                        }
                        df = pd.DataFrame(data)

                        # Plot for Rodada vs Gols
                        fig1, ax1 = plt.subplots(figsize=(10, 5))
                        ax1.bar(df["clube_a"], df['vitorias_clube_a'], label='Total de vitórias do clube a em cima do clube b',
                                color='red')
                        ax1.bar(df["clube_b"], df['vitorias_clube_b'], label='Total de vitórias do clube b em cima do clube a',
                                color='black')
                        ax1.set_xlabel('Clubes')
                        ax1.set_ylabel('Total de Vitórias')
                        ax1.set_title('Total de Partidas Vencidas Pelo Clube Contra O Outro')
                        ax1.legend()
                        ax1.grid(True)

                        # Create Panel objects for the plots
                        plot1 = pn.pane.Matplotlib(fig1, tight=True)

                        # Return the plots in a Panel layout
                        return pn.Column(plot1)
                    else:
                        return pn.pane.Alert('Erro ao buscar dados!', alert_type='danger')
        except Exception as e:
            print(f'Erro: {e}')
            return pn.pane.Alert('Erro ao buscar dados!' + str(e), alert_type='danger')

    async def table_creator_buscar(ins):
        if ins:
            return await on_buscar()

    interactive_table_buscar = pn.bind(lambda ins: asyncio.create_task(table_creator_buscar(ins)), buttonBuscar)

    formulario_de_busca = pn.Column(
        "Buscar Vitórias por Rodada",
        clube_a_input,
        clube_b_input,
        buttonBuscar,
        interactive_table_buscar
    ).servable()

    return formulario_de_busca


def tela_grafico_gols():
    buttonCarregar = pn.widgets.Button(name='Carregar', button_type='default')
    image_pane = pn.pane.Image(width=500, height=500)

    async def on_carregar():
        try:
            url = f"http://localhost:8000/partidas/grafico/gols"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Lê a imagem da resposta
                        image_data = await response.read()
                        image = Image.open(io.BytesIO(image_data))  # Use PIL to open the image
                        # Atualiza o painel de imagem
                        image_pane.object = image
                    else:
                        return pn.pane.Alert('Erro ao buscar dados!', alert_type='danger')
        except Exception as e:
            print(f'Erro: {e}')
            return pn.pane.Alert('Erro ao buscar dados!' + str(e), alert_type='danger')

    async def table_creator_buscar(ins):
        if ins:
            return await on_carregar()

    interactive_table_buscar = pn.bind(lambda ins: asyncio.create_task(table_creator_buscar(ins)), buttonCarregar)
    return pn.Column(buttonCarregar, image_pane, interactive_table_buscar).servable()


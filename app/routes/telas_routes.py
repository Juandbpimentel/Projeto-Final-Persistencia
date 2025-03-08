import aiohttp
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import panel as pn

pn.extension()
pn.extension('tabulator')
pn.extension(notifications=True)

def telaFormularioInserir():
    nomeInserir = pn.widgets.TextInput(
        name="Nome",
        value='',
        placeholder='Digite o titulo',
        disabled=False
    )

    emailInserir = pn.widgets.TextInput(
        name="E-mail",
        value='',
        placeholder='Digite o E-mail',
        disabled=False
    )

    senhaInserir = pn.widgets.TextInput(
        name="Senha",
        value='',
        placeholder='Digite o Senha',
        disabled=False
    )

    localizacaoInserir = pn.widgets.TextInput(
        name="Localização",
        value='',
        placeholder='Digite o Localização',
        disabled=False
    )

    tipoInserir = pn.widgets.RadioBoxGroup(
        name='Tipo de Usuário', options=['Organização', 'Voluntário'])

    buttonInserir = pn.widgets.Button(name='Inserir', button_type='default')

    def on_inserir():
        try:
            # fazer a requisicao
            # with engine.connect() as connection:
            #     tipo = 'organizacao' if tipoInserir.value == 'Organização' else 'voluntario'
            #     stringInsercao = text(
            #         f"INSERT INTO conecta.usuario (nome, email, senha, tipo, localizacao) VALUES ('{nomeInserir.value}', '{emailInserir.value}', '{senhaInserir.value}', '{tipo}','{localizacaoInserir.value}')")
            #     connection.execute(
            #         stringInsercao
            #     )
            #     connection.commit()
                # Limpar os campos
                nomeInserir.value = ''
                emailInserir.value = ''
                senhaInserir.value = ''
                localizacaoInserir.value = ''
                tipoInserir.value = None
                return pn.pane.Alert('Inserido com sucesso!')
        except Exception as e:
            print(f'Erro: {e}')
            return pn.pane.Alert('Erro ao inserir!' + str(e), alert_type='danger')

    def table_creator_inserir(ins):
        if ins:
            return on_inserir()

    interactive_table_inserir = pn.bind(table_creator_inserir, buttonInserir)

    formulario_de_insercao = pn.Column(
        "Formulário de Inserção",
        nomeInserir,
        emailInserir,
        senhaInserir,
        localizacaoInserir,
        tipoInserir,
        # projetosInserir,
        # habilidadesInserir,
        buttonInserir,
        interactive_table_inserir
    ).servable()

    return formulario_de_insercao

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
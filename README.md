# Projeto-Final-Persistencia
Projeto Final de Persistência de usam dados abertos do governo


```markdown


## Como rodar o projeto

Primeiramente, é necessário instalar o Python 3.12. Exemplo de resolução no Windows

```bash
choco install python --version=3.12
```

Depois, instale o pip (já incluído com a instalação do Python 3.12):

```bash
python -m ensurepip --upgrade
```

Instale o virtualenv:

```bash
pip install virtualenv
```

Crie um ambiente virtual:

```bash
python -m virtualenv venv
```

Ative o ambiente virtual:

```bash
.\venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Rode o projeto:

```bash 
python -m fastapi dev .\app\main.py --reload
```
# Mastermind Web Game

Implementação full-stack do clássico jogo de quebra de código **Mastermind**, desenvolvido como case técnico para a vaga de Engenheiro de Software Full-Stack Jr no Itaú.

## Regras do Jogo

- O sistema gera um **código secreto** de 4 cores (de 6 possíveis)
- Cores disponíveis: Vermelho, Azul, Verde, Amarelo, Laranja, Roxo
- Cores **podem se repetir** no código secreto
- O jogador tem **10 tentativas** para adivinhar o código
- Após cada tentativa, o sistema retorna feedback:
  - **Pino preto**: cor certa na posição certa
  - **Pino branco**: cor certa na posição errada
- **Vitória**: 4 pinos pretos | **Derrota**: 10 tentativas sem acertar

## Tech Stack

| Camada    | Tecnologia          | Propósito                     |
|-----------|---------------------|-------------------------------|
| Backend   | Python + FastAPI    | API REST + servidor estático  |
| Frontend  | HTML + CSS + JS     | Interface do jogo (vanilla)   |
| Banco     | SQLite              | Persistência dos dados        |

## Quick Start

### Opção 1: Rodar Localmente (recomendado)

```bash
# Instalar dependências do backend
cd backend
pip install -r requirements.txt

# Iniciar o servidor (também serve o frontend)
uvicorn app.main:app --reload --port 8000
```

Acesse:
- **Jogo**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

### Opção 2: Frontend direto no navegador

O frontend também funciona abrindo `frontend/index.html` diretamente no navegador (com CORS habilitado no backend).

## Testes

```bash
cd backend
python -m pytest app/tests/ -v
```

## API Endpoints

| Método | Rota                      | Descrição                    | Status |
|--------|---------------------------|------------------------------|--------|
| POST   | `/games/`                 | Criar novo jogo              | 201    |
| POST   | `/games/{id}/guesses`     | Enviar tentativa             | 201    |
| GET    | `/games/{id}`             | Consultar estado do jogo     | 200    |
| GET    | `/games/ranking/`         | Ranking de partidas          | 200    |
| GET    | `/health`                 | Health check                 | 200    |
| GET    | `/`                       | Serve o frontend             | 200    |

## Estrutura do Projeto

```
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # Entrada do FastAPI (inclui static files)
│       ├── config.py           # Configurações (SQLite por padrão)
│       ├── database.py         # Conexão com o banco
│       ├── models.py           # Tabelas (Game, Guess)
│       ├── schemas.py          # Validação de dados
│       ├── game_logic.py       # Algoritmo do Mastermind
│       ├── routers/game.py     # Endpoints da API
│       └── tests/              # Testes unitários e de integração
├── frontend/
│   ├── index.html              # Página única (SPA simulada)
│   ├── css/
│   │   └── style.css           # Estilos
│   └── js/
│       ├── api.js              # Chamadas HTTP para o backend
│       └── app.js              # Lógica da interface
└── data/                       # Banco SQLite (criado automaticamente)
```

## Decisões Arquiteturais

- **Stack simplificada**: HTML/CSS/JS puro no frontend (sem frameworks/build)
- **SQLite como padrão**: Não precisa instalar banco de dados separado
- **FastAPI serve tudo**: API + arquivos estáticos em um único processo
- **UUID como ID dos jogos**: Impede que IDs sejam adivinhados por incremento
- **Código secreto oculto**: Só revelado via API quando o jogo termina

## Screenshots

Adicionar screenshots/GIFs do jogo em ação aqui.

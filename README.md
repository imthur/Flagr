# Feature Flags API

API REST para gerenciamento de feature flags com rollout percentual, ativação por usuário e cache Redis.

Construída com **FastAPI**, **SQLite**, **Redis** e **Docker**.

---

## Funcionalidades

- **CRUD completo** — criar, listar, buscar e atualizar feature flags
- **Rollout percentual** — baseado em hash determinístico (o mesmo usuário sempre recebe o mesmo resultado)
- **Ativação por usuário** — habilitar uma flag explicitamente para IDs específicos
- **Cache Redis** — flags em cache por 5 minutos com invalidação automática ao atualizar
- **Endpoint de health check**
- **Swagger UI** gerado automaticamente em `/docs`

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | FastAPI |
| Banco de dados | SQLite (SQLAlchemy ORM) |
| Cache | Redis |
| Containerização | Docker |
| Testes | Pytest + HTTPX |
| Validação | Pydantic v2 |

---

## Rodando com Docker

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/)
- Redis externo (ex: [Upstash](https://upstash.com) — free tier disponível)

### Passo a passo

```bash
# Clone o repositório
git clone https://github.com/imthur/Flagr.git
cd Flagr

# Copie e preencha as variáveis de ambiente
cp .env.example .env

# Sobe a API
docker compose up --build
```

A API estará disponível em `http://localhost:8000`.

Documentação interativa (Swagger UI): `http://localhost:8000/docs`

---

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```env
DATABASE_URL=sqlite:///./flagr.db

REDIS_HOST=seu-endpoint.upstash.io
REDIS_PORT=6379

SECRET_KEY=supersecret
```

> Crie um Redis grátis em [upstash.com](https://upstash.com) e cole o endpoint acima.

---

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Verificação de saúde |
| `POST` | `/flags/` | Criar uma feature flag |
| `GET` | `/flags/` | Listar todas as flags |
| `GET` | `/flags/{nome}` | Buscar flag pelo nome |
| `GET` | `/flags/{nome}/evaluate?user_id=42` | Avaliar flag para um usuário |
| `PUT` | `/flags/{flag_id}` | Atualizar uma flag |

---

## Exemplos de uso

### Criar uma flag com 30% de rollout

```bash
curl -X POST http://localhost:8000/flags/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "novo-checkout",
    "enabled": true,
    "rollout_percentage": 30
  }'
```

### Avaliar para um usuário específico

```bash
curl "http://localhost:8000/flags/novo-checkout/evaluate?user_id=42"
# {"enabled": true}
```

### Habilitar flag apenas para usuários específicos

```bash
curl -X POST http://localhost:8000/flags/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "beta-dashboard",
    "enabled": true,
    "users": [1, 2, 99]
  }'
```

---

## Lógica de avaliação

A avaliação de uma flag para um usuário segue esta ordem de prioridade:

1. Flag desativada → `false`
2. ID do usuário está na lista explícita de `users` → `true`
3. `rollout_percentage` definido → resultado via `hash(user_id + flag_name) % 100 < percentual`
4. Fallback para o estado global (`enabled`)

O hash é baseado em SHA-256, garantindo que o mesmo usuário sempre receba o mesmo resultado para uma flag (rollout fixo/sticky).

---

## Estratégia de cache Redis

- **Chave:** `feature_flag:{nome}`
- **TTL:** 300 segundos (5 minutos)
- **Leitura:** Redis → fallback para banco → armazena no Redis
- **Escrita:** atualiza no banco → invalida a chave no Redis

---

## Rodando os testes

```bash
docker compose exec api pytest
```

---

## Estrutura do projeto

```
.
├── app/
│   ├── core/           # configuração, conexão com banco, segurança
│   ├── models/         # modelos SQLAlchemy
│   ├── schemas/        # schemas Pydantic de request/response
│   ├── repositories/   # queries ao banco (sem lógica de negócio)
│   ├── services/       # lógica de negócio + gerenciamento do cache Redis
│   ├── routers/        # handlers de rota FastAPI
│   ├── utils/          # utilitários (hashing)
│   └── main.py
├── tests/
│   ├── unit/           # testes de hashing e lógica de avaliação
│   └── integration/    # testes de endpoints
├── docker/
│   └── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

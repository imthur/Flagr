# 📘 Development Guide — Feature Flags API (FastAPI + Docker)

## 🎯 Objective

Build a production-ready Feature Flags API using FastAPI, with support for:

* Be totally in Brazilian portuguese
* Global feature toggles
* User-based activation
* Percentage rollout (deterministic)
* Redis caching
* Dockerized environment

---

## 🧱 Tech Stack

* FastAPI
* PostgreSQL
* Redis
* Docker + Docker Compose
* SQLAlchemy (ORM)
* Pydantic (validation)

---

## 📂 Project Structure

```
feature-flags-api/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   │
│   ├── models/
│   │   └── feature_flag.py
│   │
│   ├── schemas/
│   │   └── feature_flag.py
│   │
│   ├── repositories/
│   │   └── feature_flag_repository.py
│   │
│   ├── services/
│   │   └── feature_flag_service.py
│   │
│   ├── routers/
│   │   └── feature_flag_router.py
│   │
│   └── utils/
│       └── hashing.py
│
├── docker/
│   └── Dockerfile
│
├── docker-compose.yml
├── .env
└── README.md
```

---

## ⚙️ Environment Variables (.env)

```
POSTGRES_DB=feature_flags
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

DATABASE_URL=postgresql://postgres:postgres@db:5432/feature_flags

REDIS_HOST=redis
REDIS_PORT=6379

SECRET_KEY=supersecret
```

---

## 🐳 Docker Setup

### docker-compose.yml

Services required:

* api (FastAPI)
* db (PostgreSQL)
* redis

Expose:

* API: 8000
* DB: 5432
* Redis: 6379

---

## 🧠 Domain Model

### FeatureFlag

Fields:

* id (int, pk)
* name (string, unique)
* enabled (boolean)
* rollout_percentage (int, nullable)
* users (JSON array of user_ids, nullable)
* created_at
* updated_at

---

## 🔁 Business Rules

### Evaluation Priority

1. If flag is disabled → return false
2. If user is explicitly listed → return true
3. If rollout_percentage exists:

   * apply deterministic hashing
4. Otherwise → return global enabled

---

## 🧮 Rollout Logic (Deterministic)

Implement:

```
hash(user_id + flag_name) % 100 < rollout_percentage
```

Requirements:

* Same user must always receive same result
* Use stable hash (e.g., hashlib.sha256)

---

## 🚀 API Endpoints

### Create Flag

POST /flags

Body:

```
{
  "name": "new_dashboard",
  "enabled": true,
  "rollout_percentage": 50,
  "users": [1, 2, 3]
}
```

---

### List Flags

GET /flags

---

### Get Flag

GET /flags/{name}

---

### Evaluate Flag

GET /flags/{name}/evaluate?user_id=10

Response:

```
{
  "enabled": true
}
```

---

### Update Flag

PUT /flags/{id}

---

## 🧩 Service Layer Responsibilities

FeatureFlagService must:

* Validate rules
* Handle evaluation logic
* Interact with cache (Redis)
* Fallback to database

---

## ⚡ Redis Strategy

* Key: `feature_flag:{name}`
* Store serialized flag
* TTL: optional (e.g., 5 minutes)

Flow:

1. Try Redis
2. If miss → query DB
3. Save in Redis

---

## 🗄️ Repository Layer

Responsibilities:

* Pure database access
* No business logic

---

## 🧪 Testing Requirements

* Unit tests for:

  * rollout logic
  * evaluation rules

* Integration tests:

  * endpoints
  * database interaction

---

## 🔐 (Optional) Auth

* JWT authentication
* Admin:

  * create/update flags
* Client:

  * evaluate flags

---

## 🧹 Code Standards

* Use dependency injection (FastAPI Depends)
* Separate layers strictly:

  * router → service → repository
* No business logic in routers
* Type hints required

---

## 🚀 Development Phases

### Phase 1 — Base Setup

* FastAPI app
* Docker running
* DB connection

---

### Phase 2 — CRUD

* FeatureFlag model
* Basic endpoints

---

### Phase 3 — Evaluation Logic

* Implement service logic
* Add hashing

---

### Phase 4 — Redis

* Add caching layer

---

### Phase 5 — Tests

* Unit + integration

---

### Phase 6 — Polish

* Logging
* Error handling
* README

---

## 🧠 Constraints for AI (Claude Code)

* Do NOT mix layers
* Do NOT skip validation
* Keep code modular
* Prefer clarity over cleverness
* Always include docstrings

---

## ✅ Expected Outcome

A production-ready API that demonstrates:

* Backend architecture
* Performance optimization
* Real-world problem solving
* Clean code practices

---
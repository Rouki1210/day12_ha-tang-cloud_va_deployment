# Part 6 - Simple Production Agent

Agent FastAPI don gian ket hop cac noi dung chinh cua Day 12:

- API key authentication
- Redis conversation history
- Rate limiting theo API key
- Monthly cost guard
- Health va readiness endpoints
- Structured JSON application logs
- Multi-stage Docker image va non-root user

## Architecture

```text
Client -> FastAPI Agent -> Redis
```

## Run with Docker

```powershell
cd 06-lab-complete
$env:AGENT_API_KEY="dev-secret-key"
docker compose up --build
```

Test:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ready

curl.exe -X POST http://localhost:8000/ask `
  -H "X-API-Key: dev-secret-key" `
  -H "Content-Type: application/json" `
  -d '{"question":"What is Docker?"}'
```

Lay `session_id` tu response va tiep tuc conversation:

```powershell
curl.exe -X POST http://localhost:8000/ask `
  -H "X-API-Key: dev-secret-key" `
  -H "Content-Type: application/json" `
  -d '{"question":"Tell me more","session_id":"SESSION_ID"}'

curl.exe http://localhost:8000/history/SESSION_ID `
  -H "X-API-Key: dev-secret-key"
```

Stop:

```powershell
docker compose down
```

## Run Tests

```powershell
python -m unittest -v test_agent.py
```

## Deploy to Railway

This repository is a monorepo, so the Railway service must use
`/06-lab-complete` as its root directory.

1. Push the repository to GitHub. Do not commit `.env.local`.
2. In Railway, create a project and choose **Deploy from GitHub repo**.
3. Open the application service, then set **Settings > Source > Root Directory**
   to `/06-lab-complete`.
4. On the project canvas, select **+ New > Database > Redis**.
5. In the application service's **Variables** tab, add:

```env
ENVIRONMENT=production
AGENT_API_KEY=replace-with-a-long-random-secret
REDIS_URL=${{Redis.REDIS_URL}}
APP_NAME=Noir AI
APP_VERSION=1.0.0
LLM_MODEL=mock-llm
RATE_LIMIT_PER_MINUTE=10
MONTHLY_BUDGET_USD=10.0
```

The name `Redis` in `${{Redis.REDIS_URL}}` is case-sensitive. Change it if the
database service has a different name. Do not define `PORT`; Railway supplies
that variable automatically.

6. Deploy the staged changes and wait until the `/ready` health check succeeds.
7. Open **Settings > Networking > Public Networking**, then select
   **Generate Domain**.
8. Open the generated domain, enter the same `AGENT_API_KEY` in **Access
   settings**, and send a message.

Verify the deployment:

```powershell
curl.exe https://YOUR-DOMAIN.up.railway.app/health
curl.exe https://YOUR-DOMAIN.up.railway.app/ready

curl.exe -X POST https://YOUR-DOMAIN.up.railway.app/ask `
  -H "X-API-Key: YOUR-AGENT-API-KEY" `
  -H "Content-Type: application/json" `
  -d '{"question":"What is Docker?"}'
```

## API

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | No | Liveness probe |
| GET | `/ready` | No | Redis readiness probe |
| POST | `/ask` | API key | Ask agent and save history |
| GET | `/history/{session_id}` | API key | Read conversation history |
| DELETE | `/history/{session_id}` | API key | Delete conversation history |
| GET | `/metrics` | API key | Rate and budget information |

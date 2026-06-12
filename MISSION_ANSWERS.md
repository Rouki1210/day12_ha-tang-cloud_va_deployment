# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. **Hardcoded API key:** `OPENAI_API_KEY` duoc viet truc tiep trong source code. Neu day code len GitHub, key co the bi lo va bi nguoi khac su dung.
2. **Hardcoded database credentials:** `DATABASE_URL` chua username va password ngay trong code, gay ro ri thong tin truy cap database.
3. **Khong co config management:** `DEBUG` va `MAX_TOKENS` duoc gan co dinh, nen phai sua code khi chuyen giua development, staging va production.
4. **Log thong tin nhay cam:** Chuong trinh in API key ra console. Log production thuong duoc luu lau dai hoac gui den dich vu ben thu ba.
5. **Dung `print()` thay cho logging:** Log khong co level, timestamp, event name va cau truc on dinh de he thong monitoring phan tich.
6. **Khong co health check:** Cloud platform khong co endpoint de kiem tra process con hoat dong va quyet dinh restart container.
7. **Bind vao `localhost`:** Server chi nhan ket noi tu ben trong may hoac container, nen traffic tu ben ngoai container khong truy cap duoc.
8. **Port bi hardcode:** Port `8000` khong doc tu bien moi truong `PORT` do Railway, Render hoac cloud platform cung cap.
9. **Luon bat reload:** `reload=True` phu hop khi phat trien, nhung tang tai nguyen va khong nen dung trong production.
10. **Khong co graceful shutdown:** Ung dung khong co logic startup/shutdown de ngung nhan request, hoan tat request dang xu ly va dong cac ket noi.
11. **Input va giao dien API chua ro rang:** Endpoint develop nhan `question` qua query parameter va khong kiem tra chuoi rong mot cach ro rang.
12. **Khong co readiness check:** Load balancer khong biet ung dung da khoi tao xong va san sang nhan traffic hay chua.

### Exercise 1.2: Basic version observations

- Ung dung co the chay tren may local tai `http://localhost:8000`.
- Endpoint `/` tra ve thong bao agent dang hoat dong.
- Endpoint `/ask` goi duoc mock LLM, nhung phien ban nay chua production-ready.
- Lenh test phu hop voi implementation hien tai:

```bash
curl -X POST "http://localhost:8000/ask?question=Hello"
```

- Khi goi API, terminal in ca noi dung cau hoi, cau tra loi va API key. Day la rui ro bao mat nghiem trong.

### Exercise 1.3: Comparison table

| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Gia tri duoc hardcode trong source code | Doc tu environment variables qua `config.py` | Mot codebase co the dung cho dev, staging va production ma khong can sua code |
| Secrets | API key va database password nam trong code; API key con bi ghi ra log | Secret doc tu environment va khong duoc ghi vao log | Tranh lo secret qua GitHub, source code va he thong log |
| Host | `localhost` | Doc tu `HOST`, mac dinh `0.0.0.0` | `0.0.0.0` cho phep ung dung nhan ket noi tu ben ngoai container |
| Port | Co dinh `8000` | Doc tu bien `PORT` | Cloud platform co the cap port dong cho service |
| Debug/reload | Luon bat `reload=True` | Chi bat khi `DEBUG=true` | Tranh ton tai nguyen va han che hanh vi development trong production |
| Health check | Khong co | Co `GET /health` | Platform co the phat hien instance loi va restart no |
| Readiness check | Khong co | Co `GET /ready` | Load balancer chi gui traffic khi ung dung da san sang |
| Logging | Dung `print()` va log ca secret | Structured JSON logging, khong log secret | De tim kiem, phan tich, canh bao va bao ve thong tin nhay cam |
| Input validation | Nhan query parameter, khong bao loi ro rang khi thieu du lieu | Doc JSON body va tra HTTP 422 khi thieu `question` | API co contract ro rang va client nhan duoc loi phu hop |
| Shutdown | Tat dot ngot | Co FastAPI lifespan va xu ly `SIGTERM` | Cho phep hoan tat request va cleanup tai nguyen truoc khi dung |
| CORS | Khong cau hinh | Chi cho phep origins va methods da cau hinh | Kiem soat frontend nao duoc phep goi API tu trinh duyet |
| Metrics | Khong co | Co `GET /metrics` | Ho tro monitoring uptime, version va environment |

### Checkpoint 1

- [x] Hieu tai sao hardcode secrets la nguy hiem.
- [x] Biet cach dung environment variables de tach config khoi source code.
- [x] Hieu health check giup cloud platform phat hien va restart instance loi.
- [x] Hieu readiness check giup load balancer chi gui traffic den instance da san sang.
- [x] Hieu graceful shutdown giup hoan tat request va dong tai nguyen truoc khi process dung.
- [x] Phan biet `localhost` va `0.0.0.0` khi chay trong container.

### Discussion questions

#### 1. Dieu gi xay ra neu push API key hardcode len GitHub public?

API key co the bi bot hoac nguoi la phat hien va su dung de goi dich vu, lam tang chi phi, truy cap du lieu hoac thuc hien hanh vi trai phep. Xoa key khoi commit moi la chua du vi key van co the ton tai trong Git history. Can thu hoi key cu, tao key moi, xoa secret khoi lich su neu can va chuyen secret sang environment variables hoac secret manager.

#### 2. Tai sao stateless quan trong khi scale?

Khi co nhieu instance, moi instance co memory rieng va request tiep theo cua mot user co the den instance khac. Neu session hoac conversation history chi nam trong memory, du lieu se khong dong nhat va mat khi instance restart. Stateless design luu state trong he thong dung chung nhu Redis hoac database, giup moi instance xu ly request nhu nhau.

#### 3. "Dev/prod parity" co nghia la gi trong thuc te?

Moi truong development va production nen cang giong nhau cang tot ve runtime, dependency, service phu tro va cach deploy. Vi du, ca hai cung chay dung phien ban Python, dependencies duoc khoa phien ban, config deu den tu environment variables va ung dung duoc chay trong Docker. Dieu nay giam loi "it works on my machine" va giup phat hien van de som hon.

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. **Base image:** Ban develop dung `python:3.11`. Day la Python image day du, de su dung nhung co kich thuoc lon hon ban slim.
2. **Working directory:** `WORKDIR /app` dat `/app` lam thu muc lam viec mac dinh ben trong container. Cac lenh `COPY`, `RUN` va `CMD` sau do hoat dong dua tren thu muc nay.
3. **Tai sao copy `requirements.txt` truoc source code:** Docker cache tung layer. Khi source code thay doi nhung dependencies khong doi, layer `pip install` duoc tai su dung, giup build nhanh hon.
4. **`CMD` va `ENTRYPOINT`:** `CMD` cung cap lenh hoac tham so mac dinh va de bi thay the khi chay `docker run`. `ENTRYPOINT` xac dinh executable chinh, con tham so tu `docker run` thuong duoc noi vao sau. Project nay dung `CMD ["python", "app.py"]` de khoi dong agent.

### Exercise 2.2: Basic image and container

Build context phai la project root vi Dockerfile copy ca `02-docker/develop/...` va `utils/mock_llm.py`:

```bash
docker build -f 02-docker/develop/Dockerfile -t agent-develop .
docker run --rm -p 8000:8000 agent-develop
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/ask?question=What%20is%20Docker%3F"
```

Y nghia cua port mapping `-p 8000:8000`: port `8000` tren may host duoc chuyen tiep den port `8000` trong container.

### Exercise 2.3: Multi-stage build

- **Stage 1 - `builder`:** Dung `python:3.11-slim`, cai `gcc` va `libpq-dev`, sau do cai Python dependencies vao `/root/.local`.
- **Stage 2 - `runtime`:** Bat dau tu image `python:3.11-slim` sach, copy dependencies tu builder va chi copy source code can de chay.
- **Tai sao image nho va an toan hon:** Final image khong chua `gcc`, `libpq-dev`, apt cache va cac build artifacts cua stage builder. Ung dung con chay bang non-root user `appuser`.
- **Production features:** Docker health check, `0.0.0.0:8000`, hai Uvicorn workers, `PYTHONPATH`, va non-root user.

Lenh build va so sanh:

```bash
docker build -f 02-docker/production/Dockerfile -t agent-production .
docker images agent-develop agent-production
```

#### Image size comparison

- Develop: chua do tren may hien tai.
- Production: chua do tren may hien tai.
- Ly do: Docker CLI chua duoc cai dat hoac chua co trong `PATH`.
- Muc tieu cua lab: image production nho hon image develop va duoi 500 MB.
- Tai lieu tham khao uoc tinh khoang 800 MB cho develop va 160 MB cho production; day khong phai ket qua build thuc te cua may nay.

### Exercise 2.4: Docker Compose architecture

```text
Client
  |
  v
Nginx :80
  |
  v
Agent :8000
  |             |
  v             v
Redis :6379   Qdrant :6333
```

Bon services duoc khai bao:

1. `nginx`: public entry point, reverse proxy, rate limit va load balancer.
2. `agent`: FastAPI agent; chi nam trong internal network va khong publish port truc tiep.
3. `redis`: session cache va rate-limiting storage, co persistent volume `redis_data`.
4. `qdrant`: vector database cho RAG, co persistent volume `qdrant_data`.

Compose dung DNS noi bo theo service name. Agent ket noi Redis qua `redis://redis:6379/0`, Qdrant qua `http://qdrant:6333`, va Nginx proxy request den `agent:8000`. `depends_on` cho agent doi Redis va Qdrant healthy truoc khi khoi dong.

Truoc khi chay, tao local env file:

```powershell
Copy-Item 02-docker/production/.env.example 02-docker/production/.env.local
docker compose -f 02-docker/production/docker-compose.yml up --build
```

Kiem tra va debug:

```bash
curl http://localhost/health
curl -X POST http://localhost/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain microservices"}'
docker compose -f 02-docker/production/docker-compose.yml ps
docker compose -f 02-docker/production/docker-compose.yml logs agent
docker compose -f 02-docker/production/docker-compose.yml down
```

### Discussion questions

#### 1. Tai sao copy requirements va cai dependencies truoc khi copy code?

De tan dung Docker layer cache. Source code thuong thay doi nhieu hon dependencies, vi vay Docker khong can chay lai `pip install` sau moi thay doi code.

#### 2. `.dockerignore` nen chua gi?

Nen loai bo virtual environments, `.git`, cache Python, IDE files, tests, docs va dac biet la `.env`. `venv/` lam build context rat lon va co the chua binary khong tuong thich voi Linux container. `.env` co the chua API key, password va cac secret khac.

#### 3. Lam sao mount file hoac thu muc vao container?

Dung bind mount:

```bash
docker run --mount type=bind,source=/path/on/host,target=/app/data,readonly agent-production
```

Hoac trong Compose:

```yaml
services:
  agent:
    volumes:
      - ./data:/app/data:ro
```

### Checkpoint 2

- [x] Hieu cac instruction chinh cua Dockerfile.
- [x] Hieu Docker layer cache va build context.
- [x] Hieu loi ich cua multi-stage build va non-root user.
- [x] Doc va mo ta duoc Docker Compose architecture.
- [x] Biet dung `docker logs`, `docker compose logs` va `docker exec` de debug.
- [ ] Build va chay container thuc te; dang bi chan vi Docker CLI chua kha dung.

## Part 4: API Security

### Exercise 4.1: API Key authentication

Ban develop bao ve `POST /ask` bang FastAPI dependency `verify_api_key`. Dependency doc header `X-API-Key` qua `APIKeyHeader` va so sanh voi `AGENT_API_KEY` trong environment.

- Khong gui key: HTTP `401 Unauthorized`.
- Gui key sai: HTTP `403 Forbidden`.
- Gui key dung: request duoc chuyen den agent va tra HTTP `200 OK`.
- `GET /` va `GET /health` la public de client va cloud platform co the kiem tra service.

API key nen duoc rotate bang cach tao key moi trong secret manager/environment, cap nhat client, deploy service voi key moi, sau do thu hoi key cu. Khong ghi key vao source code, log hoac Git history.

Lenh PowerShell:

```powershell
$env:AGENT_API_KEY="my-secret-key"
python app.py

curl.exe -X POST http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d '{"question":"Hello"}'

curl.exe -X POST http://localhost:8000/ask `
  -H "X-API-Key: my-secret-key" `
  -H "Content-Type: application/json" `
  -d '{"question":"Hello"}'
```

### Exercise 4.2: JWT authentication

JWT flow cua ban production:

1. Client gui username/password den `POST /auth/token`.
2. `authenticate_user` kiem tra credentials.
3. `create_token` tao JWT ky bang `HS256`, chua `sub`, `role`, `iat` va `exp`.
4. Client gui `Authorization: Bearer <token>` khi goi endpoint duoc bao ve.
5. `verify_token` kiem tra chu ky va thoi han, sau do tra username va role cho endpoint.

Token het han sau 60 phut. Token thieu hoac het han tra `401`; token khong hop le tra `403`. User thuong co role `user`, con teacher co role `admin` va duoc truy cap `/admin/stats`.

```powershell
$login = Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/auth/token `
  -ContentType "application/json" `
  -Body '{"username":"student","password":"demo123"}'

$token = $login.access_token

Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/ask `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"question":"Explain JWT"}'
```

Luu y production: `JWT_SECRET` bat buoc phai la secret manh lay tu environment/secret manager. Demo users va plain-text passwords trong `auth.py` chi phu hop cho bai lab; he thong that can database va password hashing.

### Exercise 4.3: Rate limiting

`rate_limiter.py` dung **sliding window log**: moi user co mot `deque` luu timestamp request. Moi lan check, timestamp cu hon 60 giay bi xoa; neu so request trong window da dat limit thi API tra `429` va cac header rate-limit.

- User: 10 requests/60 giay.
- Admin: 100 requests/60 giay.
- Admin khong bypass hoan toan; admin co quota cao hon.
- Request thu 11 cua user trong cung window tra `429 Too Many Requests`.
- Response `429` co `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining` va `X-RateLimit-Reset`.

Implementation hien tai luu counter trong memory. Khi scale nhieu process/instance, moi process co counter rieng, vi vay production that can chuyen state sang Redis.

### Exercise 4.4: Cost guard

Cost guard hien tai thuc hien:

1. Lay usage record cua user trong ngay hien tai.
2. Chan toan service bang HTTP `503` neu global daily cost dat `$10`.
3. Chan user bang HTTP `402` neu personal daily cost dat `$1`.
4. Ghi warning khi user dat 80% budget.
5. Sau moi LLM call, ghi input tokens, output tokens, request count va estimated cost.
6. Reset user record khi ngay thay doi.

Gia token demo:

- Input: `$0.00015/1K tokens`.
- Output: `$0.0006/1K tokens`.

Da sua response `/ask` de `budget_remaining_usd` tra dung `$1 - cost da dung`, thay vi tra cost da dung.

Day la implementation demo in-memory theo ngay. Yeu cau final project `$10/thang/user` can luu tong chi phi theo key dang `budget:{user_id}:{YYYY-MM}` trong Redis, dung thao tac atomic de tranh race condition, va dat TTL de cleanup du lieu cu.

### Exercise 4.1-4.4: Test results

Da them `04-api-gateway/production/test_advanced.py` va chay:

```bash
python -m unittest -v test_advanced.py
```

Ket qua: **8 tests passed**.

| Test | Expected | Result |
|------|----------|--------|
| Missing JWT | 401 | Passed |
| Invalid credentials | 401 | Passed |
| Invalid JWT | 403 | Passed |
| Empty question | 422 | Passed |
| Valid authenticated request | 200 | Passed |
| Request 11 trong 60 giay | 429 | Passed |
| Student truy cap admin endpoint | 403 | Passed |
| Teacher truy cap admin endpoint | 200 | Passed |
| User vuot cost budget | 402 | Passed |

### Discussion questions

#### 1. Khi nao dung API Key, JWT hay OAuth2?

- API Key: internal service, script, server-to-server hoac MVP don gian.
- JWT: ung dung co login, nhieu user, role va authorization stateless.
- OAuth2/OIDC: dang nhap qua Google/Microsoft/GitHub, third-party authorization, SSO hoac he thong can identity provider chuyen nghiep.

#### 2. Nen dat rate limit bao nhieu cho AI agent?

Khong co mot con so dung cho moi he thong. Can dua tren latency, model cost, user tier va workload. `10 req/min` phu hop cho lab va free tier; paid user co the co quota cao hon. Nen co them concurrent-request limit, token limit va global budget guard.

#### 3. Xu ly the nao khi API key bi lo?

Thu hoi va rotate key ngay, kiem tra logs/usage de xac dinh pham vi anh huong, block traffic bat thuong, thong bao cac ben lien quan, va tao key moi qua secret manager. Sau do xoa secret khoi code va Git history neu da commit, nhung van phai coi key cu la da bi compromise.

### Checkpoint 4

- [x] Hieu va test API Key authentication.
- [x] Hieu JWT issue/verify flow va role-based access.
- [x] Hieu sliding-window rate limiting.
- [x] Test rate limit `429` sau 10 requests.
- [x] Hieu cost guard, per-user budget va global budget.
- [x] Test cost guard tra `402` khi user vuot budget.
- [x] Bo sung automated test suite; 8 tests passed.
- [ ] Chuyen rate limiter va monthly cost guard sang Redis; day la yeu cau cua final project.

## Part 5: Scaling & Reliability

### Exercise 5.1: Health and readiness checks

Ban develop cung cap hai probe rieng biet:

- `GET /health`: liveness probe, tra status, uptime, version, environment va memory check. Platform co the restart container neu endpoint nay timeout hoac tra non-200.
- `GET /ready`: readiness probe, tra `200` khi `_is_ready=True` va `503` trong luc startup/shutdown. Load balancer dung endpoint nay de dung route traffic den instance chua san sang.

Ban production kiem tra them Redis. Da sua `/ready` de tra `503` khi Redis khong kha dung hoac ung dung dang fallback sang in-memory, vi instance in-memory khong con dat yeu cau stateless.

### Exercise 5.2: Graceful shutdown

Ban develop dung FastAPI lifespan va middleware `_in_flight_requests`:

1. Startup load dependencies va dat `_is_ready=True`.
2. Middleware tang counter khi request bat dau va giam trong `finally` khi request ket thuc.
3. Khi nhan SIGTERM, Uvicorn ngung nhan traffic moi va chay lifespan shutdown.
4. `_is_ready=False`, sau do app cho request dang chay hoan thanh, toi da 30 giay.
5. Uvicorn dong process sau khi application shutdown hoan tat.

Da kiem tra bang `docker stop production-agent-2`. Log thuc te:

```text
Shutting down
Waiting for application shutdown
Instance instance-4263a9 shutting down
Application shutdown complete
Finished server process [1]
```

### Exercise 5.3: Stateless design with Redis

Stateful design luu conversation history trong RAM cua tung process, nen request tiep theo co the mat history neu Nginx route sang instance khac. Ban production luu session trong Redis bang key `session:{session_id}`.

Flow cua `POST /chat`:

1. Tao UUID neu client chua gui `session_id`.
2. Doc session JSON tu Redis.
3. Them user message vao history.
4. Goi mock LLM.
5. Them assistant message va ghi session lai Redis bang `SETEX`.
6. Dat TTL 3600 giay va chi giu 20 messages moi nhat.

Da sua loi dem turn: request dau tien bay gio tra `turn=1`, request thu hai tra `turn=2`. Input `question` duoc validate tu 1 den 1000 ky tu.

### Exercise 5.4: Load balancing

Docker Compose chay Redis, Nginx va ba agent replicas. Agent khong publish port ra host; client chi truy cap Nginx tai `localhost:8080`. Docker DNS resolve service `agent` thanh cac replica va Nginx phan phoi request round-robin.

```text
Client -> Nginx :8080 -> Agent 1 --+
                       Agent 2 ----+-> Redis :6379
                       Agent 3 --+
```

Da xoa dependency `.env.local` khong can thiet va field Compose `version` da loi thoi. `docker compose config --quiet` passed.

Lenh da chay:

```bash
docker compose build agent
docker compose up --scale agent=3 -d
docker compose ps
python test_stateless.py
```

Ket qua ba agent, Redis va Nginx deu healthy. Image `production-agent` co disk usage 244 MB va content size 58.1 MB.

### Exercise 5.5: Stateless and failure tests

Da them `production/test_app.py` va chay:

```bash
python -m unittest -v test_app.py
```

Ket qua: **8 tests passed**.

| Test | Result |
|------|--------|
| Health va readiness khi Redis hoat dong | Passed |
| Readiness tra 503 khi khong dung Redis | Passed |
| Readiness tra 503 khi Redis disconnect | Passed |
| Multi-turn session va turn number | Passed |
| Session duoc serialize vao shared store | Passed |
| Delete session va 404 sau khi xoa | Passed |
| Empty question tra 422 | Passed |
| History chi giu 20 messages | Passed |

Integration test qua Nginx gui nam request cua cung mot session den ba instance:

```text
Instances used: instance-4263a9, instance-593c85, instance-5860fa
Total messages in Redis history: 10
```

Sau do da dung `production-agent-2` va chay lai. Nam request van thanh cong qua hai instance con lai, history van co 10 messages. Dieu nay chung minh load balancing va shared Redis state tiep tuc hoat dong khi mot agent bi dung.

### Checkpoint 5

- [x] Hieu va kiem tra liveness/readiness probes.
- [x] Xac minh graceful container shutdown qua log.
- [x] Luu session va conversation history trong Redis.
- [x] Chay ba agent replicas sau Nginx.
- [x] Xac minh request duoc phan phoi qua ba instance.
- [x] Xac minh history duoc bao toan qua Redis.
- [x] Dung mot agent va xac minh service van hoat dong.
- [x] Automated tests: 8 passed.

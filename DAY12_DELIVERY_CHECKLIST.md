#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** _________________________  
> **Student ID:** _________________________  
> **Date:** _________________________

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key va database credentials bi hardcode trong source code.
2. API key bi in ra log, co nguy co ro ri secret.
3. Config nhu `DEBUG`, `MAX_TOKENS` va port duoc gan co dinh.
4. Dung `print()` thay cho structured logging.
5. Khong co health check va readiness check.
6. Server bind vao `localhost`, nen khong nhan traffic tu ben ngoai container.
7. Port `8000` khong doc tu environment variable `PORT`.
8. `reload=True` luon duoc bat, khong phu hop production.
9. Khong co lifecycle management va graceful shutdown.
10. Input validation va API contract chua ro rang.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Hardcode trong source code | Doc tu environment variables qua `config.py` | Dung cung mot codebase cho nhieu moi truong |
| Secrets | Nam trong code va bi ghi ra log | Doc tu environment, khong log secret | Tranh lo secret va bi su dung trai phep |
| Host | `localhost` | `0.0.0.0` | Cho phep traffic tu ben ngoai container truy cap |
| Port | Co dinh `8000` | Doc tu `PORT` | Tuong thich voi port do cloud platform cap |
| Health check | Khong co | Co `GET /health` | Cloud phat hien va restart instance loi |
| Readiness check | Khong co | Co `GET /ready` | Chi nhan traffic khi ung dung da san sang |
| Logging | `print()`, co log secret | Structured JSON logging | De monitoring va bao ve thong tin nhay cam |
| Shutdown | Tat dot ngot | Lifespan va xu ly `SIGTERM` | Hoan tat request va cleanup truoc khi dung |
| Debug/reload | Luon bat | Chi bat khi `DEBUG=true` | Tranh hanh vi development trong production |

### Part 1 completion
- [x] Identified development anti-patterns.
- [x] Compared the develop and production implementations.
- [x] Understood environment-based configuration.
- [x] Understood health checks, readiness checks and graceful shutdown.
- [x] Full explanations are recorded in `MISSION_ANSWERS.md`.

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: Develop dung `python:3.11`; production dung `python:3.11-slim` cho ca builder va runtime.
2. Working directory: `/app`.
3. Copy `requirements.txt` truoc de Docker tai su dung layer cai dependencies khi chi source code thay doi.
4. `CMD` la lenh/tham so mac dinh de thay the; `ENTRYPOINT` la executable chinh cua container.

### Exercise 2.3: Image size comparison
- Develop: chua do vi Docker CLI chua kha dung tren may.
- Production: chua do vi Docker CLI chua kha dung tren may.
- Difference: se cap nhat sau khi chay `docker images agent-develop agent-production`.
- Multi-stage analysis and Compose architecture: completed in `MISSION_ANSWERS.md`.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- Added `04-api-gateway/production/test_advanced.py`.
- Command: `python -m unittest -v test_advanced.py`.
- Result: 8 tests passed.
- Verified: 401 missing auth, 401 invalid credentials, 403 invalid token,
  422 invalid input, 200 valid request, 429 rate limit, role-based admin
  access, and 402 cost limit.

### Exercise 4.4: Cost guard implementation
- Tracks daily input/output tokens and estimated cost per user.
- Returns 402 when a user reaches the $1 daily demo budget.
- Returns 503 when the service reaches the $10 global daily budget.
- Logs a warning at 80% usage and resets records on a new day.
- Current Part 4 demo is in-memory; the final project must use Redis and a
  $10 monthly per-user budget.
- Full explanation and PowerShell test commands are in `MISSION_ANSWERS.md`.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- Implemented liveness `/health` and readiness `/ready` behavior.
- Readiness now returns 503 whenever Redis is unavailable or the app falls
  back to non-scalable in-memory storage.
- Verified graceful shutdown through Docker logs after stopping one agent.
- Fixed conversation turn numbering and added question validation.
- Added `05-scaling-reliability/production/test_app.py`: 8 tests passed.
- Built `production-agent`: 244 MB disk usage, 58.1 MB content size.
- Started Redis, Nginx and 3 healthy agent replicas with Docker Compose.
- Stateless integration test used all 3 instances and preserved 10 messages.
- Stopped one agent and verified all requests still succeeded through the
  remaining 2 instances with history preserved in Redis.
- Full commands and explanations are recorded in `MISSION_ANSWERS.md`.
```

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

```markdown
# Deployment Information

## Public URL
https://your-agent.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
```

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **

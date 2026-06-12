import json
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

from fastapi import HTTPException

from app.config import settings


class Storage:
    def __init__(self):
        self.redis = None
        self.backend = "memory"
        self.histories: dict[str, list[dict]] = {}
        self.rate_windows: dict[str, deque] = defaultdict(deque)
        self.budgets: dict[str, float] = defaultdict(float)

        if settings.redis_url:
            try:
                import redis

                client = redis.from_url(settings.redis_url, decode_responses=True)
                client.ping()
                self.redis = client
                self.backend = "redis"
            except Exception:
                if settings.environment == "production":
                    raise

    def ping(self) -> bool:
        if not self.redis:
            return settings.environment != "production"
        try:
            return bool(self.redis.ping())
        except Exception:
            return False

    def _history_key(self, session_id: str) -> str:
        return f"history:{session_id}"

    def get_history(self, session_id: str) -> list[dict]:
        key = self._history_key(session_id)
        if self.redis:
            value = self.redis.get(key)
            return json.loads(value) if value else []
        return self.histories.get(key, [])

    def append_message(self, session_id: str, role: str, content: str) -> list[dict]:
        history = self.get_history(session_id)
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        history = history[-20:]
        key = self._history_key(session_id)
        if self.redis:
            self.redis.setex(key, 3600, json.dumps(history))
        else:
            self.histories[key] = history
        return history

    def delete_history(self, session_id: str) -> None:
        key = self._history_key(session_id)
        if self.redis:
            self.redis.delete(key)
        else:
            self.histories.pop(key, None)

    def check_rate_limit(self, user_id: str, limit: int) -> None:
        now = time.time()
        key = f"rate:{user_id}:{int(now // 60)}"
        if self.redis:
            count = self.redis.incr(key)
            if count == 1:
                self.redis.expire(key, 60)
        else:
            window = self.rate_windows[user_id]
            while window and window[0] <= now - 60:
                window.popleft()
            window.append(now)
            count = len(window)

        if count > limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {limit} requests/minute",
                headers={"Retry-After": "60"},
            )

    def _budget_key(self, user_id: str) -> str:
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        return f"budget:{user_id}:{month}"

    def get_monthly_cost(self, user_id: str) -> float:
        key = self._budget_key(user_id)
        if self.redis:
            return round(float(self.redis.get(key) or 0), 6)
        return round(self.budgets[key], 6)

    def check_and_record_budget(self, user_id: str, cost: float, limit: float) -> None:
        current = self.get_monthly_cost(user_id)
        if current + cost > limit:
            raise HTTPException(status_code=402, detail="Monthly budget exceeded")

        key = self._budget_key(user_id)
        if self.redis:
            self.redis.incrbyfloat(key, cost)
            self.redis.expire(key, 32 * 24 * 3600)
        else:
            self.budgets[key] += cost


storage = Storage()

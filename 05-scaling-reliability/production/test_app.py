import json
import unittest

from fastapi.testclient import TestClient

import app as app_module


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.available = True

    def ping(self):
        if not self.available:
            raise ConnectionError("Redis unavailable")
        return True

    def setex(self, key, ttl_seconds, value):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key)

    def delete(self, key):
        self.values.pop(key, None)


class StatelessAgentTests(unittest.TestCase):
    def setUp(self):
        self.original_redis = app_module._redis
        self.original_use_redis = app_module.USE_REDIS
        self.redis = FakeRedis()
        app_module._redis = self.redis
        app_module.USE_REDIS = True
        self.client = TestClient(app_module.app)

    def tearDown(self):
        app_module._redis = self.original_redis
        app_module.USE_REDIS = self.original_use_redis

    def test_health_and_readiness_with_redis(self):
        health = self.client.get("/health")
        ready = self.client.get("/ready")

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")
        self.assertEqual(health.json()["storage"], "redis")
        self.assertEqual(ready.status_code, 200)

    def test_readiness_fails_without_redis(self):
        app_module.USE_REDIS = False
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 503)

    def test_readiness_fails_when_redis_disconnects(self):
        self.redis.available = False
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 503)

    def test_multi_turn_history_and_turn_numbers(self):
        first = self.client.post("/chat", json={"question": "What is Docker?"})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["turn"], 1)
        self.assertEqual(first.json()["storage"], "redis")

        session_id = first.json()["session_id"]
        second = self.client.post(
            "/chat",
            json={"question": "Tell me more", "session_id": session_id},
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["turn"], 2)

        history = self.client.get(f"/chat/{session_id}/history")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.json()["count"], 4)
        self.assertEqual(
            [message["role"] for message in history.json()["messages"]],
            ["user", "assistant", "user", "assistant"],
        )

    def test_session_is_serialized_in_shared_store(self):
        response = self.client.post("/chat", json={"question": "Hello"})
        session_id = response.json()["session_id"]
        stored = json.loads(self.redis.values[f"session:{session_id}"])
        self.assertEqual(len(stored["history"]), 2)

    def test_delete_session(self):
        created = self.client.post("/chat", json={"question": "Hello"})
        session_id = created.json()["session_id"]

        deleted = self.client.delete(f"/chat/{session_id}")
        missing = self.client.get(f"/chat/{session_id}/history")

        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(missing.status_code, 404)

    def test_question_validation(self):
        response = self.client.post("/chat", json={"question": ""})
        self.assertEqual(response.status_code, 422)

    def test_history_keeps_only_twenty_messages(self):
        session_id = "bounded-history"
        for index in range(12):
            response = self.client.post(
                "/chat",
                json={"question": f"Question {index}", "session_id": session_id},
            )
            self.assertEqual(response.status_code, 200)

        history = self.client.get(f"/chat/{session_id}/history")
        self.assertEqual(history.json()["count"], 20)


if __name__ == "__main__":
    unittest.main()

import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.storage import storage


class SimpleAgentTests(unittest.TestCase):
    def setUp(self):
        storage.histories.clear()
        storage.rate_windows.clear()
        storage.budgets.clear()
        self.client = TestClient(app)
        self.headers = {"X-API-Key": "dev-secret-key"}

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_authentication_required(self):
        response = self.client.post("/ask", json={"question": "Hello"})
        self.assertEqual(response.status_code, 401)

    def test_ask_and_history(self):
        first = self.client.post(
            "/ask", headers=self.headers, json={"question": "What is Docker?"}
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["turn"], 1)

        session_id = first.json()["session_id"]
        second = self.client.post(
            "/ask",
            headers=self.headers,
            json={"question": "Tell me more", "session_id": session_id},
        )
        self.assertEqual(second.json()["turn"], 2)

        history = self.client.get(f"/history/{session_id}", headers=self.headers)
        self.assertEqual(len(history.json()["messages"]), 4)

    def test_empty_question_is_rejected(self):
        response = self.client.post(
            "/ask", headers=self.headers, json={"question": ""}
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()

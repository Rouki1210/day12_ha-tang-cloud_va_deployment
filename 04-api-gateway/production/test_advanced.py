import unittest

from fastapi.testclient import TestClient

from app import app
from cost_guard import cost_guard
from rate_limiter import rate_limiter_admin, rate_limiter_user


class SecurityStackTests(unittest.TestCase):
    def setUp(self):
        rate_limiter_user._windows.clear()
        rate_limiter_admin._windows.clear()
        cost_guard._records.clear()
        cost_guard._global_cost = 0.0
        self.client = TestClient(app)

    def login(self, username="student", password="demo123"):
        response = self.client.post(
            "/auth/token",
            json={"username": username, "password": password},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def auth_headers(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_missing_token_returns_401(self):
        response = self.client.post("/ask", json={"question": "hello"})
        self.assertEqual(response.status_code, 401)

    def test_invalid_credentials_return_401(self):
        response = self.client.post(
            "/auth/token",
            json={"username": "student", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_returns_403(self):
        response = self.client.post(
            "/ask",
            headers=self.auth_headers("not-a-valid-token"),
            json={"question": "hello"},
        )
        self.assertEqual(response.status_code, 403)

    def test_question_validation_returns_422(self):
        token = self.login()
        response = self.client.post(
            "/ask",
            headers=self.auth_headers(token),
            json={"question": ""},
        )
        self.assertEqual(response.status_code, 422)

    def test_authenticated_request_records_usage(self):
        token = self.login()
        response = self.client.post(
            "/ask",
            headers=self.auth_headers(token),
            json={"question": "What is API security?"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["usage"]["requests_remaining"], 9)
        self.assertGreater(response.json()["usage"]["budget_remaining_usd"], 0)

        usage = self.client.get("/me/usage", headers=self.auth_headers(token))
        self.assertEqual(usage.status_code, 200)
        self.assertEqual(usage.json()["requests"], 1)

    def test_user_rate_limit_returns_429_after_ten_requests(self):
        token = self.login()
        headers = self.auth_headers(token)
        for request_number in range(10):
            response = self.client.post(
                "/ask",
                headers=headers,
                json={"question": f"request {request_number}"},
            )
            self.assertEqual(response.status_code, 200)

        blocked = self.client.post(
            "/ask",
            headers=headers,
            json={"question": "request 11"},
        )
        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(blocked.headers["x-ratelimit-remaining"], "0")

    def test_admin_endpoint_requires_admin_role(self):
        student_token = self.login()
        forbidden = self.client.get(
            "/admin/stats", headers=self.auth_headers(student_token)
        )
        self.assertEqual(forbidden.status_code, 403)

        teacher_token = self.login("teacher", "teach456")
        allowed = self.client.get(
            "/admin/stats", headers=self.auth_headers(teacher_token)
        )
        self.assertEqual(allowed.status_code, 200)

    def test_cost_guard_returns_402_when_user_budget_is_exhausted(self):
        record = cost_guard._get_record("student")
        record.input_tokens = 10_000_000

        token = self.login()
        response = self.client.post(
            "/ask",
            headers=self.auth_headers(token),
            json={"question": "hello"},
        )
        self.assertEqual(response.status_code, 402)


if __name__ == "__main__":
    unittest.main()

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Simple AI Agent"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    agent_api_key: str = field(default_factory=lambda: os.getenv("AGENT_API_KEY", "dev-secret-key"))
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "mock-llm"))
    rate_limit_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    )
    monthly_budget_usd: float = field(
        default_factory=lambda: float(os.getenv("MONTHLY_BUDGET_USD", "10.0"))
    )
    allowed_origins: list[str] = field(
        default_factory=lambda: os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:8000,null",
        ).split(",")
    )

    def validate(self):
        if self.environment == "production" and self.agent_api_key == "dev-secret-key":
            raise ValueError("AGENT_API_KEY must be changed in production")
        return self


settings = Settings().validate()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./pactai.db"

    GROQ_API_KEY: str = ""

    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = ""

    # This field was missing entirely — it's what QwenLLM (app/llm/qwen.py) reads via
    # settings.QWEN_MODEL. Its absence is the actual root cause of the earlier
    # "extra_forbidden: qwen_model" crash: your .env had a QWEN_MODEL value with
    # nowhere declared to receive it.
    QWEN_MODEL: str = "qwen-plus"

    QWEN_THINKING_MODEL: str = "qwen3.7-max"


settings = Settings()
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:Ayh2GXsFqMCLL5GazLJAe_LIZiWQbvqsiS6QgTf7_Fw@127.0.0.1:15433/sparkdocs"
    test_database_url: str = "sqlite+aiosqlite:///./test.db"
    spark_dms_url: str = "http://127.0.0.1:8002"
    spark_temporal_cli: str = "docker exec spark-workflow-temporal-admin-tools-1 temporal"
    spark_temporal_ui_url: str = "http://127.0.0.1:8080"
    litellm_url: str = "http://127.0.0.1:4000"
    litellm_api_key: str = "y9Y7BYhbm6IkUFX0pnqsIGD6e-pGN1NF9HxPzw8dc_Q"
    litellm_model: str = "gpt-oss-120b"
    litellm_embedding_model: str = "BAAI/bge-m3"
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_collection: str = "data_ollama"

    model_config = {"env_prefix": "SPARK_DOCS_"}


settings = Settings()

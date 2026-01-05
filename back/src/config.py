from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://tastify:tastify@localhost:5432/tastify"
    
    # Game settings
    round_duration_seconds: int = 30
    min_target_number: int = 1
    max_target_number: int = 100
    
    # Job settings
    game_timer_job_interval: float = 1.0
    room_cleanup_job_interval: float = 3600.0  # Run every hour
    room_inactivity_threshold_hours: int = 24  # Close rooms inactive for 24 hours
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


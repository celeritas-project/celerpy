from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "celerpy"
    debug: bool = False

import os
from typing import Optional
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class Environment:
    bot_token: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    test_guild: Optional[str]

    @staticmethod
    def load() -> "Environment":
        load_dotenv()
        return Environment(
            bot_token=os.environ["BOT_TOKEN"],
            db_user=os.environ["DB_USER"],
            db_password=os.environ["DB_PASSWORD"],
            db_host=os.environ.get("DB_HOST", "localhost"),
            db_port=os.environ.get("DB_PORT", "5432"),
            db_name=os.environ["DB_NAME"],
            test_guild=os.environ.get("TEST_GUILD"),
        )

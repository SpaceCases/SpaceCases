import os
from typing import Optional
from dotenv import load_dotenv
from dataclasses import dataclass

DEFAULT_ASSET_DOMAIN = "https://assets.spacecases.xyz"


@dataclass
class Environment:
    bot_token: str
    owner_id: int
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    test_guild: Optional[str]
    asset_domain: str

    @staticmethod
    def load() -> "Environment":
        load_dotenv(override=True)
        return Environment(
            bot_token=os.environ["BOT_TOKEN"],
            owner_id=int(os.environ["OWNER_ID"]),
            db_user=os.environ["DB_USER"],
            db_password=os.environ["DB_PASSWORD"],
            db_host=os.environ.get("DB_HOST", "localhost"),
            db_port=os.environ.get("DB_PORT", "5432"),
            db_name=os.environ["DB_NAME"],
            test_guild=os.environ.get("TEST_GUILD"),
            asset_domain=os.environ.get("ASSET_DOMAIN", DEFAULT_ASSET_DOMAIN),
        )


environment = Environment.load()

import asyncio
from src.database import Database
from src.bot import SpaceCasesBot
from src.environment import Environment


async def main():
    environment = Environment.load()
    async with await Database.create(
        environment.db_user,
        environment.db_password,
        environment.db_name,
        environment.db_host,
        environment.db_port,
    ) as db:
        bot = SpaceCasesBot(db, environment.test_guild)
        try:
            await bot.start(environment.bot_token)
        finally:
            await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

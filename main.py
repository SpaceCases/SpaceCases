import asyncio
from contextlib import suppress
from src.database import Database
from src.bot import SpaceCasesBot
from src.environment import environment


async def main():
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
    with suppress(KeyboardInterrupt):
        asyncio.run(main())

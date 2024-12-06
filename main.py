import os
import glob
import asyncio
from src.database import Database
from src.bot import SpaceCasesBot
from src.logger import logger
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
        logger.info("Running sql init queries")
        sql_init_queries = glob.glob(os.path.join("src", "sql", "init", "*.sql"))
        for sql_file_path in sql_init_queries:
            sql_file_name = os.path.basename(sql_file_path)
            await db.execute_from_file(os.path.join("init", sql_file_name))
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

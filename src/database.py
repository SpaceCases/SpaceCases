import os
import asyncpg
from src.logger import logger

INIT_SCRIPTS_DIRECTORY = os.path.join("src", "sql", "init")
SQL_QUERIES_DIRECTORY = os.path.join("src", "sql")


class Database:
    @classmethod
    async def create(
        self, user: str, password: str, database: str, host: str, port: str
    ) -> "Database":
        pool = await asyncpg.create_pool(
            user=user, password=password, database=database, host=host, port=port
        )
        logger.info(f"Connected to database '{database}' as user '{user}'")
        return Database(pool)

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def _execute(self, query: str, *params):
        async with self.pool.acquire() as connection:
            await connection.execute(query, *params)

    async def execute_from_file(self, filename: str, *params):
        with open(os.path.join(SQL_QUERIES_DIRECTORY, filename)) as f:
            await self._execute(f.read(), *params)
        logger.debug(
            f"Ran execute query from file: '{filename}' with params: {", ".join(map(str, params))}"
        )

    async def _fetch(self, query: str, *params):
        async with self.pool.acquire() as connection:
            result = await connection.fetch(query, *params)
        return result

    async def fetch_from_file(self, filename: str, *params):
        with open(os.path.join(SQL_QUERIES_DIRECTORY, filename)) as f:
            val = await self._fetch(f.read(), *params)
        logger.debug(
            f"Ran fetch query from file: '{filename}' with params: {', '.join(map(str, params))}"
        )
        return val

    async def close(self):
        await self.pool.close()
        logger.info("Closed database")

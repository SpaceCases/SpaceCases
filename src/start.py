import discord
import asyncio
from contextlib import suppress
from src.database import Database
from src.bot import SpaceCasesBot
from src.environment import Environment


async def main(environment: Environment, sync_slash_commands: bool) -> None:
    async with await Database.create(
        environment.db_user,
        environment.db_password,
        environment.db_name,
        environment.db_host,
        environment.db_port,
    ) as db:
        bot = SpaceCasesBot(
            db,
            environment.asset_domain,
            environment.leaderboards_domain,
            environment.test_guild,
            environment.owner_id,
            sync_slash_commands,
        )
        try:
            await bot.start(environment.bot_token)
        finally:
            await bot.close()


def start(sync_slash_commands: bool) -> None:
    discord.utils.setup_logging(root=False)
    environment = Environment.load()
    with suppress(KeyboardInterrupt):
        asyncio.run(main(environment, sync_slash_commands))

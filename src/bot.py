import os
import requests
import discord
from discord.ext import commands, tasks
from discord import app_commands
from src.logger import logger
from src.environment import Environment
from src.database import Database
from marisa_trie import Trie
from spacecases_common import Skin


class SpaceCasesCommandTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Debug logging
        user = interaction.user
        guild = interaction.guild if interaction.guild else "DM"
        # Check if it's a slash command and log the parameters
        if interaction.type == discord.InteractionType.application_command:
            command_name = interaction.command.name
            options = interaction.data.get("options", [])
            parameters = {opt["name"]: opt["value"] for opt in options}
            logger.debug(
                f"Slash command '{command_name}' invoked by {user} ({user.id}) in {guild} with parameters: {parameters}"
            )

        else:
            # Other interaction types
            logger.debug(
                f"Interaction '{interaction.type}' invoked by {user} ({user.id}) in {guild}"
            )
        return True

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        logger.error(f"{error}")
        e = discord.Embed(
            title="An error occurred!",
            description="It has been reported automatically",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=e, ephemeral=True)


class SpaceCasesBot(commands.Bot):
    def __init__(self, environment: Environment):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="", intents=intents, tree_cls=SpaceCasesCommandTree
        )
        self.skin_data: dict[str, Skin] = {}
        self.all_unformatted_names: list[str] = []
        self.skin_name_trie = Trie()
        self.environment = environment
        self.command_ids: dict[str, int] = {}

    def refresh_skin_data(self):
        logger.info("Refreshing skin data...")
        new_skin_data = {}
        new_all_unformatted_names = []
        raw_json = requests.get(
            "https://assets.spacecases.xyz/generated/skin_data.json"
        ).json()
        for unformatted_name, datum in raw_json.items():
            new_all_unformatted_names.append(unformatted_name)
            skin = Skin(
                datum["formatted_name"],
                datum["description"],
                datum["image_url"],
                datum["grade"],
                datum["min_float"],
                datum["max_float"],
                datum["price"],
            )
            new_skin_data[unformatted_name] = skin
        new_skin_name_trie = Trie(new_all_unformatted_names)
        self.skin_data = new_skin_data
        self.all_unformatted_names = new_all_unformatted_names
        self.skin_name_trie = new_skin_name_trie
        logger.info("Skin data refreshed")

    @tasks.loop(minutes=15)
    async def refresh_skin_data_loop(self):
        self.refresh_skin_data()

    async def close(self):
        await self.db.close()
        logger.info(f"Goodbye from {self.user}")

    async def setup_hook(self):
        self.db = await Database.create(
            self.environment.db_user,
            self.environment.db_password,
            self.environment.db_name,
            self.environment.db_host,
            self.environment.db_port,
        )
        await self._load_cogs()
        if self.environment.test_guild is not None:
            guild = discord.Object(id=self.environment.test_guild)
            logger.info(
                f"Syncing commands for guild with id: {self.environment.test_guild}..."
            )
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(
                f"Successfully synced the following commands for guild {self.environment.test_guild}: {synced}"
            )
        else:
            logger.info(f"Syncing commands globally...")
            synced = await self.tree.sync()
            logger.info(
                f"Successfully synced the following commands globally: {synced}"
            )
        for command in synced:
            self.command_ids[command.name] = command.id
        self.refresh_skin_data_loop.start()

    async def on_ready(self):
        logger.info(f"Bot is logged in as {self.user}")
        logger.info("Bot is ready to receive commands - press CTRL+C to stop")

    async def _load_cogs(self):
        for filename in os.listdir("src/cogs"):
            if filename.endswith(".py"):
                cog_name = filename.removesuffix(".py")
                await self.load_extension(f"src.cogs.{cog_name}")
                logger.info(f"Loaded cog: {cog_name}")

    async def on_message(self, _: discord.Message):
        # Disabling chat commands
        pass

    def get_slash_command_mention_string(self, name: str) -> str:
        return f"</{name}:{self.command_ids[name]}>"

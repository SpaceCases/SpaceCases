import os
import requests
import discord
from discord.ext import commands, tasks
from discord import app_commands
from src.logger import logger
from src.database import Database
from marisa_trie import Trie
from spacecases_common import ItemMetadatum, StickerMetadatum, SkinMetadatum, Rarity
from collections.abc import Iterable
from typing import Any, Optional


class SpaceCasesCommandTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Debug logging
        user = interaction.user
        guild = interaction.guild if interaction.guild else "DM"
        # Check if it's a slash command and log the parameters
        if (
            interaction.type == discord.InteractionType.application_command
            and interaction.command is not None
        ):
            command_name = interaction.command.name
            if interaction.data is not None:
                options = interaction.data.get("options", [])
            else:
                options = []

            parameters: Any
            if isinstance(options, Iterable):
                parameters = {opt["name"]: opt["value"] for opt in options}
            else:
                parameters = options

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
    def __init__(self, pool: Database, test_guild: Optional[str]):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="", intents=intents, tree_cls=SpaceCasesCommandTree
        )
        self.db = pool
        self.item_metadata: dict[str, ItemMetadatum] = {}
        self.all_unformatted_names: list[str] = []
        self.skin_name_trie = Trie()
        self.command_ids: dict[str, int] = {}
        self.status_int = 0
        self.user_count = 0
        self.test_guild = test_guild

    def refresh_item_metadata(self):
        # get new skin metadata
        logger.info("Refreshing skin metadata...")
        new_item_metadata = {}
        new_all_unformatted_names = []
        raw_json = requests.get(
            "https://assets.spacecases.xyz/generated/skin_metadata.json"
        ).json()
        for unformatted_name, datum in raw_json.items():
            new_all_unformatted_names.append(unformatted_name)
            skin_metadatum = SkinMetadatum(
                datum["formatted_name"],
                Rarity(datum["rarity"]),
                datum["price"],
                datum["image_url"],
                datum["description"],
                datum["min_float"],
                datum["max_float"],
            )
            new_item_metadata[unformatted_name] = skin_metadatum
        logger.info("Skin metadata refreshed")
        # get new sticker metadata
        logger.info("Refreshing sticker metadata...")
        raw_json = requests.get(
            "https://assets.spacecases.xyz/generated/sticker_metadata.json"
        ).json()
        for unformatted_name, datum in raw_json.items():
            new_all_unformatted_names.append(unformatted_name)
            sticker_metadatum = StickerMetadatum(
                datum["formatted_name"],
                Rarity(datum["rarity"]),
                datum["price"],
                datum["image_url"],
            )
            new_item_metadata[unformatted_name] = sticker_metadatum
        # update data
        new_skin_name_trie = Trie(new_all_unformatted_names)
        self.item_metadata = new_item_metadata
        self.all_unformatted_names = new_all_unformatted_names
        self.skin_name_trie = new_skin_name_trie
        logger.info("Sticker metadata refreshed")

    @tasks.loop(minutes=15)
    async def refresh_item_metadata_loop(self):
        self.refresh_item_metadata()

    @tasks.loop(seconds=10)
    async def bot_status_loop(self):
        self.status_int = (self.status_int + 1) % 2
        match self.status_int:
            case 0:
                await self.change_presence(activity=discord.Game(name="/register"))
            case 1:
                await self.change_presence(
                    activity=discord.Game(
                        name=f"{self.user_count} users | {len(self.guilds)} servers"
                    )
                )

    async def close(self):
        logger.info(f"Goodbye from {self.user}")

    async def setup_hook(self):
        self.user_count = (await self.db.fetch_from_file("count_users.sql"))[0]["count"]
        await self._load_cogs()
        if self.test_guild is not None:
            guild = discord.Object(id=self.test_guild)
            logger.info(f"Syncing commands for guild with id: {self.test_guild}...")
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(
                f"Successfully synced the following commands for {self.test_guild}: {synced}"
            )
        else:
            logger.info("Syncing commands globally...")
            synced = await self.tree.sync()
            logger.info(
                f"Successfully synced the following commands globally: {synced}"
            )
        for command in synced:
            self.command_ids[command.name] = command.id
        self.refresh_item_metadata_loop.start()

    async def on_ready(self):
        self.bot_status_loop.start()
        logger.info(f"Bot is logged in as {self.user}")
        logger.info("Bot is ready to receive commands - press CTRL+C to stop")

    def get_welcome_embed(self) -> discord.Embed:
        if self.user:
            name = self.user.display_name
        else:
            name = "SpaceCases"
        e = discord.Embed(
            description=f"""Hello! My name is **{name}**

I am CS:GO case unboxing and economy bot. With me you can:
• Unbox your dream skins
• Trade them with other users
• Take a risk and upgrade them
• And more coming soon
Use {self.get_slash_command_mention_string('register')} to get started!

Enjoy! - [Spacerulerwill](https://github.com/Spacerulerwill)""",
            color=discord.Color.dark_theme(),
        )
        if self.user:
            e.set_thumbnail(url=self.user.display_avatar.url)
        return e

    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"Joined new guild {guild.name} ({guild.id})")
        if (
            guild.system_channel
            and guild.system_channel.permissions_for(guild.me).send_messages
        ):
            await guild.system_channel.send(embed=self.get_welcome_embed())
        else:
            if guild.owner:
                await guild.owner.send(embed=self.get_welcome_embed())

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

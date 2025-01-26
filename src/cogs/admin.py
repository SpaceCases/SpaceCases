import discord
from discord.ext import commands
from src.bot import SpaceCasesBot
from src.commands.admin.sync import sync


class Admin(commands.Cog):
    def __init__(self, bot: SpaceCasesBot):
        self.bot = bot

    @discord.app_commands.command(name="sync", description="Synchronise slash commands")
    async def sync(self, interaction: discord.Interaction) -> None:
        await sync(self.bot, interaction)


async def setup(bot: SpaceCasesBot) -> None:
    await bot.add_cog(Admin(bot))

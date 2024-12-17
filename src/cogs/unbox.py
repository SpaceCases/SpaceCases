import discord
from discord.ext import commands
from src.bot import SpaceCasesBot
from src.commands.unbox.item import item, item_name_autocomplete
from src.commands.unbox.open import open, open_name_autocomplete


class Unbox(commands.Cog):
    def __init__(self, bot: SpaceCasesBot):
        self.bot = bot

    @discord.app_commands.command(name="item", description="Inspect an item")
    @discord.app_commands.describe(name="Name of the item you want to inspect")
    async def item(self, interaction: discord.Interaction, name: str):
        await item(self.bot, interaction, name)

    @item.autocomplete("name")
    async def item_autocomplete(self, _: discord.Interaction, current: str):
        return await item_name_autocomplete(self.bot, current)

    @discord.app_commands.command(name="open", description="Open a container")
    @discord.app_commands.describe(name="Name of the container you want to open")
    async def open(self, interaction: discord.Interaction, name: str):
        await open(self.bot, interaction, name)

    @open.autocomplete("name")
    async def open_autocomplete(self, _: discord.Interaction, current: str):
        return await open_name_autocomplete(self.bot, current)


async def setup(bot: SpaceCasesBot):
    await bot.add_cog(Unbox(bot))

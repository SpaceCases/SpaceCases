import discord
from discord.ext import commands
from src.bot import SpaceCasesBot
from src.commands.user.close import close
from src.commands.user.register import register
from src.commands.user.balance import balance
from src.commands.user.transfer import transfer
from src.commands.user.claim import claim
from src.commands.user.inventory import inventory, item_name_autocomplete
from typing import Optional


class User(commands.Cog):
    def __init__(self, bot: SpaceCasesBot):
        self.bot = bot

    @discord.app_commands.command(name="register", description="Register for a SpaceCases account")
    async def register(self, interaction: discord.Interaction) -> None:
        await register(self.bot, interaction)

    @discord.app_commands.command(name="close", description="Close your SpaceCases account")
    async def close(self, interaction: discord.Interaction) -> None:
        await close(self.bot, interaction)

    @discord.app_commands.command(name="balance", description="Check your SpaceCases account balance")
    @discord.app_commands.describe(user="The user whose balance you want to check. Defaults to your own balance if not specified.")
    async def balance(self, interaction: discord.Interaction, user: Optional[discord.User]) -> None:
        await balance(self.bot, interaction, user)

    @discord.app_commands.command(name="transfer", description="Transfer balance to another SpaceCases account")
    @discord.app_commands.describe(amount="Amount of balance to transfer", recipient="Recipient of the balance")
    async def transfer(self, interaction: discord.Interaction, amount: str, recipient: discord.User) -> None:
        await transfer(self.bot, interaction, amount, recipient)

    @discord.app_commands.command(name="claim", description="Claim your daily balance")
    async def claim(self, interaction: discord.Interaction) -> None:
        await claim(self.bot, interaction)

    @discord.app_commands.command(
        name="inventory",
        description="View a user's inventory, or an item from a user's inventory",
    )
    @discord.app_commands.describe(
        user="The user who's inventory to inspect",
        item_name="Name of item in the user's inventory",
    )
    async def inventory(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.User],
        item_name: Optional[str],
    ) -> None:
        await inventory(self.bot, interaction, user, item_name)

    @inventory.autocomplete("item_name")
    async def item_name_autocomplete(self, interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice]:
        return await item_name_autocomplete(self.bot, interaction, current)


async def setup(bot: SpaceCasesBot) -> None:
    await bot.add_cog(User(bot))

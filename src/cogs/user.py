import discord
from discord.ext import commands
from src.bot import SpaceCasesBot
from src.commands.user.close import close
from src.commands.user.register import register
from src.commands.user.balance import balance
from src.commands.user.transfer import transfer
from src.commands.user.claim import claim
from typing import Optional


class User(commands.Cog):
    def __init__(self, bot: SpaceCasesBot):
        self.bot = bot

    @discord.app_commands.command(
        name="register", description="Register for a SpaceCases account"
    )
    async def register(self, interaction: discord.Interaction):
        await register(self.bot, interaction)

    @discord.app_commands.command(
        name="close", description="Close your SpaceCases account"
    )
    async def close(self, interaction: discord.Interaction):
        await close(self.bot, interaction)

    @discord.app_commands.command(
        name="balance", description="Check your SpaceCases account balance"
    )
    @discord.app_commands.describe(
        user="The user whose balance you want to check. Defaults to your own balance if not specified."
    )
    async def balance(
        self, interaction: discord.Interaction, user: Optional[discord.User]
    ):
        await balance(self.bot, interaction, user)

    @discord.app_commands.command(
        name="transfer", description="Transfer balance to another SpaceCases account"
    )
    @discord.app_commands.describe(
        amount="Amount of balance to transfer", recipient="Recipient of the balance"
    )
    async def transfer(
        self, interaction: discord.Interaction, amount: str, recipient: discord.User
    ):
        await transfer(self.bot, interaction, amount, recipient)

    @discord.app_commands.command(name="claim", description="Claim your daily balance")
    async def claim(self, interaction: discord.Interaction):
        await claim(self.bot, interaction)


async def setup(bot: SpaceCasesBot):
    await bot.add_cog(User(bot))

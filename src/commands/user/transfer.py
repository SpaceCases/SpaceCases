import discord
from src.bot import SpaceCasesBot


async def transfer(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    amount: float,
    recipient: discord.User,
):
    await interaction.response.defer()

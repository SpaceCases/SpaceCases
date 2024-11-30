import discord
from src.bot import SpaceCasesBot
from src.util.embed import send_success_embed


async def register(bot: SpaceCasesBot, interaction: discord.Interaction):
    rows = await bot.db.fetch_from_file("register.sql", interaction.user.id)
    if len(rows) == 0:
        response = "You are **already** registered!"
    else:
        response = "You are **now** registered!"
    await send_success_embed(interaction, response)

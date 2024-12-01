import discord
from src.bot import SpaceCasesBot
from src.util.embed import send_success_embed, send_err_embed


async def register(bot: SpaceCasesBot, interaction: discord.Interaction):
    rows = await bot.db.fetch_from_file("register.sql", interaction.user.id)
    if len(rows) == 0:
        await send_err_embed(interaction, "You are **already** registered!")
    else:
        await send_success_embed(interaction, "You are **now** registered!")
        bot.user_count += 1

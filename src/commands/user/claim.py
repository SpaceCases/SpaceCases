import discord
from typing import Optional
from src.bot import SpaceCasesBot
from src.util.embed import send_err_embed
from src.util.string import currency_str_format


async def claim(bot: SpaceCasesBot, interaction: discord.Interaction) -> None:
    rows = await bot.db.fetch_from_file("claim.sql", interaction.user.id)
    status: Optional[bool] = rows[0]["status"]
    if status is None:
        await send_err_embed(
            interaction,
            f"You are **not** registered. Use {bot.get_slash_command_mention_string('register')} to register!",
        )
    elif not status:
        await send_err_embed(interaction, "You have **already** claimed today!")
    else:
        e = discord.Embed(
            title="You have successfully claimed your daily reward!",
            color=discord.Color.green(),
        )
        new_balance = rows[0]["balance"]
        amount = rows[0]["amount"]
        claim_streak = rows[0]["streak"]
        e.set_thumbnail(url=interaction.user.display_avatar.url)
        e.add_field(name="New Balance", value=currency_str_format(new_balance))
        e.add_field(name="Amount", value=currency_str_format(amount))
        e.add_field(name="Claim Streak ️‍🔥", value=str(claim_streak))
        e.set_footer(text="You can claim again tomorrow")
        await interaction.response.send_message(embed=e)

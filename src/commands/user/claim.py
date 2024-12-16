import discord
from src.bot import SpaceCasesBot
from src.util.embed import send_err_embed
from src.util.string import currency_str_format

USER_NOT_FOUND = 0
USER_CANT_CLAIM = 1
USER_CLAIM_SUCCESS = 2


async def claim(bot: SpaceCasesBot, interaction: discord.Interaction):
    rows = await bot.db.fetch_from_file("claim.sql", interaction.user.id)
    status = rows[0]["status"]
    if status == USER_NOT_FOUND:
        await send_err_embed(
            interaction,
            f"You are **not** registered. Use {bot.get_slash_command_mention_string('register')} to register!",
        )
    elif status == USER_CANT_CLAIM:
        await send_err_embed(interaction, "You have **already** claimed today!")
    elif status == USER_CLAIM_SUCCESS:
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

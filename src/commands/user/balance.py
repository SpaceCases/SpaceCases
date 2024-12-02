import discord
from src.bot import SpaceCasesBot
from src.util.string import currency_str_format
from src.util.embed import send_err_embed
from typing import Optional


async def balance(
    bot: SpaceCasesBot, interaction: discord.Interaction, user: Optional[discord.User]
):
    if user is None:
        target_user = interaction.user
    else:
        target_user = user

    rows = await bot.db.fetch_from_file("balance.sql", target_user.id)
    if len(rows) > 0:
        balance = rows[0]["balance"]
        e = discord.Embed(
            title=f"{target_user.display_name}'s Balance",
            color=discord.Color.dark_theme(),
        )
        e.set_thumbnail(url=target_user.display_avatar.url)
        e.add_field(name="Current Balance", value=currency_str_format(balance))
        await interaction.response.send_message(embed=e)
    else:
        if target_user.id == interaction.user.id:
            await send_err_embed(
                interaction,
                f"You are **not** registered. Use {bot.get_slash_command_mention_string('register')} to register!",
            )
        else:
            await send_err_embed(
                interaction,
                f"{target_user.display_name} is **not** registered",
            )

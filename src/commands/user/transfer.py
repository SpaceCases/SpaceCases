import discord
import re
from src.bot import SpaceCasesBot
from src.util.embed import send_err_embed
from src.util.string import currency_str_format
from decimal import Decimal


async def transfer(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    amount: str,
    recipient: discord.User,
):
    if interaction.user.id == recipient.id:
        await send_err_embed(interaction, "You **cannot** transfer money to yourself")
        return

    # Regex pattern for a number with a maximum of two decimal places, allowing a leading or trailing dot
    pattern = r"^\d*\.?\d{0,2}$"

    if not re.match(pattern, amount):
        await send_err_embed(
            interaction,
            "**Invalid** amount provided. Please enter a valid amount with up to two decimal places",
        )
        return

    amount = Decimal(amount)
    cents = int(amount * 100)
    if cents == 0:
        await send_err_embed(interaction, "You **cannot** transfer **zero** balance")
        return

    async with bot.db.pool.acquire() as connection:
        async with connection.transaction(isolation="serializable"):
            # check we exist
            rows = await bot.db.fetch_from_file("balance.sql", interaction.user.id)
            if len(rows) == 0:
                await send_err_embed(
                    interaction,
                    f"You are **not** registered. Use {bot.get_slash_command_mention_string('register')} to register!",
                )
                return

            # check we have enough balance
            balance = rows[0]["balance"]
            if balance < cents:
                await send_err_embed(
                    interaction, "You **do not** have enough balance for this action"
                )
                return

            # give their balance
            rows = await bot.db.fetch_from_file(
                "change_balance.sql", cents, recipient.id
            )
            if len(rows) == 0:
                await send_err_embed(
                    interaction, f"{recipient.display_name} is **not** registered!"
                )
                return
            new_recipient_balance = rows[0]["balance"]
            # remove our balance
            rows = await bot.db.fetch_from_file(
                "change_balance.sql", -cents, interaction.user.id
            )
            new_sender_balance = rows[0]["balance"]
    e = discord.Embed(
        description=f"Successfully transferred **{currency_str_format(cents)}** to {recipient.display_name}",
        color=discord.Colour.green(),
    )
    e.set_thumbnail(url=recipient.display_avatar)
    e.add_field(name="Your New Balance", value=currency_str_format(new_sender_balance))
    e.add_field(
        name=f"{recipient.display_name}'s New Balance",
        value=currency_str_format(new_recipient_balance),
    )
    await interaction.response.send_message(embed=e)

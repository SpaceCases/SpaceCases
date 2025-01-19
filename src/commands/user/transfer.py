import discord
import re
from src.bot import SpaceCasesBot
from src.database import BALANCE_FOR_UPDATE, CHANGE_BALANCE
from src.ui.embed import send_err_embed
from src.string import currency_str_format
from decimal import Decimal
from src.exceptions import UserNotRegisteredError, InsufficientBalanceError


async def transfer(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    amount: str,
    recipient: discord.User,
) -> None:
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

    decimal_amount = Decimal(amount)
    cents = int(decimal_amount * 100)
    if cents == 0:
        await send_err_embed(interaction, "You **cannot** transfer **zero** balance")
        return

    async with bot.db.pool.acquire() as connection:
        async with connection.transaction(isolation="serializable"):
            # check we exist
            rows = await bot.db.fetch_from_file_with_connection(
                BALANCE_FOR_UPDATE, connection, interaction.user.id
            )
            if len(rows) == 0:
                raise UserNotRegisteredError(interaction.user)

            # check we have enough balance
            balance = rows[0]["balance"]
            if balance < cents:
                raise InsufficientBalanceError

            # give their balance
            rows = await bot.db.fetch_from_file_with_connection(
                CHANGE_BALANCE, connection, recipient.id, cents
            )
            if len(rows) == 0:
                raise UserNotRegisteredError(recipient)

            new_recipient_balance = rows[0]["balance"]

            # remove our balance
            rows = await bot.db.fetch_from_file_with_connection(
                CHANGE_BALANCE,
                connection,
                interaction.user.id,
                -cents,
            )
            new_sender_balance = rows[0]["balance"]

    # send result embed
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

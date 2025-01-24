import discord
from . import send_err_embed
from src.exceptions import (
    UserNotRegisteredError,
    InsufficientBalanceError,
    ItemDoesNotExistError,
    ContainerDoesNotExistError,
    UserDoesNotOwnItemError,
    UserInventoryEmptyError,
)
from src.logger import logger


async def send_exception_embed(
    interaction: discord.Interaction, exception: Exception, ephemeral: bool = False
) -> None:
    if isinstance(exception, UserNotRegisteredError):
        if interaction.user.id == exception.user.id:
            message = "You are **not** registered"
        else:
            message = f"{exception.user.display_name} is **not** registered"
        await send_err_embed(interaction, message, ephemeral)
    elif isinstance(exception, InsufficientBalanceError):
        await send_err_embed(
            interaction,
            "You **do not** have sufficient balance for this action",
            ephemeral,
        )
    elif isinstance(exception, ItemDoesNotExistError):
        await send_err_embed(
            interaction, f"Item `{exception.item}` does **not** exist", ephemeral
        )
    elif isinstance(exception, ContainerDoesNotExistError):
        await send_err_embed(
            interaction,
            f"Container `{exception.container}` does **not** exist",
            ephemeral,
        )
    elif isinstance(exception, UserDoesNotOwnItemError):
        if exception.user.id == interaction.user.id:
            message = f"You do not own an item with ID: `{exception.id}`"
        else:
            message = f"{exception.user.display_name} does not own an item with ID: `{exception.id}`"
        await send_err_embed(interaction, message, ephemeral)
    elif isinstance(exception, UserInventoryEmptyError):
        if exception.user.id == interaction.user.id:
            message = "Your inventory is **empty**"
        else:
            message = f"{exception.user.display_name}'s inventory is **empty**"
        await send_err_embed(interaction, message, ephemeral)
    else:
        e = discord.Embed(
            title="An error occurred!",
            description="It has been reported automatically",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=e, ephemeral=True)
        logger.exception(exception)
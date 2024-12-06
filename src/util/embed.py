import discord
from typing import Optional
from discord.ui import Button, View
from spacecases_common import Rarity


def create_embed(
    msg_content: str, color: discord.Color = discord.Color.dark_theme()
) -> discord.Embed:
    return discord.Embed(description=msg_content, color=color)


def create_success_embed(msg_content: str) -> discord.Embed:
    return create_embed(msg_content, discord.Color.green())


def create_err_embed(msg_content: str) -> discord.Embed:
    return create_embed(msg_content, discord.Color.red())


async def send_embed(
    interaction: discord.Interaction,
    msg_content: str,
    color: discord.Color = discord.Color.dark_theme(),
    ephemeral: bool = False,
) -> None:
    embed = create_embed(msg_content, color)
    await interaction.response.send_message(
        embed=embed,
        ephemeral=ephemeral,
    )


async def send_success_embed(
    interaction: discord.Interaction, msg_content: str, ephemeral: bool = False
) -> None:
    embed = create_success_embed(msg_content)
    await interaction.response.send_message(
        embed=embed,
        ephemeral=ephemeral,
    )


async def send_err_embed(
    interaction: discord.Interaction, msg_content: str, ephemeral: bool = False
) -> None:
    embed = create_err_embed(msg_content)
    await interaction.response.send_message(
        embed=embed,
        ephemeral=ephemeral,
    )


async def yes_no_embed(
    interaction: discord.Interaction,
    msg_content: str,
    on_yes,
    on_no,
    timeout: Optional[float] = 30,
) -> None:
    responded = False
    embed = discord.Embed(description=msg_content, color=discord.Color.dark_theme())

    # Define buttons
    yes_button: Button = Button(label="Yes", style=discord.ButtonStyle.green)
    no_button: Button = Button(label="No", style=discord.ButtonStyle.red)

    # Callback for "Yes" button
    async def yes_button_callback(interaction: discord.Interaction):
        nonlocal responded
        if interaction.user != interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
        await on_yes(interaction)
        responded = True

    # Callback for "No" button
    async def no_button_callback(interaction: discord.Interaction):
        nonlocal responded
        if interaction.user != interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
        await on_no(interaction)
        responded = True

    # Attach callbacks to buttons
    yes_button.callback = yes_button_callback  # type: ignore[assignment]
    no_button.callback = no_button_callback  # type: ignore[assignment]

    async def timeout_callback():
        if responded:
            return
        # Edit the message to indicate timeout and remove buttons
        message = await interaction.original_response()
        # Edit the message to indicate timeout and remove buttons
        new_embed = create_err_embed("You did **not** respond in time")
        await message.edit(embed=new_embed, view=None)

    # Create a view and add buttons
    view = View(timeout=timeout)
    view.on_timeout = timeout_callback  # type: ignore[assignment]
    view.add_item(yes_button)
    view.add_item(no_button)

    # Send the message with the embed and buttons
    await interaction.response.send_message(embed=embed, view=view)


def get_rarity_embed_color(rarity: Rarity):
    return [0xB0C3D9, 0x5E98D9, 0x4B69FF, 0x8847FF, 0xD32CE6, 0xEB4B4B, 0xE4AE39][
        rarity.value
    ]

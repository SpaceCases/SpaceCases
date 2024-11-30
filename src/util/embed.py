import discord
from typing import Optional
from discord.ui import Button, View


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
    embed = discord.Embed(description=msg_content, color=discord.Color.dark_theme())

    # Define buttons
    yes_button = Button(label="Yes", style=discord.ButtonStyle.green)
    no_button = Button(label="No", style=discord.ButtonStyle.red)

    # Callback for "Yes" button
    async def yes_button_callback(interaction: discord.Interaction):
        if interaction.user != interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
        await on_yes(interaction)

    # Callback for "No" button
    async def no_button_callback(interaction: discord.Interaction):
        if interaction.user != interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
        await on_no(interaction)

    # Attach callbacks to buttons
    yes_button.callback = yes_button_callback
    no_button.callback = no_button_callback

    async def timeout_callback():
        # Edit the message to indicate timeout and remove buttons
        message = await interaction.original_response()
        # Edit the message to indicate timeout and remove buttons
        new_embed = create_err_embed("You did **not** respond in time")
        await message.edit(embed=new_embed, view=None)

    # Create a view and add buttons
    view = View(timeout=timeout)
    view.on_timeout = timeout_callback
    view.add_item(yes_button)
    view.add_item(no_button)

    # Send the message with the embed and buttons
    await interaction.response.send_message(embed=embed, view=view)


def get_grade_embed_colour(grade: str):
    match grade:
        case "Consumer Grade":
            return 0xB0C3D9
        case "Industrial Grade":
            return 0x5E98D9
        case "Mil-Spec Grade" | "High Grade":
            return 0x4B69FF
        case "Restricted" | "Remarkable":
            return 0x8847FF
        case "Classified" | "Exotic":
            return 0xD32CE6
        case "Covert" | "Extraordinary":
            return 0xEB4B4B
        case "Contraband":
            return 0xE4AE39
        case _:
            raise ValueError(f"Invalid grade: {grade}")

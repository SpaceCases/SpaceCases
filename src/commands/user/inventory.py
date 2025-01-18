import json
import discord
from src.bot import SpaceCasesBot
from src.database import GET_INVENTORY_CHECK_EXIST, GET_ITEM
from src.util.string import currency_str_format
from src.util.autocomplete import inventory_item_autocomplete
from src.util.types import ItemType
from src.util.embed import get_rarity_embed_color
from src.exceptions import (
    UserNotRegisteredError,
    UserInventoryEmptyError,
    UserDoesNotOwnItemError,
)
from spacecases_common import SkinMetadatum
from typing import Optional, cast


async def inventory(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    user: Optional[discord.User],
    item_id: Optional[int],
) -> None:
    if user is None:
        target_user = interaction.user
    else:
        target_user = user

    if item_id is None:
        await show_user_inventory(interaction, bot, target_user)
    else:
        await show_item_from_user_inventory(interaction, bot, target_user, item_id)


async def show_user_inventory(
    interaction: discord.Interaction,
    bot: SpaceCasesBot,
    user: discord.Member | discord.User,
) -> None:
    user_exists, inventory_capacity, items = (
        await bot.db.fetch_from_file(GET_INVENTORY_CHECK_EXIST, user.id)
    )[0]
    if not user_exists:
        raise UserNotRegisteredError(user)

    # empty inventory
    if len(items) == 0:
        raise UserInventoryEmptyError(user)

    # create embed
    inventory_value = sum(bot.item_metadata[item[2]].price for item in items)
    e = discord.Embed(
        title=f"{user.display_name}'s Inventory",
        description=f"Total Value: **{currency_str_format(inventory_value)}**\nSlots Used: **{len(items)}/{inventory_capacity}**",
    )
    item_strings = []
    for id, _, name, _ in items:
        metadata = bot.item_metadata[name]
        item_strings.append(
            f"{metadata.formatted_name} - **{currency_str_format(metadata.price)}** (ID: **{id}**)"
        )
    e.add_field(name="Items", value="\n".join(item_strings))
    e.set_thumbnail(url=user.display_avatar.url)
    await interaction.response.send_message(embed=e)


async def show_item_from_user_inventory(
    interaction: discord.Interaction,
    bot: SpaceCasesBot,
    user: discord.Member | discord.User,
    item_id: int,
) -> None:
    rows = await bot.db.fetch_from_file(GET_ITEM, user.id, item_id)
    if len(rows) == 0:
        raise UserDoesNotOwnItemError(user, item_id)
    user_exists: bool
    name: str
    type: ItemType
    user_exists, name, type, details = rows[0]
    details = json.loads(details)
    if not user_exists:
        raise UserNotRegisteredError(user)
    metadatum = bot.item_metadata[name]
    e = discord.Embed(
        title=metadatum.formatted_name, color=get_rarity_embed_color(metadatum.rarity)
    )
    e.add_field(name="Price", value=currency_str_format(metadatum.price))
    e.set_image(url=metadatum.image_url)
    e.set_footer(text=f"Owned by {user.display_name}", icon_url=user.display_avatar)
    if type == ItemType.Skin:
        metadatum = cast(SkinMetadatum, metadatum)
        e.description = metadatum.description
        float_val: float = details["float"]
        e.add_field(name="Float", value=float_val)
        rarity = metadatum.rarity.get_name_for_skin()
    elif type == ItemType.Sticker:
        rarity = metadatum.rarity.get_name_for_skin()
    e.add_field(name="Rarity", value=rarity)
    await interaction.response.send_message(embed=e)


async def item_id_autocomplete(
    bot: SpaceCasesBot, interaction: discord.Interaction, current: str
) -> list[discord.app_commands.Choice]:
    # what user are they trying to view the inventory of?
    try:
        user = interaction.namespace["user"]
    except KeyError:
        user = interaction.user

    return await inventory_item_autocomplete(bot, user, current)

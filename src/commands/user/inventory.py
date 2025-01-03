import discord
from src.bot import SpaceCasesBot
from src.database import (
    GET_INVENTORY_CHECK_EXIST,
    GET_INVENTORY,
    GET_SKIN,
    GET_STICKER,
)
from src.util.embed import (
    send_skin_viewer,
    send_sticker_viewer,
)
from src.util.string import currency_str_format
from src.util.types import SkinOwnership, StickerOwnership
from src.exceptions import (
    UserNotRegisteredError,
    UserInventoryEmptyError,
    ItemDoesNotExistError,
    UserDoesNotOwnItemError,
)
from spacecases_common import (
    remove_skin_name_formatting,
    SkinMetadatum,
    StickerMetadatum,
)
from typing import Optional
from collections import Counter


async def inventory(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    user: Optional[discord.User],
    item: Optional[str],
) -> None:
    if user is None:
        target_user = interaction.user
    else:
        target_user = user

    if item is None:
        await show_user_inventory(interaction, bot, target_user)
    else:
        await show_item_from_user_inventory(interaction, bot, target_user, item)


async def show_user_inventory(
    interaction: discord.Interaction,
    bot: SpaceCasesBot,
    user: discord.Member | discord.User,
) -> None:
    user_exists, inventory_capacity, skins, stickers = (
        await bot.db.fetch_from_file(GET_INVENTORY_CHECK_EXIST, user.id)
    )[0]
    if not user_exists:
        raise UserNotRegisteredError(user)

    # empty inventory
    if len(skins) == 0 and len(stickers) == 0:
        raise UserInventoryEmptyError(user)

    # create embed
    inventory_value = sum(bot.item_metadata[skin[0]].price for skin in skins) + sum(
        bot.item_metadata[sticker[0]].price for sticker in stickers
    )
    e = discord.Embed(
        title=f"{user.display_name}'s Inventory",
        description=f"Total Value: **{currency_str_format(inventory_value)}**\nSlots Used: **{len(skins) + len(stickers)}/{inventory_capacity}**",
    )
    # skins field
    if len(skins) > 0:
        skin_details = []
        for skin in skins:
            metadata = bot.item_metadata[skin[0]]
            skin_details.append(
                f"{metadata.formatted_name} - **{currency_str_format(metadata.price)}**"
            )
        e.add_field(name="Skins", value="\n".join(skin_details), inline=False)
    # stickers field
    if len(stickers):
        sticker_details = []
        for sticker in stickers:
            metadata = bot.item_metadata[sticker[0]]
            sticker_details.append(
                f"{metadata.formatted_name} - **{currency_str_format(metadata.price)}**"
            )
        e.add_field(name="Stickers", value="\n".join(sticker_details))
    e.set_thumbnail(url=user.display_avatar.url)
    await interaction.response.send_message(embed=e)


async def show_item_from_user_inventory(
    interaction: discord.Interaction,
    bot: SpaceCasesBot,
    user: discord.Member | discord.User,
    item: str,
) -> None:
    # check item exists
    unformatted_item_name = remove_skin_name_formatting(item)
    try:
        item_metadatum = bot.item_metadata[unformatted_item_name]
    except KeyError:
        raise ItemDoesNotExistError(item)

    # send embed
    if isinstance(item_metadatum, SkinMetadatum):
        # get the skin(s)
        exists, floats = (
            await bot.db.fetch_from_file(GET_SKIN, user.id, unformatted_item_name)
        )[0]
        if not exists:
            raise UserNotRegisteredError(user)
        # user does not own this item
        if len(floats) == 0:
            raise UserDoesNotOwnItemError(user, item)
        # send skin viewer embed
        await send_skin_viewer(interaction, SkinOwnership(user, item_metadatum, floats))

    elif isinstance(item_metadatum, StickerMetadatum):
        # get the sticker
        exists, count = (
            await bot.db.fetch_from_file(GET_STICKER, user.id, unformatted_item_name)
        )[0]
        if not exists:
            raise UserNotRegisteredError(user)
        # user does not own this item
        if count == 0:
            raise UserDoesNotOwnItemError(user, item)
        # send sticker embed
        await send_sticker_viewer(
            interaction, StickerOwnership(user, item_metadatum, count)
        )


async def item_name_autocomplete(
    bot: SpaceCasesBot, interaction: discord.Interaction, current: str
) -> list[discord.app_commands.Choice]:
    # what user are they trying to view the inventory of?
    try:
        user = interaction.namespace["user"]
    except KeyError:
        user = interaction.user

    # get their items
    unformatted_curret = remove_skin_name_formatting(current)
    skins, stickers = (await bot.db.fetch_from_file(GET_INVENTORY, user.id))[0]
    all_names: list[str] = [skin[0] for skin in skins] + [
        sticker[0] for sticker in stickers
    ]
    name_counter = Counter(all_names)
    # build the options
    result = []
    for name, count in name_counter.items():
        if not name.startswith(unformatted_curret):
            continue
        item_metadatum = bot.item_metadata[name]
        if count == 1:
            result.append(
                discord.app_commands.Choice(
                    name=item_metadatum.formatted_name,
                    value=item_metadatum.formatted_name,
                )
            )
        else:
            result.append(
                discord.app_commands.Choice(
                    name=f"{item_metadatum.formatted_name} X{count}",
                    value=item_metadatum.formatted_name,
                )
            )
    return result

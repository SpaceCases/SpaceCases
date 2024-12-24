import discord
from src.bot import SpaceCasesBot
from src.database import GET_INVENTORY_CHECK_EXIST, GET_INVENTORY, GET_SKIN, GET_STICKER
from src.util.embed import send_err_embed, get_rarity_embed_color
from src.util.string import currency_str_format
from src.exceptions import UserNotRegisteredError
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
        user_exists, inventory_capacity, skins, stickers = (
            await bot.db.fetch_from_file(GET_INVENTORY_CHECK_EXIST, target_user.id)
        )[0]
        if not user_exists:
            raise UserNotRegisteredError(target_user)

        # empty inventory
        if len(skins) == 0 and len(stickers) == 0:
            await send_err_embed(interaction, "Your inventory is **empty!**")
            return

        # create embed
        inventory_value = sum(bot.item_metadata[skin[0]].price for skin in skins) + sum(
            bot.item_metadata[sticker[0]].price for sticker in stickers
        )
        e = discord.Embed(
            title=f"{target_user.display_name}'s Inventory",
            description=f"Total Value: **{currency_str_format(inventory_value)}**\nSlots Used: **{len(skins) + len(stickers)}/{inventory_capacity}**",
        )
        if len(skins) > 0:
            skin_details = []
            for skin in skins:
                metadata = bot.item_metadata[skin[0]]
                skin_details.append(
                    f"{metadata.formatted_name} - **{currency_str_format(metadata.price)}**"
                )
            e.add_field(name="Skins", value="\n".join(skin_details), inline=False)
        if len(stickers):
            sticker_details = []
            for sticker in stickers:
                metadata = bot.item_metadata[sticker[0]]
                sticker_details.append(
                    f"{metadata.formatted_name} - **{currency_str_format(metadata.price)}**"
                )
            e.add_field(name="Stickers", value="\n".join(sticker_details))
        e.set_thumbnail(url=target_user.display_avatar.url)
        await interaction.response.send_message(embed=e)
    else:
        # check item exists
        unformatted_item_name = remove_skin_name_formatting(item)
        try:
            item_metadatum = bot.item_metadata[unformatted_item_name]
        except KeyError:
            await send_err_embed(interaction, f"Item `{item}` does **not** exist")
            return
        # send embed
        if isinstance(item_metadatum, SkinMetadatum):
            exists, skins = (
                await bot.db.fetch_from_file(
                    GET_SKIN, target_user.id, unformatted_item_name
                )
            )[0]
            if not exists:
                raise UserNotRegisteredError(target_user)
            # user does not own this item
            if len(skins) == 0:
                if target_user.id == interaction.user.id:
                    message = f"You do not own a `{item}`"
                else:
                    message = f"{target_user.display_name} does not own a `{item}`"
                await send_err_embed(interaction, message)

            # send item embed
            best_float = min(skin[1] for skin in skins)
            e = discord.Embed(
                title=item_metadatum.formatted_name,
                description=item_metadatum.description,
                color=get_rarity_embed_color(item_metadatum.rarity),
            )
            e.set_image(url=item_metadatum.image_url)
            e.add_field(name="Price", value=currency_str_format(item_metadatum.price))
            e.add_field(
                name="Rarity", value=item_metadatum.rarity.get_name_for_regular_item()
            )
            e.add_field(name="Best Float", value=best_float)
            e.set_footer(
                text=f"Owned by {target_user.display_name}",
                icon_url=target_user.display_avatar.url,
            )

            await interaction.response.send_message(embed=e)

        elif isinstance(item_metadatum, StickerMetadatum):
            exists, count = (
                await bot.db.fetch_from_file(
                    GET_STICKER, target_user.id, unformatted_item_name
                )
            )[0]
            if not exists:
                raise UserNotRegisteredError(target_user)

            # user does not own this item
            if count == 0:
                if target_user.id == interaction.user.id:
                    message = f"You do not own a `{item}`"
                else:
                    message = f"{target_user.display_name} does not own a `{item}`"
                await send_err_embed(interaction, message)
            # send sticker embed
            e = discord.Embed(
                title=item_metadatum.formatted_name,
                color=get_rarity_embed_color(item_metadatum.rarity),
            )
            e.set_image(url=item_metadatum.image_url)
            e.add_field(name="Price", value=currency_str_format(item_metadatum.price))
            e.add_field(
                name="Rarity", value=item_metadatum.rarity.get_name_for_regular_item()
            )
            e.add_field(name="Count", value=count)
            e.set_footer(
                text=f"Owned by {target_user.display_name}",
                icon_url=target_user.display_avatar.url,
            )
            await interaction.response.send_message(embed=e)


async def item_name_autocomplete(
    bot: SpaceCasesBot, interaction: discord.Interaction, current: str
) -> list[discord.app_commands.Choice]:
    try:
        user = interaction.namespace["user"]
    except KeyError:
        user = interaction.user

    unformatted_curret = remove_skin_name_formatting(current)
    skins, stickers = (await bot.db.fetch_from_file(GET_INVENTORY, user.id))[0]
    all_names: list[str] = [skin[0] for skin in skins] + [
        sticker[0] for sticker in stickers
    ]
    name_counter = Counter(all_names)
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

import discord
from typing import Optional, Iterable
from src.bot import SpaceCasesBot
from src.util.embed import send_err_embed, get_rarity_embed_color
from src.util.string import currency_str_format
from spacecases_common import (
    remove_skin_name_formatting,
    SkinMetadatum,
    StickerMetadatum,
)


def get_inventory_item_list_string(
    bot: SpaceCasesBot, items: Iterable[tuple[str, int]]
) -> str:
    item_strings = []
    for unformatted_name, count in items:
        item_metadata = bot.item_metadata[unformatted_name]
        if count == 1:
            item_strings.append(
                f"• {item_metadata.formatted_name} - **{currency_str_format(item_metadata.price)}**"
            )
        else:
            item_strings.append(
                f"• {item_metadata.formatted_name} **X{count}** - **{currency_str_format(item_metadata.price * count)}** (**{currency_str_format(item_metadata.price)}** each)"
            )
    return "\n".join(item_strings)


async def inventory(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    user: Optional[discord.User],
    item_name: Optional[str],
) -> None:
    if user is None:
        target_user = interaction.user
    else:
        target_user = user

    # check target user exists
    does_user_exist = (
        await bot.db.fetch_from_file("does_user_exist.sql", target_user.id)
    )[0]["exists"]
    if not does_user_exist:
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
            return

    # if no item, then we display inventory overview
    if item_name is None:
        skins_result = await bot.db.fetch_from_file(
            "inventory/get_user_skins.sql", target_user.id
        )
        stickers_result = await bot.db.fetch_from_file(
            "inventory/get_user_stickers.sql", target_user.id
        )

        # empty inventory
        if len(skins_result) == 0 and len(stickers_result) == 0:
            if target_user.id == interaction.user.id:
                await send_err_embed(interaction, "Your inventory is empty")
            else:
                await send_err_embed(interaction, f"{target_user.display_name}'s inventory is empty")
            return

        e = discord.Embed(title=f"{target_user.display_name}'s Inventory")
        e.set_thumbnail(url=target_user.display_avatar.url)
        if len(skins_result) > 0:
            e.add_field(
                name="Skins",
                value=get_inventory_item_list_string(
                    bot, ((skin["name"], len(skin["floats"])) for skin in skins_result)
                ),
                inline=False,
            )
        if len(stickers_result) > 0:
            e.add_field(
                name="Stickers",
                value=get_inventory_item_list_string(
                    bot,
                    (
                        (sticker["name"], sticker["count"])
                        for sticker in stickers_result
                    ),
                ),
                inline=False,
            )
        # determine inventory value
        skins_value = sum(
            bot.item_metadata[skin["name"]].price * len(skin["floats"])
            for skin in skins_result
        )
        stickers_value = sum(
            bot.item_metadata[sticker["name"]].price * sticker["count"]
            for sticker in stickers_result
        )
        inventory_value = skins_value + stickers_value
        e.description = f"Total Value: **{currency_str_format(inventory_value)}**"
        await interaction.response.send_message(embed=e)
    else:
        # otherwise show specific information for that item
        unformatted_item_name = remove_skin_name_formatting(item_name)
        try:
            item_metadatum = bot.item_metadata[unformatted_item_name]
        except KeyError:
            await send_err_embed(interaction, f"No item exists with name: `{unformatted_item_name}`")
            return
        if isinstance(item_metadatum, SkinMetadatum):
            skin_result = await bot.db.fetch_from_file(
                "inventory/get_skin.sql", target_user.id, unformatted_item_name
            )
            if len(skin_result) == 0:
                await send_err_embed(
                    interaction,
                    f"There is no **{item_metadatum.formatted_name}** in your inventory",
                )
                return
            skin_data = skin_result[0]
            e = discord.Embed(
                title=item_metadatum.formatted_name,
                description=item_metadatum.description,
                color=get_rarity_embed_color(item_metadatum.rarity),
            )
            e.set_image(url=item_metadatum.image_url)
            e.add_field(name="Price", value=currency_str_format(item_metadatum.price))
            e.add_field(name="Best Float", value=max(skin_data["floats"]))
            e.add_field(name="Rarity", value=item_metadatum.rarity.get_name_for_skin())
        if isinstance(item_metadatum, StickerMetadatum):
            sticker_result = await bot.db.fetch_from_file(
                "inventory/get_sticker.sql", target_user.id, unformatted_item_name
            )
            if len(sticker_result) == 0:
                await send_err_embed(
                    interaction,
                    f"There is no **{item_metadatum.formatted_name}** in your inventory",
                )
                return
            sticker_data = sticker_result[0]
            e = discord.Embed(
                title=item_metadatum.formatted_name,
                color=get_rarity_embed_color(item_metadatum.rarity),
            )
            e.set_image(url=item_metadatum.image_url)
            e.add_field(name="Price", value=currency_str_format(item_metadatum.price))
            if sticker_data["count"] > 1:
                e.add_field(name="Count", value=sticker_data["count"])
            e.add_field(
                name="Rarity", value=item_metadatum.rarity.get_name_for_regular_item()
            )
        e.set_footer(
            text=f"Owned by {target_user.display_name}",
            icon_url=target_user.display_avatar.url,
        )
        await interaction.response.send_message(embed=e)


async def item_name_autocomplete(
    bot: SpaceCasesBot, interaction: discord.Interaction, current: str
) -> list[discord.app_commands.Choice]:
    try:
        target_user = interaction.namespace["user"]
    except KeyError:
        target_user = interaction.user
    unformatted_current = remove_skin_name_formatting(current)
    choices: list[discord.app_commands.Choice] = []
    # skin choices
    skins_result = await bot.db.fetch_from_file(
        "inventory/get_user_skins.sql", target_user.id
    )
    for skin in skins_result:
        if len(choices) == 25:
            return choices
        unformatted_name: str = skin["name"]
        if not unformatted_name.startswith(unformatted_current):
            continue
        floats: list[float] = skin["floats"]
        formatted_name = bot.item_metadata[unformatted_name].formatted_name
        if len(floats) == 1:
            choice_name = formatted_name
        else:
            choice_name = f"{formatted_name} x{len(floats)})"
        choices.append(
            discord.app_commands.Choice(name=choice_name, value=unformatted_name)
        )
    # sticker choices
    stickers_result = await bot.db.fetch_from_file(
        "inventory/get_user_stickers.sql", target_user.id
    )
    for sticker in stickers_result:
        if len(choices) == 25:
            return choices
        unformatted_name = sticker["name"]
        if not unformatted_name.startswith(unformatted_current):
            continue
        count: int = sticker["count"]
        formatted_name = bot.item_metadata[unformatted_name].formatted_name
        if count == 1:
            choice_name = formatted_name
        else:
            choice_name = f"{formatted_name} x{count})"
        choices.append(
            discord.app_commands.Choice(name=choice_name, value=unformatted_name)
        )
    return choices

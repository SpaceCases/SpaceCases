import discord
from collections import Counter
from spacecases_common import remove_skin_name_formatting
from src.bot import SpaceCasesBot
from src.database import GET_INVENTORY


async def inventory_item_autocomplete(
    bot: SpaceCasesBot, user: discord.Member | discord.User, current: str
) -> list[discord.app_commands.Choice]:
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

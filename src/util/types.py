import discord
from enum import Enum
from dataclasses import dataclass
from spacecases_common import SkinMetadatum, StickerMetadatum


class ItemType(Enum):
    Skin = "skin"
    Sticker = "sticker"


@dataclass
class SkinOwnership:
    owner: discord.User | discord.Member
    metadatum: SkinMetadatum
    floats: list[float]


@dataclass
class StickerOwnership:
    owner: discord.User | discord.Member
    metadatum: StickerMetadatum
    count: int

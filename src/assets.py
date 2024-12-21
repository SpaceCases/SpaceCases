import os
import requests
from spacecases_common import (
    SkinMetadatum,
    StickerMetadatum,
    SkinContainerEntry,
    ItemContainerEntry,
    Rarity,
    SkinCase,
    SouvenirPackage,
    StickerCapsule,
)
from src.environment import environment
from src.logger import logger

T_LOGO = os.path.join(environment.asset_domain, "static", "t.webp")
CT_LOGO = os.path.join(environment.asset_domain, "static", "ct.webp")

SKIN_METADATA_PATH = os.path.join(environment.asset_domain, "generated", "skin_metadata.json")
STICKER_METADATA_PATH = os.path.join(environment.asset_domain, "generated", "sticker_metadata.json")
SKIN_CASES_METADATA_PATH = os.path.join(environment.asset_domain, "generated", "skin_cases.json")
STICKER_CAPSULE_METADATA_PATH = os.path.join(environment.asset_domain, "generated", "sticker_capsules.json")
SOUVENIR_PACKAGE_METADATA_PATH = os.path.join(environment.asset_domain, "generated", "souvenir_packages.json")


def get_skin_metadata() -> dict[str, SkinMetadatum]:
    logger.info("Refreshing skin metadata...")
    skin_metadata = {}
    raw_json = requests.get(SKIN_METADATA_PATH).json()
    for unformatted_name, datum in raw_json.items():
        skin_metadatum = SkinMetadatum(
            datum["formatted_name"],
            Rarity(datum["rarity"]),
            datum["price"],
            datum["image_url"],
            datum["description"],
            datum["min_float"],
            datum["max_float"],
        )
        skin_metadata[unformatted_name] = skin_metadatum
    logger.info("Skin metadata refreshed")
    return skin_metadata


def get_sticker_metadata() -> dict[str, StickerMetadatum]:
    logger.info("Refreshing sticker metadata...")
    sticker_metadata = {}
    raw_json = requests.get(STICKER_METADATA_PATH).json()
    for unformatted_name, datum in raw_json.items():
        sticker_metadatum = StickerMetadatum(
            datum["formatted_name"],
            Rarity(datum["rarity"]),
            datum["price"],
            datum["image_url"],
        )
        sticker_metadata[unformatted_name] = sticker_metadatum
    logger.info("Sticker metadata refreshed")
    return sticker_metadata


def get_skin_cases() -> dict[str, SkinCase]:
    logger.info("Refreshing skin cases")
    skin_cases = {}
    raw_json = requests.get(SKIN_CASES_METADATA_PATH).json()
    for unformatted_name, datum in raw_json.items():
        skin_cases[unformatted_name] = SkinCase(
            datum["formatted_name"],
            datum["price"],
            datum["image_url"],
            datum["requires_key"],
            {Rarity(int(key)): [SkinContainerEntry(**item) for item in val] for key, val in datum["contains"].items()},
            [SkinContainerEntry(**val) for val in datum["contains_rare"]],
        )
    logger.info("Skin cases refreshed")
    return skin_cases


def get_souvenir_packages() -> dict[str, SouvenirPackage]:
    logger.info("Refreshing souvenir packages...")
    souvenir_packages = {}
    raw_json = requests.get(SOUVENIR_PACKAGE_METADATA_PATH).json()
    for unformatted_name, datum in raw_json.items():
        souvenir_packages[unformatted_name] = SouvenirPackage(
            datum["formatted_name"],
            datum["price"],
            datum["image_url"],
            datum["requires_key"],
            {Rarity(int(key)): [SkinContainerEntry(**item) for item in val] for key, val in datum["contains"].items()},
            [SkinContainerEntry(**val) for val in datum["contains_rare"]],
        )
    logger.info("Souvenir packages refreshed")
    return souvenir_packages


def get_sticker_capsules() -> dict[str, StickerCapsule]:
    logger.info("Refreshing sticker capsules")
    sticker_capsules = {}
    raw_json = requests.get(STICKER_CAPSULE_METADATA_PATH).json()
    for unformatted_name, datum in raw_json.items():
        sticker_capsules[unformatted_name] = StickerCapsule(
            datum["formatted_name"],
            datum["price"],
            datum["image_url"],
            datum["requires_key"],
            {Rarity(int(key)): [ItemContainerEntry(**item) for item in val] for key, val in datum["contains"].items()},
            [ItemContainerEntry(**val) for val in datum["contains_rare"]],
        )
    logger.info("Sticker capsules refreshed")
    return sticker_capsules

import os
import requests
from pydantic import BaseModel
from spacecases_common import (
    SkinMetadatum,
    StickerMetadatum,
    SkinCase,
    SouvenirPackage,
    StickerCapsule,
)
from src.environment import environment
from src.logger import logger

T_LOGO = os.path.join(environment.asset_domain, "static", "t.webp")
CT_LOGO = os.path.join(environment.asset_domain, "static", "ct.webp")

SKIN_METADATA_PATH = os.path.join(
    environment.asset_domain, "generated", "skin_metadata.json"
)
STICKER_METADATA_PATH = os.path.join(
    environment.asset_domain, "generated", "sticker_metadata.json"
)
SKIN_CASES_METADATA_PATH = os.path.join(
    environment.asset_domain, "generated", "skin_cases.json"
)
STICKER_CAPSULE_METADATA_PATH = os.path.join(
    environment.asset_domain, "generated", "sticker_capsules.json"
)
SOUVENIR_PACKAGE_METADATA_PATH = os.path.join(
    environment.asset_domain, "generated", "souvenir_packages.json"
)


# Helper function to parse the raw JSON data into a dictionary of model instances
def parse_metadata[T: BaseModel](url: str, model: type[T]) -> dict[str, T]:
    logger.info(f"Refreshing metadata from {url}...")
    raw_json = requests.get(url).json()
    metadata = {
        key: model.model_validate(value) for key, value in raw_json.items()
    } 
    logger.info(f"Metadata refreshed from {url}")
    return metadata


def get_skin_metadata() -> dict[str, SkinMetadatum]:
    return parse_metadata(SKIN_METADATA_PATH, SkinMetadatum)


def get_sticker_metadata() -> dict[str, StickerMetadatum]:
    return parse_metadata(STICKER_METADATA_PATH, StickerMetadatum)


def get_skin_cases() -> dict[str, SkinCase]:
    return parse_metadata(SKIN_CASES_METADATA_PATH, SkinCase)


def get_souvenir_packages() -> dict[str, SouvenirPackage]:
    return parse_metadata(SOUVENIR_PACKAGE_METADATA_PATH, SouvenirPackage)


def get_sticker_capsules() -> dict[str, StickerCapsule]:
    return parse_metadata(STICKER_CAPSULE_METADATA_PATH, StickerCapsule)

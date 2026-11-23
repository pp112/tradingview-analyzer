from fastapi import APIRouter
from pydantic import TypeAdapter

from backend.config import get_logger
from backend.schemas.price_volume import PriceVolumeResponse
from backend.storage.paths import PRICE_VOLUME_FILE
from backend.storage.writer import read_json


logger = get_logger(__name__, "[API]")

router = APIRouter(tags=["price_volume"])

PRICE_VOLUME_ADAPTER = TypeAdapter(list[PriceVolumeResponse])


@router.get("/price_volume", response_model=list[PriceVolumeResponse])
def get_price_volume():
    """
    Возвращает последние изменения цен и объёмов.
    """
    logger.info("Запрос изменений цен и объёмов")
    data = read_json(PRICE_VOLUME_FILE, default=[])
    return PRICE_VOLUME_ADAPTER.validate_python(data)
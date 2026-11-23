from fastapi import APIRouter
from pydantic import TypeAdapter

from backend.config import get_logger
from backend.schemas.signals import SignalResponse
from backend.storage.paths import signals_file


logger = get_logger(__name__, "[API]")

router = APIRouter(tags=["signals"])

SIGNALS_ADAPTER = TypeAdapter(list[SignalResponse])


@router.get("/signals", response_model=list[SignalResponse])
def get_signals(tf: str):
    """
    Возвращает сигналы для указанного таймфрейма из JSON файла.
    """
    logger.info(f"Запрос сигналов: {tf}")
    json_data = signals_file(tf).read_text(encoding="utf-8")
    return SIGNALS_ADAPTER.validate_json(json_data)
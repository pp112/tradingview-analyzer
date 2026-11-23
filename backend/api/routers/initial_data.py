from fastapi import APIRouter

from backend.schemas.initial_data import InitialDataResponse
from backend.storage.paths import PRICE_VOLUME_FILE, SIGNALS_DIR
from backend.storage.writer import read_json


router = APIRouter(tags=["initial_data"])


@router.get("/initial_data", response_model=InitialDataResponse)
def get_initial_data():
    """
    Возвращает все актуальные данные для клиента при первом подключении:
    - сигналы по таймфреймам
    - изменения цен и объёмов
    """
    signals = {
        file_path.stem.removeprefix("signals_"): read_json(file_path)
        for file_path in SIGNALS_DIR.glob("signals_*.json")
    }
    price_changes = read_json(PRICE_VOLUME_FILE, default=[])

    return InitialDataResponse(
        signals=signals,
        price_changes=price_changes,
    )
from enum import Enum

class SortMode(str, Enum):
    CORR_IND_VOL = "corr_ind_vol"
    VOL_IND_CORR = "vol_ind_corr"
    IND_VOL_CORR = "ind_vol_corr"

    @property
    def filename(self) -> str:
        return {
            SortMode.CORR_IND_VOL: "by_corr",
            SortMode.VOL_IND_CORR: "by_volume",
            SortMode.IND_VOL_CORR: "by_indicator",
        }[self]
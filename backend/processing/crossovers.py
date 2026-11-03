from dataclasses import dataclass

import numpy as np
import pandas as pd

from backend.models.signal import Direction


@dataclass(frozen=True)
class Crossover:
    index: int
    direction: Direction


def find_crossovers(a: pd.Series, b: pd.Series) -> list[Crossover]:
    """Все пересечения a и b в хронологическом порядке."""
    sign = np.where((a - b).to_numpy() > 0, 1, -1)
    changed = sign[1:] != sign[:-1]
    return [
        Crossover(
            index=i + 1,
            direction=Direction.UP if sign[i + 1] > 0 else Direction.DOWN,
        )
        for i, c in enumerate(changed) if c
    ]
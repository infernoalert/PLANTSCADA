from __future__ import annotations

from typing import Dict

import processor
from services.paths import input_dir

_ADVALM = input_dir() / "ADVALM.csv"


def load_alarm_tag_comment_map() -> Dict[str, str]:
    """Load Alarm Tag -> Comment from input/ADVALM.csv."""
    return processor.load_alarm_tag_comment_map(_ADVALM)

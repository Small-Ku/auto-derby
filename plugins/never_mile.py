import auto_derby
import logging
from auto_derby import single_mode, mathtools
from typing import Tuple, Text, Dict

LOGGER = logging.getLogger(__name__)

from typing import Text, Dict, Tuple

class Race(auto_derby.config.single_mode_race_class):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)

        if self.distance < 2000:
            ret = 0
            
        return ret

class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_race_class = Race

auto_derby.plugin.register(__name__, Plugin())

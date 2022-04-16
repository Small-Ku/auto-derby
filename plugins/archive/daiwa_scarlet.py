import auto_derby
import logging
from auto_derby import single_mode, mathtools
from typing import Tuple

LOGGER = logging.getLogger(__name__)

class Race(single_mode.Race):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        return ret


class Context(single_mode.Context):
    def next_turn(self) -> None:
        super().next_turn()
        if auto_derby.config.user_pause_if_race_order_gt == -1:
            auto_derby.config.user_pause_if_race_order_gt = auto_derby.config.pause_if_race_order_gt
        auto_derby.config.pause_if_race_order_gt = {
            (2, 3, 0): 5,
            (2, 4, 0): 5,
            (2, 5, 1): 5,
            (2, 10, 1): 3,
            (2, 11, 0): 3,
            (3, 3, 1): 3,
            (3, 10, 1): 1,
            (3, 12, 1): 1,
            (5, 1, 2): 1
        }.get(self.date, auto_derby.config.user_pause_if_race_order_gt)


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.user_pause_if_race_order_gt = -1
        auto_derby.config.single_mode_race_class = Race
        auto_derby.config.single_mode_context_class = Context


auto_derby.plugin.register(__name__, Plugin())

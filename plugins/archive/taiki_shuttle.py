import auto_derby
import logging
from auto_derby import single_mode, mathtools
from typing import Tuple

LOGGER = logging.getLogger(__name__)

class Context(single_mode.Context):
    def next_turn(self) -> None:
        super().next_turn()
        if auto_derby.config.user_pause_if_race_order_gt == -1:
            auto_derby.config.user_pause_if_race_order_gt = auto_derby.config.pause_if_race_order_gt
        auto_derby.config.pause_if_race_order_gt = {
            (2, 1, 0): 5,
            (2, 5, 0): 5,
            (2, 6, 1): 5,
            (2, 11, 1): 3,
            (3, 6, 0): 1,
            (3, 9, 1): 1,
            (3, 11, 1): 1,
            (5, 1, 2): 1
        }.get(self.date, auto_derby.config.user_pause_if_race_order_gt)


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.user_pause_if_race_order_gt = -1
        auto_derby.config.single_mode_context_class = Context


auto_derby.plugin.register(__name__, Plugin())

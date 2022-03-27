import auto_derby
import logging
from auto_derby import single_mode, mathtools
from typing import Tuple

LOGGER = logging.getLogger(__name__)

class Race(single_mode.Race):
    def style_scores(
        self,
        ctx: single_mode.Context,
    ) -> Tuple[float, float, float, float]:
        if self.name == "URAファイナルズ決勝":
            return (0, 1, 0, 0)

        ret = super().style_scores(ctx)
        return ret

    def score(self, ctx: single_mode.Context) -> float:
        LOGGER.debug("%s",ctx.date)
        ret = super().score(ctx)
        if self.ground != Race.GROUND_DART:
            ret += {
                Race.GRADE_G1: 50,
                Race.GRADE_G2: 0,
                Race.GRADE_G3: -10,
                Race.GRADE_OP: -20,
                Race.GRADE_PRE_OP: -30,
                Race.GRADE_NOT_WINNING: 0,
                Race.GRADE_DEBUT: 0,
            }[self.grade]
        if self.distance < 1800:
            ret -= 60
        return ret


class Context(single_mode.Context):
    def next_turn(self) -> None:
        super().next_turn()
        if auto_derby.config.user_pause_if_race_order_gt == -1:
            auto_derby.config.user_pause_if_race_order_gt = auto_derby.config.pause_if_race_order_gt
        auto_derby.config.pause_if_race_order_gt = {
            (1, 10, 0): 5,
            (2, 4, 0): 5,
            (2, 5, 1): 5,
            (2, 10, 1): 3,
            (2, 12, 1): 3,
            (3, 4, 1): 3,
            (3, 11, 1): 2,
            (3, 12, 1): 1,
            (5, 1, 2): 1
        }.get(self.date, auto_derby.config.user_pause_if_race_order_gt)


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.user_pause_if_race_order_gt = -1
        auto_derby.config.single_mode_race_class = Race
        auto_derby.config.single_mode_context_class = Context


auto_derby.plugin.register(__name__, Plugin())

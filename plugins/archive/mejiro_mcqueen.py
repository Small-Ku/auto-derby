import auto_derby
import logging
from auto_derby import single_mode, mathtools
from typing import Tuple, Text, Dict

LOGGER = logging.getLogger(__name__)

from typing import Text, Dict, Tuple

_ACTION_NONE = 0
_ACTION_BAN = 1
_ACTION_LESS = 2
_ACTION_MORE = 3
_ACTION_PICK = 4

_DEFAULT_ACTION = _ACTION_NONE

_RULES: Dict[Tuple[int, Text], int] = {
    (23, "ホープフルステークス"): _ACTION_PICK,
    (44, "アルゼンチン共和国杯"): _ACTION_MORE,
    (46, "ステイヤーズステークス"): _ACTION_PICK,
    (47, "有馬記念"): _ACTION_PICK,
    (57, "目黒記念"): _ACTION_MORE,
    (69, "ジャパンカップ"): _ACTION_LESS,
    (70, "ステイヤーズステークス"): _ACTION_PICK,
    (71, "有馬記念"): _ACTION_PICK,
}

class Race(auto_derby.config.single_mode_race_class):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        
        action = _RULES.get(
            (ctx.turn_count(), self.name),
            _DEFAULT_ACTION,
        )
        if action == _ACTION_BAN:
            ret = 0
        elif action == _ACTION_LESS:
            ret -= 5
        elif action == _ACTION_MORE:
            ret += 5
        elif action == _ACTION_PICK:
            ret += 100
            
        if self.grade != Race.GRADE_G1 or self.distance > 2400:
            ret -= 15
            
        if action != _ACTION_PICK and self.distance <= 2400 and (ctx.sprint_race_count >= ctx.long_race_count or ctx.mile_race_count >= ctx.long_race_count or ctx.intermediate_race_count >= ctx.long_race_count):
            ret = 0
            
        return ret

class RaceCommand(single_mode.commands.RaceCommand):
    def execute(self, ctx: single_mode.Context) -> None:
        if self.race.distance <= 1400:
            ctx.sprint_race_count += 1
        elif self.race.distance <= 1800:
            ctx.mile_race_count += 1
        elif self.race.distance <= 2400:
            ctx.intermediate_race_count += 1
        else:
            ctx.long_race_count += 1
        super().execute(ctx)

class Context(single_mode.Context):
    def __init__(self) -> None:
        super().__init__()
        self.sprint_race_count = 0
        self.mile_race_count = 0
        self.intermediate_race_count = 0
        self.long_race_count = 0
        
    def next_turn(self) -> None:
        super().next_turn()
        if auto_derby.config.user_pause_if_race_order_gt == -1:
            auto_derby.config.user_pause_if_race_order_gt = auto_derby.config.pause_if_race_order_gt
        ret = {
            (1, 12, 2): 1,
            (2, 9, 1): 3,
            (2, 10, 1): 3,
            (3, 4, 1): 1,
            (3, 6, 1): 2,
            (3, 10, 1): 1,
            (5, 1, 2): 1
        }.get(self.date, 20)
        if ret > auto_derby.config.user_pause_if_race_order_gt:
            ret = auto_derby.config.user_pause_if_race_order_gt
        auto_derby.config.pause_if_race_order_gt = ret

class Training(single_mode.Training):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        success_rate = 1 - self.failure_rate
        sta = mathtools.integrate(
            ctx.wisdom,
            self.wisdom,
            ((0, 1.5), (800, 1.0), (900, 0.1)),
        )
        int_ = mathtools.integrate(
            ctx.stamina,
            self.stamina,
            ((0, 1.5), (800, 1.0), (900, 0.1)),
        )
        pow = mathtools.integrate(
            ctx.power,
            self.power,
            (
                (0, 0.0),
                (300, ctx.speed / 600),
                (600, ctx.speed / 900),
                (900, ctx.speed / 900 / 3),
            ),
        )
        ret += (sta + int_ - pow) * success_rate
        return ret

class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.user_pause_if_race_order_gt = -1
        auto_derby.config.single_mode_race_class = Race
        auto_derby.config.single_mode_context_class = Context
        auto_derby.config.single_mode_training_class = Training

auto_derby.plugin.register(__name__, Plugin())

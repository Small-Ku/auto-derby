import auto_derby
import logging
from auto_derby import single_mode, mathtools
from auto_derby.single_mode.commands.race import RaceResult
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
    (22, "朝日杯フューチュリティステークス"): _ACTION_PICK,
    (23, "ホープフルステークス"): _ACTION_MORE,
    (33, "東京優駿（日本ダービー）"): _ACTION_PICK,
    (34, "安田記念"): _ACTION_MORE,
    (35, "宝塚記念"): _ACTION_MORE,
    (43, "菊花賞"): _ACTION_MORE,
    (44, "アルゼンチン共和国杯"): _ACTION_MORE,
    (45, "ジャパンカップ"): _ACTION_PICK,
    (46, "ステイヤーズステークス"): _ACTION_MORE,
    (47, "有馬記念"): _ACTION_PICK,
    (55, "天皇賞（春）"): _ACTION_MORE,
    (59, "宝塚記念"): _ACTION_PICK,
    (66, "毎日王冠"): _ACTION_PICK,
    (68, "アルゼンチン共和国杯"): _ACTION_MORE,
    (70, "ステイヤーズステークス"): _ACTION_MORE,
    (71, "有馬記念"): _ACTION_PICK,
}

class Plugin(auto_derby.Plugin):
    def install(self) -> None:

        _next = auto_derby.config.on_single_mode_race_result
        
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
                    ret += 10000
                    
                if self.distance > 1400:
                    ret += 5
                if self.distance > 2400:
                    ret += 5
                #if (ctx.sprint_race_count > ctx.long_race_count or ctx.mile_race_count > ctx.long_race_count or ctx.intermediate_race_count > ctx.long_race_count):
                #    if action != _ACTION_PICK and ctx.fan_count >= 1000 and self.distance <= 2400:
                #        if self.distance >= 1800:
                #            ret -= 0.003 * (ctx.fan_count - 3000)
                #        else:
                #            ret = 0
                #    elif self.distance > 2400:
                #        ret += 0.00005 * (280000 - ctx.fan_count)
                
                if auto_derby.config.futatsuna == True and self.distance > 1400 and ctx.mood == ctx.MOOD_VERY_GOOD:
                    if (ctx.date[0] == 1 and ctx.date[1] > 8 and ctx.date[1] < 12) or (ctx.date[0] == 2 and ctx.date[1] > 2 and ctx.date[1] < 6) or (ctx.date[0] == 2 and ctx.date[1] > 9 and ctx.date[1] < 13) or (ctx.date[0] == 3 and ctx.date[1] > 4 and ctx.date[1] < 7) or (ctx.date[0] == 3 and ctx.date[1] > 9 and ctx.date[1] < 13):
                        continuous_race_bonus = mathtools.interpolate(
                            ctx.continuous_race_count(),
                            (
                                (1, 5),
                                (2, 8),
                                (3, 10),
                                (4, 25),
                                (5, 50),
                            ),
                        )
                        ret += continuous_race_bonus
                    
                if self.ground == self.GROUND_DART or self.distance <= 1400:
                    ret = 0
                return ret
                
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
                    (1, 12, 1): 5,
                    (2, 5, 2): 5,
                    (2, 11, 2): 5,
                    (2, 12, 2): 3,
                    (3, 6, 2): 3,
                    (3, 10, 1): 1,
                    (3, 12, 2): 1,
                    (5, 1, 2): 1
                }.get(self.date, 20)
                if auto_derby.config.futatsuna == 1:
                    ret = futatsuna_race = {
                        (1, 12, 1): 1,
                        (2, 12, 2): 1,
                        (3, 6, 2): 1,
                        (3, 12, 2): 1
                    }.get(self.date, ret)
                if ret > auto_derby.config.user_pause_if_race_order_gt:
                    ret = auto_derby.config.user_pause_if_race_order_gt
                auto_derby.config.pause_if_race_order_gt = ret
                
        class Training(single_mode.Training):
            def score(self, ctx: single_mode.Context) -> float:
                ret = super().score(ctx)
                if auto_derby.config.futatsuna == True and ctx.mood == ctx.MOOD_VERY_GOOD:
                    success_rate = 1 - self.failure_rate
                    ret *= 1 / success_rate
                return ret

        def _handle(ctx: Context, result: RaceResult):
            if result.race.distance <= 1400:
                ctx.sprint_race_count += 1
            elif result.race.distance <= 1800:
                ctx.mile_race_count += 1
            elif result.race.distance <= 2400:
                ctx.intermediate_race_count += 1
            else:
                ctx.long_race_count += 1
            futatsuna_race = {
                (1, 12, 1): 1,
                (2, 12, 2): 1,
                (3, 6, 2): 1,
                (3, 12, 2): 1
            }.get(ctx.date, 0)
            if futatsuna_race == 1 and (result.order != 1 or ctx.mood == ctx.MOOD_VERY_GOOD):
                auto_derby.config.futatsuna = False
            _next(ctx, result)
            
        class Option(single_mode.go_out.Option):
            def score(self, ctx: single_mode.Context) -> float:
                if auto_derby.config.futatsuna == True:
                    mood_limit = {
                        ctx.MOOD_VERY_GOOD: 0,
                        ctx.MOOD_GOOD: 0,
                        ctx.MOOD_NORMAL: 0.5,
                        ctx.MOOD_BAD: 1,
                        ctx.MOOD_VERY_BAD: 1,
                    }[ctx.mood]
                else:
                    mood_limit = 1
                ret = super().score(ctx)
                return mood_limit * ret

        auto_derby.config.futatsuna = True
        auto_derby.config.user_pause_if_race_order_gt = -1
        auto_derby.config.single_mode_race_class = Race
        auto_derby.config.single_mode_context_class = Context
        auto_derby.config.single_mode_training_class = Training
        auto_derby.config.single_mode_go_out_option_class = Option
        auto_derby.config.on_single_mode_race_result = _handle

auto_derby.plugin.register(__name__, Plugin())

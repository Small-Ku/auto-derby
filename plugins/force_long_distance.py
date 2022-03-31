import auto_derby
import logging
from auto_derby import single_mode, mathtools
from typing import Tuple, Text, Dict

LOGGER = logging.getLogger(__name__)

from typing import Text, Dict, Tuple

class Race(auto_derby.config.single_mode_race_class):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
            
        if self.distance <= 2400 and (ctx.sprint_race_count >= ctx.long_race_count or ctx.mile_race_count >= ctx.long_race_count or ctx.intermediate_race_count >= ctx.long_race_count):
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

class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_race_class = Race
        auto_derby.config.single_mode_context_class = Context

auto_derby.plugin.register(__name__, Plugin())

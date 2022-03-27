import auto_derby
import logging
from auto_derby import single_mode, mathtools
from typing import Tuple, Text, Dict
from auto_derby.single_mode.training.globals import g

class Training(single_mode.Training):
    def score(self, ctx: single_mode.Context) -> float:
        spd = mathtools.integrate(
            ctx.speed,
            self.speed,
            ((0, 2.0), (300, 1.0), (900, 0.9), (1000, 0.8), (1100, 0.5)),
        )
        if ctx.speed < ctx.turn_count() / 24 * 900:
            spd *= 1.5
    
        sta = mathtools.integrate(
            ctx.stamina,
            self.stamina,
            (
                (0, 2.0),
                (300, ctx.speed / 600 + 0.3 * ctx.date[0] if ctx.speed > 600 else 1.0),
                (
                    600,
                    ctx.speed / 900 * 0.9 + 0.1 * ctx.date[0] if ctx.speed > 900 else 0.9,
                ),
                (1050, ctx.speed / 1050 * 0.8),
            ),
        )
        if ctx.stamina < ctx.turn_count() / 24 * 900:
            sta *= 1.5
        pow = mathtools.integrate(
            ctx.power,
            self.power,
            ((0, 0.2), (200, 0.0))
        )
        per = mathtools.integrate(
            ctx.guts,
            self.guts,
            ((0, 0.2), (200, 0.0))
        )
        int_ = mathtools.integrate(
            ctx.wisdom,
            self.wisdom,
            ((0, 0.3), (200, 0.0))
        )
    
        vit = max(min(self.vitality, 1 - ctx.vitality), 0) * ctx.max_vitality * 0.6
        if ctx.date[1:] in ((6, 1),):
            vit *= 1.2
        if ctx.date[1:] in ((6, 2), (7, 1), (7, 2), (8, 1)):
            vit *= 1.5
    
        skill = self.skill * 0.5
    
        success_rate = 1 - self.failure_rate
    
        partner = 0
        for i in self.partners:
            partner += i.score(ctx)
    
        target_level = g.target_levels.get(self.type, self.level)
        target_level_score = 0
        if ctx.is_summer_camp:
            pass
        elif self.level < target_level:
            target_level_score += mathtools.interpolate(
                ctx.turn_count(),
                (
                    (0, 5),
                    (24, 3),
                    (48, 2),
                    (72, 0),
                ),
            )
        elif self.level > target_level:
            target_level_score -= (self.level - target_level) * 5
    
        fail_penality = 0
        if self.type != self.TYPE_WISDOM:
            fail_penality = mathtools.interpolate(
                ctx.turn_count(),
                (
                    (0, 30),
                    (72, 60),
                ),
            )
    
        has_hint = any(i for i in self.partners if i.has_hint)
        hint = 3 if has_hint else 0
        return (
            (spd + sta + pow + per + int_ + skill + partner + target_level_score + hint)
            * success_rate
            + vit
            - fail_penality * self.failure_rate
        )

class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_training_class = Training

auto_derby.plugin.register(__name__, Plugin())

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game

from krpg.actions import ActionManager, action
from krpg.executer import executer_command
from krpg.events import Events


class Clock:
    def __init__(self, game: Game):
        self.global_minutes = 60 * 31  # Day 1, 07:00
        self.game = game
        self.game.add_saver("clock", self.save, self.load)
        self.game.executer.add_extension(self)
        self.game.add_actions(self)

    def save(self):
        return self.global_minutes

    def load(self, data):
        self.global_minutes = data

    def wait(self, minutes):
        if not minutes:
            return
        day = self.days
        self.global_minutes += minutes
        self.game.events.dispatch(Events.TIMEPASS, minutes=minutes)
        if self.days > day:
            self.game.events.dispatch(Events.NEWDAY, day=self.days)

    def in_range(self, start, end):
        if start > end:
            return self.in_range(start, 24) or self.in_range(0, end)
        else:
            return start <= self.hours < end

    @property
    def days(self):
        return self.global_minutes // (24 * 60)

    @property
    def hours(self):
        return (self.global_minutes % (24 * 60)) // 60

    @property
    def minutes(self):
        return (self.global_minutes % (24 * 60)) % 60

    def __repr__(self):
        return f"<Clock d={self.days} h={self.hours} m={self.minutes} ({self.global_minutes})>"

    @executer_command("pass")
    def passtime(game: Game, minutes):
        game.clock.wait(int(minutes))

    @action("time", "Узнать, сколько время", "Информация")
    def time(game: Game):
        c = game.clock
        game.console.print(
            f"[green]Время: День [yellow]{c.days}[green], [yellow]{c.hours:0>2}:{c.minutes:0>2}[/]"
        )

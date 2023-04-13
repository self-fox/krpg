from __future__ import annotations

from krpg.actions import Action

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game

class Location:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        self.env = {}
        self.actions = []

    def save(self):
        return self.env

    def load(self, data):
        self.env = data

    def __repr__(self) -> str:
        return f"<Location name={self.id!r}>"


class World:
    def __init__(self, game: Game):
        self.locations: list[Location] = []
        self.roads = []
        self.current: Location | None = None
        self.game = game
        self.game.add_saver("world", self.save, self.load)
        
    def save(self):
        return {loc.name: loc.env for loc in self.locations}
    
    def load(self, data):
        for name, env in data.items():
            self.get(name).env = env

    def set(self, current_loc: str|Location):
        self.game.events.dispatch("move", before=self.current, after=current_loc)
        self.current = self.get(current_loc)
        
    def extract(self) -> list[Action]:
        return self.current.actions

    def add(self, location: Location):
        self.locations.append(location)

    def get(self, *ids: list[str | Location]) -> Location:
        res = []
        for id in ids:
            if isinstance(id, str):
                for loc in self.locations:
                    if loc.id == id:
                        res.append(loc)
                        break
            elif isinstance(id, Location):
                res.append(id)
        if len(res) != len(ids):
            raise Exception(f"{res} != {ids}")
        if len(res) == 1:
            return res[0]
        return res

    def get_road(self, loc: str | Location) -> list[Location]:
        loc = self.get(loc)
        res = []
        for a, b in self.roads:
            if a is loc:
                res.append(b)
            if b is loc:
                res.append(a)
        return res

    def road(self, loc1: str | Location, loc2: str | Location):
        loc1, loc2 = self.get(loc1, loc2)
        if loc2 in self.get_road(loc1):
            raise Exception(f"Road from {loc1} to {loc2} already exist")
        self.roads.append((loc1, loc2))

    def __repr__(self):
        return f"<World loc={len(self.locations)}>"
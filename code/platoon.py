"""
Class for Platoons, which are a grouping of Squads
"""

from repast4py import random, space, core
from repast4py.space import DiscretePoint

from squad import Squad


class Platoon(core.Agent):
    TYPE = 1

    def __init__(
        self,
        local_id: int,
        rank: int,
        platoon_num: int,
        pt: DiscretePoint,
        grid: space.SharedGrid,
    ):
        super().__init__(id=local_id, type=Platoon.TYPE, rank=rank)
        self.platoon_num = platoon_num
        self.x = pt.x
        self.y = pt.y
        self.direction = [pt.x, pt.y]
        # Set a random point as the outpost
        self.outpost = grid.get_random_local_pt(random.default_rng)
        # Initialize waypoint
        self.waypoint = DiscretePoint(0, 0)

    def get_platoon_num(self):
        return self.platoon_num

    def move(self):
        self.direction = random.default_rng.choice(Squad.OFFSETS, size=2)

        self.x += self.direction[0]
        self.y += self.direction[1]

    def get_xy(self):
        return self.direction

"""
Class for Platoons, which are a grouping of Squads
"""

from repast4py import random

from squad import Squad


class Platoon:
    def __init__(self, platoon_num: int, pt):
        self.platoon_num = platoon_num
        self.x = pt.x
        self.y = pt.y
        self.direction = [pt.x, pt.y]

    def get_platoon_num(self):
        return self.platoon_num

    def move(self):
        self.direction = random.default_rng.choice(Squad.OFFSETS, size=2)

        self.x += self.direction[0]
        self.y += self.direction[1]

    def get_xy(self):
        return self.direction

from typing import Dict, Tuple
from mpi4py import MPI
import numpy as np
from dataclasses import dataclass
from repast4py import core, random, space, schedule, logging, parameters
from repast4py import context as ctx
import repast4py
from repast4py.space import DiscretePoint as dpt


# Our own files
from squad import *


class Platoon:
    def __init__(self, platoon_num: int, pt):
        self.platoon_num = platoon_num
        self.x = pt.x
        self.y = pt.y
        self.direction = [pt.x, pt.y]

    def getPlatoonNum(self):
        return self.platoon_num

    def move(self):
        self.direction = random.default_rng.choice(Squad.OFFSETS, size=2)

        self.x += self.direction[0]
        self.y += self.direction[1]

    def get_xy(self):
        return self.direction

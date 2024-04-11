import sys
import math
import numpy as np
from typing import Dict, Tuple
from mpi4py import MPI
from dataclasses import dataclass

import numba
from numba import int32, int64
from numba.experimental import jitclass

from repast4py import core, space, schedule, logging, random
from repast4py import context as ctx
from repast4py.parameters import create_args_parser, init_params

from repast4py.space import ContinuousPoint as cpt
from repast4py.space import DiscretePoint as dpt
from repast4py.space import BorderType, OccupancyType

model = None


@numba.jit((int64[:], int64[:]), nopython=True)
def is_equal(a1, a2):
    return a1[0] == a2[0] and a1[1] == a2[1]


spec = [
    ('mo', int32[:]),
    ('no', int32[:]),
    ('xmin', int32),
    ('ymin', int32),
    ('ymax', int32),
    ('xmax', int32)
]


class Squad():

    """
    The squad class keeps track 
    """


class Platoon(core.Agent):
    """The Human Agent

    Args:
        a_id: a integer that uniquely identifies this Human on its starting rank
        rank: the starting MPI rank of this Human.
    """

    TYPE = 0

    def __init__(self, a_id: int, rank: int):
        super().__init__(id=a_id, type=Human.TYPE, rank=rank)
        self.infected = False

    def save(self) -> Tuple:
        """Saves the state of this Human as a Tuple.

        Used to move this Human from one MPI rank to another.

        Returns:
            The saved state of this Human.
        """
        return (self.uid, self.infected, self.infected_duration)

    def infect(self):
        self.infected = True

    # @profile
    def step(self):
        space_pt = model.space.get_location(self)
        alive = True
        if self.infected:
            self.infected_duration += 1
            alive = self.infected_duration < 10

        if alive:
            grid = model.grid
            pt = grid.get_location(self)
            nghs = model.ngh_finder.find(pt.x, pt.y)  # include_origin=True)
            # timer.stop_timer('ngh_finder')

            # timer.start_timer('zombie_finder')
            minimum = [[], sys.maxsize]
            at = dpt(0, 0, 0)
            for ngh in nghs:
                at._reset_from_array(ngh)
                count = 0
                for obj in grid.get_agents(at):
                    if obj.uid[1] == Zombie.TYPE:
                        count += 1
                if count < minimum[1]:
                    minimum[0] = [ngh]
                    minimum[1] = count
                elif count == minimum[1]:
                    minimum[0].append(ngh)

            min_ngh = minimum[0][random.default_rng.integers(
                0, len(minimum[0]))]
            # timer.stop_timer('zombie_finder')

            # if not np.all(min_ngh == pt.coordinates):
            # if min_ngh[0] != pt.coordinates[0] or min_ngh[1] != pt.coordinates[1]:
            # if not np.array_equal(min_ngh, pt.coordinates):
            if not is_equal(min_ngh, pt.coordinates):
                direction = (min_ngh - pt.coordinates) * 0.5
                model.move(self, space_pt.x +
                           direction[0], space_pt.y + direction[1])

        return (not alive, space_pt)


@dataclass
class Counts:
    """Dataclass used by repast4py aggregate logging to record
    the number of Humans and Zombies after each tick.
    """
    humans: int = 0
    zombies: int = 0

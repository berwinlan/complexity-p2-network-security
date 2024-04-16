from repast4py import core, random, space
import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass
import numba
from numba import int32, int64
from repast4py import core, random
from repast4py.space import DiscretePoint as dpt
from numpy.random import normal


# Our own files
from loggers import MeetLog


@numba.jit((int64[:], int64[:]), nopython=True)
def is_equal(a1, a2):
    return a1[0] == a2[0] and a1[1] == a2[1]


spec = [
    ("mo", int32[:]),
    ("no", int32[:]),
    ("xmin", int32),
    ("ymin", int32),
    ("ymax", int32),
    ("xmax", int32),
]


class Squad(core.Agent):
    OFFSETS = np.array([-1, 1])

    """
    OFFSETS: numpy array used in the agent behavior implementation to select the direction to move in. 
    See the discussion of the walk method below.

    local_id: that uniquely identifies an agent
    rank: on which the agent is created. 
    pt: current location (x, y)
    """

    def __init__(self, local_id: int, platoon_num: int, rank: int, pt: dpt, isInfected: bool=False):
        super().__init__(id=local_id, type=platoon_num, rank=rank)
        self.pt = pt
        self.meet_count = 0  # how many ppl they have met
        self.isInfected = isInfected  # whether they're infected or not

    def save(self) -> Tuple:
        """Saves the state of this Walker as a Tuple.
        Returns:
            The saved state of this Walker.
        """
        return (self.uid, self.meet_count, self.pt.coordinates, self.isInfected)

    def step(self, grid: space.SharedGrid, xy_dirs):
        """
        Walks the agent, then checks for infection.
        """
        center = 0
        scale = 1

        noise_x = int(normal(center, scale)) + xy_dirs[0]
        noise_y = int(normal(center, scale)) + xy_dirs[1]
        x= self.pt.x
        y = self.pt.y
        self._walk(grid, [noise_x, noise_y])
        # print(x, y, noise_x, noise_y, self.pt.x, self.pt.y)


        self._infect(grid)

    def count_colocations(self, grid, meet_log: MeetLog):
        """
        gets the number of other agents at the current location,
        and updates both the agents individual running total of other agents met
        """
        num_here = grid.get_num_agents(self.pt) - 1
        meet_log.total_meets += num_here
        if num_here < meet_log.min_meets:
            meet_log.min_meets = num_here
        if num_here > meet_log.max_meets:
            meet_log.max_meets = num_here
        self.meet_count += num_here

    def _walk(self, grid: space.SharedGrid, xy_dirs):
        """
        randomly chooses an offset from its current location (self.pt),
        adds those offsets to its current location to create a new location,
        and then moves to that new location on the grid. The moved-to-location
        becomes the agents new current location.
        """
        print(0, self.pt.x, self.pt.y,  xy_dirs[0], xy_dirs[1])
        self.pt = grid.move(
            self, dpt(self.pt.x + xy_dirs[0], self.pt.y + xy_dirs[1], 0)
        )
        print(1, self.pt.x, self.pt.y,  xy_dirs[0], xy_dirs[1])




    def _infect(self, grid: space.SharedGrid):
        """
        Infect agents.
        """
        # If this agent is in the InfectionRegion, it is infected
        coords = grid.get_location(self)
        if grid.infected_width[0] < coords.x < grid.infected_width[1]:
            if grid.infected_height[0] < coords.y < grid.infected_height[1]:
                self.isInfected = True

        # Get all the agents at this location
        agents_here = grid.get_agents(self.pt)
        # If any of them are infected, this agent is infected
        any_infected = any([agent.isInfected for agent in agents_here])
        if any_infected:
            self.isInfected = True


walker_cache = {}


def restore_walker(walker_data: Tuple):
    """
    Args:
        walker_data: tuple containing the data returned by Walker.save.
    """
    # uid is a 3 element tuple: 0 is id, 1 is type, 2 is rank
    uid = walker_data[0]
    pt_array = walker_data[2]
    pt = dpt(pt_array[0], pt_array[1], 0)

    if uid in walker_cache:
        walker = walker_cache[uid]
    else:
        walker = Walker(uid[0], uid[2], pt)
        walker_cache[uid] = walker

    walker.meet_count = walker_data[1]
    walker.pt = pt
    return walker

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

    def __init__(
        self,
        local_id: int,
        platoon_num: int,
        rank: int,
        pt: dpt,
        isInfected: bool = False,
    ):
        super().__init__(id=local_id, type=platoon_num, rank=rank)
        self.pt = pt
        self.meet_count = 0  # how many ppl they have met
        self.isInfected = isInfected  # whether they're infected or not
        self.waypoint = dpt(0, 0)  # Goal waypoint coordinates

    def save(self) -> Tuple:
        """Saves the state of this Walker as a Tuple.
        Returns:
            The saved state of this Walker.
        """
        return (self.uid, self.meet_count, self.pt.coordinates, self.isInfected)

    def step(self, grid: space.SharedGrid, xy_dirs) -> None:
        """
        Walks the agent, then checks for infection.
        """
        center = 0
        scale = 1

        noise_x = int(normal(center, scale)) + xy_dirs[0]
        noise_y = int(normal(center, scale)) + xy_dirs[1]

        match grid.spread:
            case "random_walk":
                self._random_walk(grid, [noise_x, noise_y])
            case "random_waypoint":
                self._random_waypoint(grid)
            case "hierarchical":
                self._hierarchical(grid)
            case _:
                raise Exception(f"{grid.spread} is an invalid type of spread.")

        # Infect agents
        self._infect(grid)

    def count_colocations(self, grid, meet_log: MeetLog) -> None:
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

    def _random_walk(self, grid: space.SharedGrid, xy_dirs) -> None:
        """
        randomly chooses an offset from its current location (self.pt),
        adds those offsets to its current location to create a new location,
        and then moves to that new location on the grid. The moved-to-location
        becomes the agents new current location.
        """
        self.pt = grid.move(
            self, dpt(self.pt.x + xy_dirs[0], self.pt.y + xy_dirs[1], 0)
        )

    def _random_waypoint(self, grid: space.SharedGrid) -> None:
        """
        Selects a random point and moves in that direction until it has reached it.
        """
        # If this squad has reached its waypoint or needs a new one, set new waypoint
        if (self in grid.get_agents(self.waypoint)) or (
            self.waypoint.x == 0 and self.waypoint.y == 0
        ):
            self.waypoint = grid.get_random_local_pt(random.default_rng)

        # Continue walking towards waypoint, using the shortest path
        x_movement = self.waypoint.x - self.pt.x
        y_movement = self.waypoint.y - self.pt.y
        normalizer = y_movement if y_movement > x_movement else x_movement
        # Normalize to move at most 1
        x_movement /= normalizer
        y_movement /= normalizer
        # Move
        self.pt = grid.move(
            self,
            dpt(int(self.pt.x + x_movement), int(self.pt.y + y_movement), 0),
        )

    def _hierarchical(self, grid: space.SharedGrid):
        pass

    def _infect(self, grid: space.SharedGrid) -> None:
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




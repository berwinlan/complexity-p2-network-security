"""
Squad class, which is the smallest unit of movement.
"""

import numpy as np
import numba
from numba import int32, int64
from repast4py import core, random, space
from repast4py.space import DiscretePoint as dpt

# Our own files
from loggers import MeetLog


@numba.jit((int64[:], int64[:]), nopython=True)
def is_equal(a1, a2):
    return a1[0] == a2[0] and a1[1] == a2[1]

def random_prob():
    return np.random.random()

def flip(p):
    return np.random.random() < p

spec = [
    ("mo", int32[:]),
    ("no", int32[:]),
    ("xmin", int32),
    ("ymin", int32),
    ("ymax", int32),
    ("xmax", int32),
]


class Squad(core.Agent):
    """
    OFFSETS: numpy array used in the agent behavior implementation
    to select the direction to move in.

    See the discussion of the walk method below.

    local_id: that uniquely identifies an agent
    rank: on which the agent is created.
    pt: current location (x, y)
    """

    TYPE = 0
    OFFSETS = np.array([-1, 1])

    def __init__(
        self,
        local_id: int,
        platoon_num: int,
        rank: int,
        pt: dpt,
        is_infected: bool = False
    ):
        super().__init__(id=local_id, type=Squad.TYPE, rank=rank)
        self.platoon_num = platoon_num
        self.pt = pt
        self.meet_count = 0  # how many ppl they have met
        self.is_infected = is_infected  # whether they're infected or not
        self.waypoint = dpt(0, 0)  # Goal waypoint coordinates
        self.prob_infected = random_prob()

    def save(self) -> tuple:
        """Saves the state of this Walker as a Tuple.
        Returns:
            The saved state of this Walker.
        """
        return (
            self.uid,
            self.meet_count,
            self.pt.coordinates,
            self.is_infected,
        )

    def step(self, grid: space.SharedGrid) -> None:
        """
        Walks the agent, then checks for infection.
        """
        match grid.spread:
            case "random_walk":
                self._random_walk(grid)
            case "random_waypoint":
                self._random_waypoint(grid)
            case "hierarchical":
                self._hierarchical(grid)
            case _:
                raise NameError(f"{grid.spread} is an invalid type of spread.")

        # Infect agents
        self._infect(grid)

    def count_colocations(self, grid, meet_log: MeetLog) -> None:
        """
        Gets the number of other agents at the current location, and
        updates both the agents individual running total of other agents met
        """
        num_here = grid.get_num_agents(self.pt) - 1
        meet_log.total_meets += num_here
        if num_here < meet_log.min_meets:
            meet_log.min_meets = num_here
        if num_here > meet_log.max_meets:
            meet_log.max_meets = num_here
        self.meet_count += num_here

    def _random_walk(self, grid: space.SharedGrid) -> None:
        """
        randomly chooses an offset from its current location (self.pt),
        adds those offsets to its current location to create a new location,
        and then moves to that new location on the grid. The moved-to-location
        becomes the agents new current location.
        """
        for _ in range(grid.rndwalk_size):
            # In a random walk, the agent moves up to 1 in any direction
            x_walk, y_walk = np.random.choice([-1, 1]), np.random.choice(
                [-1, 1]
            )

            self.pt = grid.move(
                self, dpt(self.pt.x + x_walk, self.pt.y + y_walk, 0)
            )

            # Checks for infection after each step.
            self._infect(grid)

    def _random_waypoint(self, grid: space.SharedGrid) -> None:
        """
        Selects a random point and moves in that direction until it arrives.
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
        while True:
            try:
                # Normalize to move at most 1
                x_movement /= normalizer
                y_movement /= normalizer
            # Handle case of zero division
            except ZeroDivisionError:
                pass
            else:
                break
        # Move
        self.pt = grid.move(
            self,
            dpt(int(self.pt.x + x_movement), int(self.pt.y + y_movement), 0),
        )

    def _hierarchical(self, grid: space.SharedGrid):
        pass
        # Begin at Company's outpost

        # HOLD between 10 and 60 minutes

        # With platoon, GOTO a random waypoint all together

        # Random walk for 30 min to 4 hours independently, then GOTO outpost

    def _infect(self, grid: space.SharedGrid) -> None:
        """
        Infect agents.
        """
        # If this agent is in the InfectionRegion, it is infected
        coords = grid.get_location(self)
        if grid.infected_width[0] < coords.x < grid.infected_width[1]:
            if grid.infected_height[0] < coords.y < grid.infected_height[1]:
                if flip(self.prob_infected):
                    self.is_infected = True

        # Get all the agents at this location
        agents_here = grid.get_agents(self.pt)
        # If any of them are infected, this agent is infected
        any_infected = any(agent.is_infected for agent in agents_here)
        if any_infected:
            if flip(self.prob_infected):
                self.is_infected = True

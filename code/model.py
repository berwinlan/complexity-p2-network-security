"""
Model class for the repast4py simulation.
"""

import random
from mpi4py import MPI
from numpy.random import normal

import repast4py
from repast4py import space, schedule, logging
from repast4py import context as ctx
from repast4py.space import DiscretePoint as dpt

from squad import Squad
from platoon import Platoon
from loggers import MeetLog

walker_cache = {}


def restore_agent(walker_data: tuple):
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
        walker = Squad(uid[0], uid[1], uid[2], pt, is_infected=False)
        walker_cache[uid] = walker

    walker.meet_count = walker_data[1]
    walker.pt = pt
    return walker


class Model:
    """
    The Model class encapsulates the simulation, and is
    responsible for initialization (scheduling events, creating agents,
    and the grid the agents inhabit), and the overall iterating
    behavior of the model.
    """

    def __init__(self, comm: MPI.Intracomm, params: dict):
        # SCHEDULING
        # Initialize scheduler
        self.runner = schedule.init_schedule_runner(comm)

        # Schedule events
        self.runner.schedule_repeating_event(at=1, interval=1, evt=self.step)
        self.runner.schedule_repeating_event(1.1, 10, self.log_agents)

        # Schedule tick when sim should stop
        self.runner.schedule_stop(params["stop.at"])

        # Clean up
        schedule.runner().schedule_end_event(self.at_end)

        # CONTEXT
        # Create context to hold agents and manage cross process synchronization
        self.context = ctx.SharedContext(comm)

        # PROJECTION
        # Define bounds
        box = space.BoundingBox(
            0, params["world.width"], 0, params["world.height"], 0, 0
        )
        # Allow multiple agents per location
        self.grid = space.SharedGrid(
            name="grid",
            bounds=box,
            borders=space.BorderType.Sticky,
            occupancy=space.OccupancyType.Multiple,
            buffer_size=2,
            comm=comm,
        )
        # Add projection to context
        self.context.add_projection(self.grid)

        # Add an InfectionRegion
        width_start = random.randint(
            0, params["world.width"] - params["InfectionRegion.width"]
        )
        height_start = random.randint(
            0, params["world.height"] - params["InfectionRegion.height"]
        )
        self.grid.infected_width = (
            width_start,
            width_start + params["InfectionRegion.width"],
        )
        self.grid.infected_height = (
            height_start,
            height_start + params["InfectionRegion.height"],
        )

        # Set spread type
        self.grid.spread = params["spread"]
        self.grid.rndwalk_size = params["step_size"]

        # Create agents
        rank = comm.Get_rank()  # Here, rank is a process rank
        # TODO: Logic for Hierarchial model
        rng = repast4py.random.default_rng

        self.platoons = []

        temp_count = 0
        for platoon_id in range(params["platoon.count"]):
            pt = self.grid.get_random_local_pt(rng)
            current_platoon = Platoon(
                platoon_id, platoon_id, platoon_id, pt, self.grid
            )
            self.platoons.append(current_platoon)

            for _ in range(params["squad.count"]):
                # Generate a random point for the Squad's origin
                new_x = current_platoon.get_xy()[0] + int(
                    normal(params["noise.center"], params["noise.scale"])
                )
                new_y = current_platoon.get_xy()[1] + int(
                    normal(params["noise.center"], params["noise.scale"])
                )

                points = space.DiscretePoint(new_x, new_y)

                # Create Squad, add to context, and move it to the point
                squad = Squad(
                    temp_count,
                    current_platoon,
                    platoon_id,
                    rank,
                    points,
                    is_infected=False,
                )
                self.context.add(squad)
                self.grid.move(squad, points)
                temp_count += 1

        # LOGGING
        self.agent_logger = logging.TabularLogger(
            comm,
            params["agent_log_file"],
            [
                "tick",
                "agent_id",
                "type",
                "agent_platoon",
                "meet_count",
                "x",
                "y",
                "infected",
            ],
        )
        self.meet_log = MeetLog()
        loggers = logging.create_loggers(
            self.meet_log, op=MPI.SUM, names={"total_meets": "total"}, rank=rank
        )
        loggers += logging.create_loggers(
            self.meet_log, op=MPI.MIN, names={"min_meets": "min"}, rank=rank
        )
        loggers += logging.create_loggers(
            self.meet_log, op=MPI.MAX, names={"max_meets": "max"}, rank=rank
        )
        self.data_set = logging.ReducingDataSet(
            loggers, MPI.COMM_WORLD, params["meet_log_file"]
        )

        # Log initial colocations at tick 0
        for walker in self.context.agents():
            walker.count_colocations(self.grid, self.meet_log)
        self.data_set.log(0)
        # Reset counts (it's per tick, not total)
        self._reset_log_counters()
        self.log_agents()

    def step(self):
        """
        Steps the model.
        """
        # Calls each agent's step function
        for platoon in self.platoons:
            platoon.move()

        for agent in self.context.agents():
            agent.step(self.grid, 0.1)

        # Synchronize across processes. (Not used because
        # we run on only one thread.)
        self.context.synchronize(restore_agent)

        # Get data for logging
        for agent in self.context.agents():
            agent.count_colocations(self.grid, self.meet_log)

        # Log data and reset counters
        tick = self.runner.schedule.tick
        self.data_set.log(tick)
        self._reset_log_counters()

    def log_agents(self):
        """
        Logs data about agents.
        """
        tick = self.runner.schedule.tick

        for agent in self.context.agents():
            self.agent_logger.log_row(
                tick,
                agent.id,
                agent.type,  # 0 for Squad, 1 for Platoon
                agent.platoon_num,
                agent.meet_count,
                agent.pt.x,
                agent.pt.y,
                agent.is_infected,
            )

        # Write to file
        self.agent_logger.write()

    def at_end(self):
        """
        Performs any cleanup work after the simulation finishes running.
        """
        self.data_set.close()
        self.agent_logger.close()

    def start(self):
        """
        Starts runner.
        """
        self.runner.execute()

    def _reset_log_counters(self):
        """
        Reset log counters. Often used after logging each tick to avoid
        counting totals, instead of counting per tick.
        """
        self.meet_log.max_meets = self.meet_log.min_meets = (
            self.meet_log.total_meets
        ) = 0

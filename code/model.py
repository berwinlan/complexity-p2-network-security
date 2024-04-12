from mpi4py import MPI

from repast4py import space, schedule, logging
from repast4py import context as ctx
import repast4py

from agent import Squad
from loggers import MeetLog


class Model:
    """
    The Model class encapsulates the simulation, and is
    responsible for initialization (scheduling events, creating agents,
    and the grid the agents inhabit), and the overall iterating
    behavior of the model.
    """

    def __init__(self, comm: MPI.Intracomm, params: dict):
        ## SCHEDULING
        # Initialize scheduler
        self.runner = schedule.init_schedule_runner(comm)

        # Schedule events
        self.runner.schedule_repeating_event(at=1, interval=1, evt=self.step)
        self.runner.schedule_repeating_event(1.1, 10, self.log_agents)

        # Schedule tick when sim should stop
        self.runner.schedule_stop(params["stop.at"])

        # Clean up
        schedule.runner().schedule_end_event(self.at_end)

        ## CONTEXT
        # Create context to hold agents and manage cross process synchronization
        self.context = ctx.SharedContext(comm)

        ## PROJECTION
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
        self.space = space.SharedCSpace(
            "space",
            bounds=box,
            borders=space.BorderType.Sticky,
            occupancy=space.OccupancyType.Multiple,
            buffer_size=2,
            comm=comm,
            tree_threshold=100,
        )
        self.context.add_projection(self.space)
        self.continuous_space = space.ContinuousSpace(
            "grid",
            box,
        )  # FINISH

        # initialize the logging
        self.agent_logger = logging.TabularLogger(
            comm, params["agent_log_file"], ["tick", "agent_id", "x", "y", "z"]
        )

        # Create agents
        rank = comm.Get_rank()  # Here, rank is a process rank
        # TODO: Logic for Hierarchial model
        rng = repast4py.random.default_rng
        for i in range(params["squad.count"]):
            # Generate a random point for the Squad's origin
            pt = self.grid.get_random_local_pt(rng)
            # Create Squad, add to context, and move it to the point
            squad = Squad(i, rank, pt)
            self.context.add(squad)
            self.grid.move(squad, pt)

        ## LOGGING
        self.agent_logger = logging.TabularLogger(
            comm,
            params["agent_log_file"],
            ["tick", "agent_id", "agent_uid_rank", "meet_count"],
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
        # Calls each agent's step function
        for agent in self.context.agents():
            agent.step(self.grid)

        # TODO: Synchronize sim across processes (5.2.5)
        # self.context.synchronize(restore_agent)

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
            coords = space.ContinuousSpace.get_location(agent)
            self.agent_logger.log_row(
                tick, agent.id, coords.x, coords.y, coords.z
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
        self.runner.execute()

    def _reset_log_counters(self):
        """
        Reset log counters. Often used after logging each tick to avoid counting totals,
        instead of counting per tick.
        """
        self.meet_log.max_meets = self.meet_log.min_meets = (
            self.meet_log.total_meets
        ) = 0

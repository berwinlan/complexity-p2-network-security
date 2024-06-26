from typing import Dict, Tuple
from mpi4py import MPI
import numpy as np
from dataclasses import dataclass

from repast4py import core, random, space, schedule, logging, parameters
from repast4py import context as ctx
import repast4py
from repast4py.space import DiscretePoint as dpt



class Model:
    """
    The Model class encapsulates the simulation, and is
    responsible for initialization (scheduling events, creating agents,
    and the grid the agents inhabit), and the overall iterating
    behavior of the model.

    Args:
        comm: the mpi communicator over which the model is distributed.
        params: the simulation input parameters
    """

    def __init__(self, comm: MPI.Intracomm, params: Dict):
        # create the schedule
        self.runner = schedule.init_schedule_runner(comm)
        self.runner.schedule_repeating_event(1, 1, self.step)
        self.runner.schedule_repeating_event(1.1, 10, self.log_agents)
        self.runner.schedule_stop(params['stop.at'])
        self.runner.schedule_end_event(self.at_end)

        # create the context to hold the agents and manage cross process
        # synchronization
        self.context = ctx.SharedContext(comm)

        # create a bounding box equal to the size of the entire global world grid
        box = space.BoundingBox(
            0, params['world.width'], 0, params['world.height'], 0, 0)
        # create a SharedGrid of 'box' size with sticky borders that allows multiple agents
        # in each grid location.
        self.grid = space.SharedGrid(name='grid', bounds=box, borders=space.BorderType.Sticky,
                                     occupancy=space.OccupancyType.Multiple, buffer_size=2, comm=comm)
        self.context.add_projection(self.grid)

        rank = comm.Get_rank()
        rng = repast4py.random.default_rng
        for i in range(params['walker.count']):


            #init Platoons
            ########
            ##########
            #########
            ##########
  
        # initialize the logging
        self.agent_logger = logging.TabularLogger(comm, params['agent_log_file'], [
                                                  'tick', 'agent_id', 'agent_uid_rank', 'meet_count'])

        self.meet_log = MeetLog()
        loggers = logging.create_loggers(self.meet_log, op=MPI.SUM, names={
                                         'total_meets': 'total'}, rank=rank)
        loggers += logging.create_loggers(self.meet_log,
                                          op=MPI.MIN, names={'min_meets': 'min'}, rank=rank)
        loggers += logging.create_loggers(self.meet_log,
                                          op=MPI.MAX, names={'max_meets': 'max'}, rank=rank)
        self.data_set = logging.ReducingDataSet(
            loggers, comm, params['meet_log_file'])

        # count the initial colocations at time 0 and log
        for  in self.context.agents():
            walker.counwalkert_colocations(self.grid, self.meet_log)
        self.data_set.log(0)
        self.meet_log.max_meets = self.meet_log.min_meets = self.meet_log.total_meets = 0
        self.log_agents()

    def step(self):
        for walker in self.context.agents():
            walker.walk(self.grid)

        self.context.synchronize(restore_walker)

        for walker in self.context.agents():
            walker.count_colocations(self.grid, self.meet_log)

        tick = self.runner.schedule.tick
        self.data_set.log(tick)
        # clear the meet log counts for the next tick
        self.meet_log.max_meets = self.meet_log.min_meets = self.meet_log.total_meets = 0

    def log_agents(self):
        tick = self.runner.schedule.tick
        for walker in self.context.agents():
            self.agent_logger.log_row(
                tick, walker.id, walker.uid_rank, walker.meet_count)

        self.agent_logger.write()

    def at_end(self):
        self.data_set.close()
        self.agent_logger.close()

    def start(self):
        self.runner.execute()


def run(params: Dict):
    model = Model(MPI.COMM_WORLD, params)
    model.start()


if __name__ == "__main__":
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(args.parameters_file, args.parameters)
    run(params)

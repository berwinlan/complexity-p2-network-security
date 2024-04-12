from mpi4py import MPI
import numpy as np
from dataclasses import dataclass

from repast4py import core, random, space, schedule, logging, parameters
from repast4py import context as ctx
import repast4py
from repast4py.space import DiscretePoint as dpt

from agent import Squad
from loggers import MeetLog

class Model:
    def __init__(self, comm: MPI.Intracomm, params: dict):
        ## SCHEDULING
        # Initialize scheduler
        self.runner = schedule.init_schedule_runner(comm)

        # Schedule events
        self.runner.schedule_repeating_event(at = 1, interval = 1, evt = self.step)
        self.runner.schedule_repeating_event(1.1, 10, self.log_agents)

        # Schedule tick when sim should stop
        self.runner.schedule_stop(params['stop.at'])

        # Clean up
        schedule.runner().schedule_end_event(self.at_end) 

        ## CONTEXT
        # Create context to hold agents and manage cross process synchronization
        self.context = ctx.SharedContext(comm)    

        ## PROJECTION
        # Define bounds
        box = space.BoundingBox(0, params['world.width'], 0, params['world.height'], 0, 0)
        # Allow multiple agents per location
        self.grid = space.SharedGrid(name='grid', bounds=box, borders=space.BorderType.Sticky,
                                occupancy=space.OccupancyType.Multiple,
                                buffer_size=2, comm=comm)
        # Add projection to context
        self.context.add_projection(self.grid)      
        self.space = space.SharedCSpace('space', bounds=box, borders=space.BorderType.Sticky,
                                        occupancy=space.OccupancyType.Multiple,
                                        buffer_size=2, comm=comm,
                                        tree_threshold=100)    
        self.context.add_projection(self.space)
        self.continuous_space = space.ContinuousSpace('grid',box, ) # FINISH

        # initialize the logging
        self.agent_logger = logging.TabularLogger(comm, params['agent_log_file'], ['tick', 'agent_id', 'x', 'y', 'z'])

        # Create agents
        rank = comm.Get_rank()  # Here, rank is a process rank
        # TODO: Logic for Hierarchial model
        rng = repast4py.random.default_rng
        for i in range(params['squad.count']):
            # Generate a random point for the Squad's origin
            pt = self.grid.get_random_local_pt(rng)    
            # Create Squad, add to context, and move it to the point
            squad = Squad(i, rank, pt)    
            self.context.add(squad)    
            self.grid.move(squad, pt)

        ## LOGGING
        self.agent_logger = logging.TabularLogger(comm, params['agent_log_file'],
                                          ['tick', 'agent_id', 'agent_uid_rank',
                                          'meet_count'])    
        self.meet_log = MeetLog()    
        loggers = logging.create_loggers(self.meet_log, op=MPI.SUM,
                                        names={'total_meets': 'total'}, rank=rank)    
        loggers += logging.create_loggers(self.meet_log, op=MPI.MIN,
                                        names={'min_meets': 'min'}, rank=rank)       
        loggers += logging.create_loggers(self.meet_log, op=MPI.MAX,
                                        names={'max_meets': 'max'}, rank=rank)       
        self.data_set = logging.ReducingDataSet(loggers, MPI.COMM_WORLD,
                                                params['meet_log_file'])    
    
    def step(self):
        pass

    def log_agents(self):
        tick = self.runner.schedule.tick
        for agent in self.context.agents():
            coords = space.ContinuousSpace.get_location(agent)
            self.agent_logger.log_row(tick, agent.id, coords.x, coords.y, coords.z)

        self.agent_logger.write()

    def at_end(self):
        """
        Performs any cleanup work after the simulation finishes running.
        """
        # self.data_set.close()
        self.agent_logger.close()

    def start(self):
        self.runner.execute()

# TODO: replace this run code

from typing import Dict, Tuple

def run(params: Dict):
    model = Model(MPI.COMM_WORLD, params)
    model.start()

if __name__ == "__main__":
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(args.parameters_file, args.parameters)
    run(params)

# Usage  mpirun -n 4 python model.py params.yaml
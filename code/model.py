from mpi4py import MPI
import numpy as np
from dataclasses import dataclass

from repast4py import core, random, space, schedule, logging, parameters
from repast4py import context as ctx
import repast4py
from repast4py.space import DiscretePoint as dpt

from agent import Squad

class Model:
    def __init__(self, comm: MPI.Intracomm, params: dict):
        ## SCHEDULING
        # Initialize scheduler
        self.runner = schedule.init_schedule_runner()

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

        # Create agents
        rank = comm.Get_rank()  # Here, rank is a process rank
        # TODO: Logic for Hierarchial model
        rng = repast4py.random.default_rng
        for i in range(params['walker.count']):
            # Generate a random point for the Squad's origin
            pt = self.grid.get_random_local_pt(rng)    
            # Create Squad, add to context, and move it to the point
            squad = Squad(i, rank, pt)    
            self.context.add(squad)    
            self.grid.move(squad, pt) 
    
    def step(self):
        pass

    def log_agents(self):
        pass

    def at_end(self):
        """
        Performs any cleanup work after the simulation finishes running.
        """
        # Close log file
        pass
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
    """
    pt: grid.get_random_local_pt(rng)
    """

    TYPE = 1

    def __init__(
        self,
        squad_num: int,
        comm: MPI.Intracomm,
        rank,
        pt,
        grid,
        infected=False,
    ) -> None:
        # create the context to hold the squads
        self.context = ctx.SharedContext(comm)
        for i in range(squad_num):
            squad = Squad(i, rank, pt)
            self.context.add(squad)
            grid.move(squad, pt)

        self.type = Platoon.TYPE

    def step(self, grid, meet_log):
        for squad in self.context.agents():
            squad.walk(grid)

        for squad in self.context.agents():
            squad.count_colocations(grid, meet_log)

        tick = self.runner.schedule.tick
        self.data_set.log(tick)
        # clear the meet log counts for the next tick
        meet_log.max_meets = meet_log.min_meets = meet_log.total_meets = 0

    def count_colocations(self):
        # TODO: abstract colocations
        pass
